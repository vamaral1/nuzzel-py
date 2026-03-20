"""
LLM API Client

This module provides a unified interface for LLM API operations with support
for multiple providers in a fallback chain: Gemini -> Groq -> OpenRouter.
"""

import json
import os
import time
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import requests  # type: ignore[import-untyped]
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google import genai
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam

# Configure logging
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM API error"""


class LLMClient(ABC):
    """Abstract base class for LLM client"""

    @abstractmethod
    def generate_text(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate text response from LLM"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this LLM client is available (has API key, etc.)"""


class GeminiClient(LLMClient):
    """Google Gemini API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def is_available(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception as e:
            logger.warning("Gemini client not available: %s", e)
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((Exception, LLMError))
    )
    def generate_text(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate text using Gemini"""
        if not self.is_available():
            raise LLMError("Gemini client not available")

        try:
            # Configure the model
            model = "gemini-2.5-flash-lite"

            # Prepare messages
            contents = []
            if system_message:
                contents.append({"role": "user", "parts": [{"text": f"System: {system_message}\n\n{prompt}"}]})
            else:
                contents.append({"role": "user", "parts": [{"text": prompt}]})

            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
                    max_output_tokens=2048,
                    temperature=0.7,
                    response_mime_type="text/plain",
                )
            )

            if response.text:
                return response.text.strip()
            else:
                raise LLMError("Empty response from Gemini")

        except Exception as e:
            raise LLMError("Gemini API error") from e


class GroqClient(LLMClient):
    """Groq API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Groq(api_key=api_key)

    def is_available(self) -> bool:
        try:
            # Quick validation by listing available models
            self.client.models.list()
            return True
        except Exception as e:
            logger.warning("Groq client not available: %s", e)
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((Exception, LLMError))
    )
    def generate_text(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate text using Groq"""
        if not self.is_available():
            raise LLMError("Groq client not available")

        try:
            model = "moonshotai/kimi-k2-instruct-0905"

            messages: List[ChatCompletionMessageParam] = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                timeout=30
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                raise LLMError("Empty response from Groq")

        except Exception as e:
            raise LLMError("Groq API error") from e


class OpenRouterClient(LLMClient):
    """OpenRouter API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"

    def is_available(self) -> bool:
        if not self.api_key:
            return False

        try:
            # Quick validation by listing available models
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                f"{self.base_url}/models/count",
                headers=headers,
                timeout=10
            )

            response.raise_for_status()
            return True
        except Exception:
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((Exception, LLMError))
    )
    def generate_text(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate text using OpenRouter"""
        if not self.is_available():
            raise LLMError("OpenRouter client not available")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            data = {
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            if result.get('choices', [{}])[0].get('message', {}).get('content'):
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.warning(
                    "OpenRouter empty choices; keys=%s",
                    list(result.keys()) if isinstance(result, dict) else type(result),
                )
                raise LLMError("Empty response from OpenRouter")

        except requests.HTTPError as e:
            resp = e.response
            if resp is not None:
                snippet = (resp.text or "")[:800]
                logger.warning(
                    "OpenRouter HTTP %s: %s",
                    resp.status_code,
                    snippet,
                )
            raise LLMError("OpenRouter API error") from e
        except requests.RequestException as e:
            raise LLMError("OpenRouter API error") from e
        except Exception as e:
            raise LLMError("OpenRouter processing error") from e


class FallbackLLMClient(LLMClient):
    """LLM client with fallback chain: Gemini -> Groq -> OpenRouter"""

    def __init__(self, gemini_key: Optional[str],
        groq_key: Optional[str],
        openrouter_key: Optional[str]
    ) -> None:
        """
        Initialize the FallbackLLMClient with the provided API keys.

        Args:
            gemini_key: Google Gemini API key
            groq_key: Groq API key
            openrouter_key: OpenRouter API key
        """
        self.clients: List[LLMClient] = []
        if gemini_key:
            self.clients.append(GeminiClient(gemini_key))
        if groq_key:
            self.clients.append(GroqClient(groq_key))
        if openrouter_key:
            self.clients.append(OpenRouterClient(openrouter_key))

    def is_available(self) -> bool:
        """Check if at least one client is available"""
        return any(client.is_available() for client in self.clients)

    def generate_text(self, prompt: str, system_message: Optional[str]) -> str:
        """Generate text using fallback chain"""
        if not self.is_available():
            raise LLMError("No LLM clients available")

        last_error = None

        for i, client in enumerate(self.clients):
            if not client.is_available():
                continue

            try:
                logger.info(
                    "Trying LLM client %d/%d: %s", i+1, len(self.clients), client.__class__.__name__
                )
                response = client.generate_text(prompt, system_message)

                if response and response.strip():
                    logger.info("Successfully used %s", client.__class__.__name__)
                    return response
                else:
                    raise LLMError("Empty response")

            except Exception as e:
                error_msg = f"{client.__class__.__name__} failed: {str(e)}"
                logger.warning(error_msg)
                last_error = e

                # Wait before trying next client
                if i < len(self.clients) - 1:
                    time.sleep(2)

        # All clients failed
        raise LLMError(f"All LLM clients failed. Last error: {str(last_error)}")


class MockLLMClient(LLMClient):
    """Mock LLM client for testing that loads responses from fixture files"""

    def __init__(self, fixtures_dir: str = "tests/fixtures/llm_api"):
        self.fixtures_dir = Path(__file__).parent.parent / fixtures_dir

    def _load_fixture(self, filename: str) -> str:
        """Load JSON fixture file and return as JSON string"""
        fixture_path = self.fixtures_dir / filename
        if not fixture_path.exists():
            raise FileNotFoundError(f"Mock fixture not found: {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data)

    def generate_text(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Return mock responses based on the type of prompt"""
        pl = prompt.lower()
        if "# themes merge" in pl:
            return self._load_fixture("themes_and_insights.json")
        if "# themes: per-chunk" in pl:
            return json.dumps(
                {
                    "notes": "Mock chunk notes",
                    "themes": [
                        {
                            "theme": "Mock chunk theme",
                            "description": "From chunked themes path",
                            "tweet_ids": ["1"],
                        }
                    ],
                }
            )
        if "# themes and insights" in pl:
            return self._load_fixture("themes_and_insights.json")
        elif "categorize" in pl or "interest categorization" in pl:
            return self._load_fixture("interest_categorization.json")
        elif "engagement prediction" in pl or "# engagement prediction" in pl:
            return self._load_fixture("engagement_prediction.json")
        else:
            # Default fallback response
            return self._load_fixture("default.json")

    def is_available(self) -> bool:
        return True


def create_llm_client() -> LLMClient:
    """
    Factory function to create LLM client with fallback chain or mock client.

    Returns:
        LLMClient instance
    """
    use_mock = os.getenv("USE_MOCK", "false").lower() == "true"

    if use_mock:
        logger.info("Using mock LLM client")
        return MockLLMClient()
    else:
        return FallbackLLMClient(
            os.getenv('GEMINI_API_KEY'), os.getenv('GROQ_API_KEY'), os.getenv('OPEN_ROUTER_API_KEY')
        )
