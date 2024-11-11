class TextChunker:
    def __init__(self, token_counter, config):
        self.token_counter = token_counter
        self.config = config
    
    def chunk_text(self, text):
        words = text.split()
        chunks = []
        current_chunk = []
        current_token_count = 0
        
        for word in words:
            word_tokens = self.token_counter.count_tokens(word)
            if current_token_count + word_tokens > self.config.target_token_count:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_token_count = word_tokens
            else:
                current_chunk.append(word)
                current_token_count += word_tokens
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks