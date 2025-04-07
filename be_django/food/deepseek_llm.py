import os
import requests
from langchain_core.language_models import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Optional, List, Dict, Any

class DeepSeekLLM(LLM):
    api_key: str = os.getenv("DEEPSEEK_API_KEY")
    api_url: str = "https://api.deepseek.com/v1/chat/completions"
    model: str = "deepseek-chat"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        response = requests.post(self.api_url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"DeepSeek API 호출 실패: {response.status_code} - {response.text}")
        result = response.json()
        print(f"Full DeepSeek response: {result}")
        return result["choices"][0]["message"]["content"].strip()

    @property
    def _llm_type(self) -> str:
        return "deepseek"