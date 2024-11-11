# Document Processing System with GPT and Claude Integration

## Overview

This project implements a sophisticated document processing system that
leverages both OpenAI's GPT and Anthropic's Claude APIs to analyze, expand, and
enhance text documents. The system is designed to process large documents by
breaking them down into manageable sections, expanding each section with
additional details and context, and then recombining them into a cohesive final
document.

## Features

- Dual API support (OpenAI GPT-4 and Claude 3.5)
- Intelligent text chunking and processing
- Token-aware content management
- Rate limiting and API quota management
- Automatic document sectioning and expansion
- Support for large document processing
- Error handling and retry mechanisms

## Project Structure

```
.
├── anthropic_api/
│   ├── api_client.py       # Claude API integration
│   ├── config.py           # Configuration settings
│   ├── document_processor.py # Document processing logic
│   ├── main.py            # Entry point for Claude processing
│   ├── rate_limiter.py    # API rate limiting
│   ├── text_processor.py  # Text chunking and processing
│   └── tokenizer.py       # Token counting utilities
├── openAI_api/
│   ├── api_client.py      # GPT API integration
│   ├── application.py     # Application orchestration
│   ├── config.py         # Configuration settings
│   ├── document_processor.py # Document processing logic
│   ├── file_manager.py   # File I/O operations
│   ├── main.py          # Entry point for GPT processing
│   └── prompt_manager.py # Prompt template management
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for GPT integration)
- Anthropic API key (for Claude integration)
- Required Python packages (see Installation section)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd document-processor
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install openai anthropic transformers python-dotenv
```

4. Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

### Using the GPT Processor

1. Run the GPT processor:

```bash
python openAI_api/main.py
```

2. When prompted, enter the full path to your document.

3. The processed document will be saved with a "\_processed" suffix in the same
   directory.

### Using the Claude Processor

1. Run the Claude processor:

```bash
python anthropic_api/main.py
```

2. Follow the same steps as with the GPT processor.

## Configuration

### GPT Configuration (openAI_api/config.py)

- `model`: Currently set to "gpt-4-0125-preview"
- `response_format`: Set to JSON for structured responses

### Claude Configuration (anthropic_api/config.py)

- `model`: Currently set to "claude-3-5-sonnet-20240620"
- `max_tokens`: 8192
- `requests_per_minute`: 50
- `target_token_count`: 25000
- `request_delay`: 1.2 seconds between requests

## Key Components

### Document Processor

Both API implementations include a DocumentProcessor class that:

1. Splits input text into logical sections
2. Expands each section with additional details
3. Recombines expanded sections into a final document

### Rate Limiting

The Claude implementation includes sophisticated rate limiting that:

- Enforces minimum delays between requests
- Tracks request counts per minute
- Implements exponential backoff for retries

### Text Processing

Includes:

- Token-aware text chunking
- Section management
- Content expansion logic

## Error Handling

The system includes comprehensive error handling for:

- API rate limits
- Network issues
- File I/O errors
- Token limit exceeded scenarios

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT](LICENS)

## Acknowledgments

- OpenAI for the GPT API
- Anthropic for the Claude API
- The transformers library for token counting

## Contact

software.developer.angelica@gmail.com
