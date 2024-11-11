class DocumentProcessor:
    def __init__(self, gpt_client, prompt_manager, file_manager):
        self.gpt_client = gpt_client
        self.prompt_manager = prompt_manager
        self.file_manager = file_manager

    def split_into_sections(self, text):
        """
        Split the text into logical sections
        """
        prompt = self.prompt_manager.create_section_prompt(text)
        return self.gpt_client.create_completion(prompt)

    def expand_section(self, section, document_title):
        """
        Expand a section with more detailed content
        """
        prompt = self.prompt_manager.create_expansion_prompt(section, document_title)
        response = self.gpt_client.create_completion(prompt)
        return response['expanded_content']

    def combine_sections(self, expanded_sections, document_title):
        """
        Combine expanded sections into a final document
        """
        prompt = self.prompt_manager.create_combination_prompt(expanded_sections, document_title)
        response = self.gpt_client.create_completion(prompt)
        return response['final_document']

    def process_document(self, file_path):
        """
        Process the entire document
        """
        try:
            # Step 1: Read the file
            print(f"Reading file: {file_path}")
            text = self.file_manager.read_file(file_path)

            # Step 2: Split into sections
            print("Step 1: Splitting the document into sections...")
            document_structure = self.split_into_sections(text)

            # Step 3: Expand each section
            print("Step 2: Expanding each section...")
            expanded_sections = []
            for i, section in enumerate(document_structure['sections'], 1):
                print(f"  Processing section {i} of {len(document_structure['sections'])}...")
                expanded_content = self.expand_section(section, document_structure['document_title'])
                expanded_sections.append({
                    'title': section['title'],
                    'expanded_content': expanded_content
                })

            # Step 4: Combine sections
            print("Step 3: Combining sections into final document...")
            final_document = self.combine_sections(expanded_sections, document_structure['document_title'])

            # Step 5: Save the result
            output_path = self.file_manager.save_file(final_document, file_path)
            print(f"Document processing complete. Processed document saved to: {output_path}")
            
            return final_document

        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None