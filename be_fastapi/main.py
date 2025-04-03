from fastapi import FastAPI
import requests
from pydantic import BaseModel
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = FastAPI()
OPENWEATHERMAP_API_KEY = "your_openweathermap_api_key"

# T5 모델 초기화
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# 감정 매핑 테이블
MOOD_MAPPING = {
    "happy": "행복해요", "excited": "설레요", "energetic": "신나요", "calm": "평온해요",
    "sad": "슬퍼요", "angry": "화나요", "tired": "피곤해요", "lethargic": "무기력해요",
    "frustrated": "답답해요", "bored": "지루해요", "nervous": "긴장돼요", "confused": "당황스러워요"
}

class LocationInput(BaseModel):
    latitude: float
    longitude: float

class TextInput(BaseModel):
    text: str

@app.post("/get-weather")
async def get_weather(location: LocationInput):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return {"weather": response.json()["weather"][0]["main"]}
    return {"weather": "Clear", "warning": "날씨 조회 실패"}

@app.post("/analyze-mood")
async def analyze_mood(text_input: TextInput):
    input_text = f"convert to emotion: {text_input.text}"
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**inputs)
    emotion = tokenizer.decode(outputs[0], skip_special_tokens=True).lower()

    # T5 결과 매핑
    mapped_emotion = MOOD_MAPPING.get(emotion, "행복해요")  # 기본값: 행복해요
    return {"emotion": mapped_emotion}