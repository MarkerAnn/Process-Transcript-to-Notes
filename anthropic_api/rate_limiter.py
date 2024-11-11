import time

class RateLimiter:
    def __init__(self, config):
        self.config = config
        self.requests_made = 0
        self.start_time = time.time()
        self.last_request_time = self.start_time
        
    def wait_if_needed(self):
        current_time = time.time()
        
        # Check minimum time between requests
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.config.request_delay:
            time.sleep(self.config.request_delay - time_since_last_request)
        
        # Check rate limits
        self.requests_made += 1
        if self.requests_made >= self.config.requests_per_minute:
            elapsed_time = current_time - self.start_time
            if elapsed_time < 60:
                wait_time = 60 - elapsed_time
                print(f"Rate limit approached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            self.start_time = time.time()
            self.requests_made = 0
        
        self.last_request_time = time.time()