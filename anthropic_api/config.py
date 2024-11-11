import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-3-5-sonnet-20240620"
        self.max_tokens = 8192
        self.max_retries = 5
        self.initial_delay = 1
        self.request_delay = 1.2  # Minimum time between requests
        self.requests_per_minute = 50
        self.target_token_count = 25000