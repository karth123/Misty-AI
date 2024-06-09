from openai import OpenAI

import google.generativeai as genai
from config import read_openai_config, read_google_gemini_config

openai_config = read_openai_config()
google_config = read_google_gemini_config()

class TokenException(Exception):
        """Exception for handling invalid or expired tokens."""
pass

class OpenAIClientSingleton:
    _instance = None

    @classmethod
    def get_gpt4o_openai_client(cls):
        if cls._instance is None:
            api_key = openai_config.get('gpt4o_openai_api_key')
            api_organization_id = openai_config.get('org_id')
            cls._instance = OpenAI(api_key = api_key, organization= api_organization_id)
        return cls._instance

class GoogleGeminiClientSingleton:
     _instance = None

     @classmethod
     def initialise_gemini_client(cls):
          if cls._instance is None:
            api_key = google_config.get('google_api_key')
            genai.configure(api_key=api_key)
            cls._instance = genai.GenerativeModel('gemini-1.5-flash')
          return cls._instance
