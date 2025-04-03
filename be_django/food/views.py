from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .models import FoodRecommendation
from .serializers import FoodRecommendationSerializer
from .deepseek_llm import DeepSeekLLM
from django.conf import settings

@api_view(['POST'])
def recommend_food(request):
    mood = request.data.get("mood")
    weather = request.data.get("weather")

    if not mood or not weather:
        return Response({"error": "mood와 weather가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 데이터베이스에서 모든 음식 데이터 가져오기
        all_foods = FoodRecommendation.objects.all()
        food_list = [f"{food.name} ({food.details})" for food in all_foods]

        if not food_list:
            return Response({"error": "데이터베이스에 음식이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # LangChain 설정 (DeepSeek LLM 사용)
        llm = DeepSeekLLM()
        prompt_template = PromptTemplate(
            input_variables=["mood", "weather", "food_list"],
            template="Given the mood '{mood}' and weather '{weather}', recommend up to 3 foods from the following list: {food_list}. Provide only the food names."
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # LangChain으로 추천 요청
        food_list_str = ", ".join(food_list)
        response = chain.run(mood=mood, weather=weather, food_list=food_list_str)

        # 추천된 음식 파싱 (줄바꿈으로 구분)
        recommended_foods = [f.strip() for f in response.split('\n') if f.strip()]
        recommended_foods = recommended_foods[:3]  # 최대 3개

        # 데이터베이스에서 추천된 음식 조회
        recommendations = []
        for food_name in recommended_foods:
            food_name_cleaned = food_name.split(' (')[0].strip()
            recs = FoodRecommendation.objects.filter(name=food_name_cleaned)[:1]
            if recs.exists():
                recommendations.extend(recs)

        serializer = FoodRecommendationSerializer(recommendations, many=True)

        return Response({"food": recommended_foods[0] if recommended_foods else "기본 음식", "recommendations": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)