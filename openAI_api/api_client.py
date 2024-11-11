from openai import OpenAI
import json

class GPTClient:
    def __init__(self, config):
        self.client = OpenAI(api_key=config.api_key)
        self.config = config
    
    def create_completion(self, prompt):
        """
        Send a prompt to the GPT API and return the parsed JSON response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=self.config.response_format
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in API call: {str(e)}")
            raise