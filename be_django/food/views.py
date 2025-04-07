from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .models import FoodRestaurant,Food
from .serializers import FoodRestaurantSerializer,FoodSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
from dotenv import load_dotenv
from .weather_api import WeatherAPI
import json
from django.http import JsonResponse

load_dotenv()
@api_view(['POST'])
def recommend_food(request):
    mood = request.data.get("mood")
    weather = request.data.get("weather")

    if not mood or not weather:
        return Response({"error": "mood와 weather가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 모든 음식 DB에서 조회
        foods = Food.objects.all()
        food_list = [f"{food.name}" for food in foods]

        if not food_list:
            return Response({"error": "음식 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # LangChain + DeepSeek LLM 설정
        llm = ChatOpenAI(
            model_name="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com/beta"
        )

        prompt_template = PromptTemplate(
            input_variables=["mood", "weather", "food_list"],
            template="""
            기분이 '{mood}'이고 날씨가 '{weather}'일 때 다음 음식 목록 중 가장 잘 어울리는 음식 3가지를 추천해줘.
            음식 목록: {food_list}
            추천 음식 이름만 줄바꿈으로 구분해서 출력해줘.
            """
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)

        food_list_str = ", ".join(food_list)
        response = chain.run(mood=mood, weather=weather, food_list=food_list_str)

        # 추천 음식 파싱
        recommended_foods = [name.strip().split(' (')[0] for name in response.split('\n') if name.strip()]
        recommended_foods = recommended_foods[:3]  

        # DB에서 해당 음식 이름 필터링
        recommendations = []
        for name in recommended_foods:
            restaurant = FoodRestaurant.objects.filter(food__name=name).first()
            if restaurant:
                recommendations.append(restaurant)

        serializer = FoodRestaurantSerializer(recommendations, many=True)
        return Response({
            "food": recommended_foods[0] if recommended_foods else "기본 음식",
            "recommendations": serializer.data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def get_weather(request):
    if request.method == "POST":
        # JSON 데이터 처리
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
                lat = data.get("latitude")
                lon = data.get("longitude")
            else:
                lat = request.POST.get("latitude")
                lon = request.POST.get("longitude")
            
            if not lat or not lon:
                return JsonResponse({"error": "latitude와 longitude가 필요합니다."}, status=400)
            
            weather_api = WeatherAPI()
            weather = weather_api.get_weather(float(lat), float(lon))
            return JsonResponse({"weather": weather}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)