from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import requests
import os
import httpx
app = FastAPI()


HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')  
class MoodInput(BaseModel):
    text: str
    weather: str

class WeatherInput(BaseModel):
    latitude: float
    longitude: float

def build_prompt(text):
    return f"""
    다음 문장에서 감정 키워드 하나를 선택해줘: "{text}"
    감정 목록: [happy, excited, energetic, calm, sad, angry, tired, lethargic, frustrated, bored, nervous, confused]
    위 목록 중 가장 알맞은 감정 키워드 하나만 골라서 출력해줘.
    """
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def query_flant5(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 10, "do_sample": False}
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    generated = response.json()[0]["generated_text"].strip()
    return generated

MOOD = {
    "happy": "행복해요", "excited": "설레요", "energetic": "신나요", "calm": "평온해요",
    "sad": "슬퍼요", "angry": "화나요", "tired": "피곤해요", "lethargic": "무기력해요",
    "frustrated": "답답해요", "bored": "지루해요", "nervous": "긴장돼요", "confused": "당황스러워요"
}

def get_translated_emotion_llm(text):
    prompt = build_prompt(text)
    predicted = query_flant5(prompt).lower()
    
    for mood_key in MOOD:
        if mood_key in predicted:
            return {
                "emotion_key": mood_key,
                "translated": MOOD[mood_key]
            }
    return {
        "emotion_key": "unknown",
        "translated": "감정을 분류할 수 없어요."
    }
@app.post("/analyze-llm")
async def analyze_llm_emotion(input: MoodInput):
    result = get_translated_emotion_llm(input.text)
    mood=result["translated"]
    weather=input.weather

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/recommend_food/",  
            json={"mood": mood, "weather": weather}
        )
    
    food_data = response.json()  

    return {
        "mood": mood,
        "weather": weather,
        "recommendations": food_data
    }

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(latitude: float, longitude: float):
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric",
        "lang": "kr"
    }
    response = requests.get(WEATHER_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["description"]
        }
    return {"error": "날씨 정보를 가져올 수 없습니다."}

@app.post("/get_weather/")
async def get_weather_info(input_data: WeatherInput):
    weather= get_weather(input_data.latitude, input_data.longitude)
    return weather


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)