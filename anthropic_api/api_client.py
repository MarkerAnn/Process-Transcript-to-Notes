from anthropic import Anthropic, RateLimitError
import time

class ClaudeClient:
    def __init__(self, config, rate_limiter):
        self.client = Anthropic(api_key=config.api_key)
        self.config = config
        self.rate_limiter = rate_limiter
    
    def create_message(self, prompt, max_retries=None):
        if max_retries is None:
            max_retries = self.config.max_retries
            
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.content[0].text if response.content else ""
                
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    delay = self.config.initial_delay * (2 ** attempt)
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise
            except Exception as e:
                print(f"Error in API call: {str(e)}")
                if attempt == max_retries - 1:
                    raise