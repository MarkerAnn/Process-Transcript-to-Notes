import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4-0125-preview"
        self.response_format = {"type": "json_object"}