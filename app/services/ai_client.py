
from openai import AsyncOpenAI
from openai import OpenAI
from app.core.config    import settings
from app.models.prompts import SYSTEM_PROMPT
from app.models.prompts import SUMMARIZE_PROMPT
#
from typing import Any
from typing import Dict
from typing import List 
from typing import Optional

import asyncio
import httpx
import requests

class LocalAIClient:
    def __init__(self, base_url: str, model_name: str, *, api_key: str = "dummy-key"):
        
        self.base_url   = base_url
        self.model_name = model_name
        self.api_key    = api_key 

        # Init by default
        self.client     = None 
        self.is_client  = self.create_client()

    # Initial validation and init connection
    def create_client(self):
        
        if self.base_url.startswith("http://") or self.base_url.startswith("https://"):
            try:
                self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
                return True
            
            except Exception as e:
                return False
        
        return False
    
    async def is_alive(self):
        try:
            _url = self.base_url.replace("/v1", "") + "/healthz"
            async with httpx.AsyncClient() as client:
                resp = await client.get(_url, timeout=5.0)
            return resp.status_code == 200

        except Exception:
            return False
        
    async def model_available(self):

        try:
            models = await self.client.models.list()
            available = [m.id for m in models.data]
            return self.model_name in available
       
        except Exception:
            return False
    
    async def status(self) -> Dict[str, Any]:
        model_available, server_alive = await asyncio.gather(
            self.model_available(),
            self.is_alive(),
        )
        return {
            "base_url": self.base_url,
            "model": self.model_name,
            "model_available": model_available,
            "server_alive": server_alive,
        }
    # End initial connection functions

    # simple chat request
    async def chat(self, messages: List[Dict[str, str]]):

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=12000,
            )
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"[LocalAIClient] Request failed: {e}")
        
    async def default_ask(self, user_query: str, resume_list: List[Dict], *, system_prompt: str = SYSTEM_PROMPT):
        message: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"**User Query: {user_query}**"
            }
        ]
        message.extend(self.add_resume_to_message(resume_list))
        result = await self.chat(messages=message)
        return result
    
    async def sumarize_ask(self, resume_list: List[Dict], *, system_prompt: str = SUMMARIZE_PROMPT):
        message: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt
            },
        ]
        message.extend(self.add_resume_to_message(resume_list, summarize=True))
        result = await self.chat(messages=message)
        return result
        
        
    # Utilitaries
    def add_resume_to_message(self, resume_list, summarize: bool = False):
        message: List[Dict[str, str]] = []
        
        if not summarize:
            message.append({
                "role": "user",
                "content": f"Use the following resumes to answer the user's query. Total resumes: {len(resume_list)}"
            })
        else:
            message.append({
                "role": "user",
                "content": f"Summarize the following resumes. Total resumes: {len(resume_list)}"
            })
        
        for resume in resume_list:
            text    = resume.get("cleaned_text", "")
            idx_doc = resume.get("idx_document")

            message.append({
                "role": "user",
                "content": f"Resume #{idx_doc}: \n {text}"
            })
        
        return message

    async def close(self):
        if self.client is not None:
            try:
                await self.client.close()
                print("LocalAIClient - Connection closed successfully.")
            except Exception as e:
                print("LocalAIClient Connection closed with warnings: {e}")

    
localAi_client = LocalAIClient(base_url=settings.LOCALAI_BASE_URL, model_name=settings.LOCALAI_MODEL_NAME, api_key=settings.LOCALAI_SECRET_KEY.get_secret_value())