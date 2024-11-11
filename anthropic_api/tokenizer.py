from transformers import GPT2Tokenizer

class TokenCounter:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    
    def count_tokens(self, text):
        return len(self.tokenizer.encode(text))