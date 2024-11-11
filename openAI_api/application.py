class Application:
    def __init__(self):
        self.config = None
        self.gpt_client = None
        self.prompt_manager = None
        self.file_manager = None
        self.processor = None
    
    def initialize(self):
        """
        Initialize all components
        """
        from config import Config
        from api_client import GPTClient
        from prompt_manager import PromptManager
        from file_manager import FileManager
        from document_processor import DocumentProcessor
        
        self.config = Config()
        self.gpt_client = GPTClient(self.config)
        self.prompt_manager = PromptManager()
        self.file_manager = FileManager()
        self.processor = DocumentProcessor(
            self.gpt_client,
            self.prompt_manager,
            self.file_manager
        )

    def run(self):
        """
        Run the application
        """
        print("Welcome to the GPT Document Processor!")
        print("This script will process your text file and create an expanded version.")
        print("You can paste the full file path, even if it contains spaces.")
        
        try:
            # Initialize all components
            self.initialize()
            
            # Get file path
            file_path = input("Please enter the full path to the document you want to process: ").strip()
            
            # Remove any surrounding quotes if present
            if (file_path.startswith('"') and file_path.endswith('"')) or \
               (file_path.startswith("'") and file_path.endswith("'")):
                file_path = file_path[1:-1]
            
            print(f"Processing file: {file_path}")
            result = self.processor.process_document(file_path)
            
            if result:
                print("Processing successful. Please check the output file for the processed document.")
            else:
                print("Processing failed. Please check the error messages above for more details.")

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        
        input("Press Enter to exit...")