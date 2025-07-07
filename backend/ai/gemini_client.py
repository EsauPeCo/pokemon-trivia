"""
Gemini client configuration and initialization
"""

import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


class GeminiClient:
    """
    Wrapper class for Google Gemini AI client using LangChain
    """

    def __init__(self, model: Optional[str] = None, temperature: float = 0.7):
        """
        Initialize Gemini client

        Args:
            model: Gemini model name (defaults to env GEMINI_MODEL)
            temperature: Model temperature for randomness (0.0-1.0)
        """
        load_dotenv()

        self.model = os.getenv("GEMINI_MODEL")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.temperature = temperature

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LangChain Gemini client"""
        try:
            self._client = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=self.temperature,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {str(e)}")

    @property
    def client(self) -> ChatGoogleGenerativeAI:
        """Get the underlying LangChain client"""
        if self._client is None:
            self._initialize_client()
        return self._client

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using Gemini

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Generated response text
        """
        try:
            response = self.client.invoke(prompt)
            return response.content
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    def set_temperature(self, temperature: float):
        """Update model temperature and reinitialize client"""
        self.temperature = temperature
        self._initialize_client()
