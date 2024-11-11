from config import Config
from tokenizer import TokenCounter
from rate_limiter import RateLimiter
from text_processor import TextChunker
from api_client import ClaudeClient
from document_processor import DocumentProcessor

def main():
    print("Welcome to the Claude Document Processor!")
    
    config = Config()
    token_counter = TokenCounter()
    rate_limiter = RateLimiter(config)
    text_chunker = TextChunker(token_counter, config)
    claude_client = ClaudeClient(config, rate_limiter)
    processor = DocumentProcessor(config, token_counter, text_chunker, claude_client)
    
    file_path = input("Please enter the full path to the document you want to process: ").strip()
    
    # Remove any surrounding quotes if present
    if (file_path.startswith('"') and file_path.endswith('"')) or \
       (file_path.startswith("'") and file_path.endswith("'")):
        file_path = file_path[1:-1]
    
    print(f"Processing file: {file_path}")
    result = processor.process_document(file_path)
    
    if result:
        print("Processing successful. Please check the output file for the processed document.")
    else:
        print("Processing failed. Please check the error messages above for more details.")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()