import os
import requests
from langchain_core.language_models import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Optional, List, Dict, Any

class DeepSeekLLM(LLM):
    api_key: str = os.getenv("DEEPSEEK_API_KEY")
    api_url: str = "https://api.deepseek.com/v1/completions"
    model: str = "deepseek-v1"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.7
        }
        response = requests.post(self.api_url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"DeepSeek API 호출 실패: {response.text}")

        return response.json()["choices"][0]["text"].strip()

    @property
    def _llm_type(self) -> str:
        return "deepseek"