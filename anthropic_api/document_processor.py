import datetime
import os

class DocumentProcessor:
    def __init__(self, config, token_counter, text_chunker, claude_client):
        self.config = config
        self.token_counter = token_counter
        self.text_chunker = text_chunker
        self.claude_client = claude_client
    
    def parse_section_response(self, response_text):
        lines = response_text.strip().split('\n')
        document_title = lines[0].strip()
        sections = []
        current_section = None
        
        for line in lines[1:]:
            if line.startswith('SECTION:'):
                if current_section:
                    sections.append(current_section)
                current_section = {'title': line[8:].strip(), 'content': ''}
            elif current_section:
                current_section['content'] += line + '\n'
                
        if current_section:
            sections.append(current_section)
            
        return document_title, sections
    
    def split_into_sections(self, text):
        chunks = self.text_chunker.chunk_text(text)
        all_sections = []
        document_title = ""
        
        print(f"Text split into {len(chunks)} chunks for processing")
        
        for i, chunk in enumerate(chunks):
            print(f"\nProcessing chunk {i+1} of {len(chunks)}...")
            
            prompt = self._create_section_prompt(chunk, i+1, len(chunks))
            response_text = self.claude_client.create_message(prompt)
            
            chunk_title, chunk_sections = self.parse_section_response(response_text)
            if not document_title:
                document_title = chunk_title
            
            all_sections.extend(chunk_sections)
            print(f"Chunk {i+1} processed. Sections in this chunk: {len(chunk_sections)}")
        
        return {"document_title": document_title, "sections": all_sections}
    
    def expand_section(self, section, document_title):
        print(f"Expanding section: {section['title']}")
        prompt = self._create_expansion_prompt(section, document_title)
        response_text = self.claude_client.create_message(prompt)
        
        if response_text.startswith("EXPANDED_CONTENT:"):
            return response_text[18:].strip()
        else:
            raise ValueError("Unexpected response format")
    
    def combine_sections(self, expanded_sections, document_title):
        final_document = ""
        chunk_size = 10
        
        while expanded_sections:
            sections_chunk = expanded_sections[:chunk_size]
            prompt = self._create_combination_prompt(sections_chunk, document_title)
            
            response_text = self.claude_client.create_message(prompt)
            
            if response_text.startswith("PARTIAL_DOCUMENT:"):
                partial_document = response_text[18:].strip()
                final_document += partial_document + "\n\n"
                expanded_sections = expanded_sections[len(sections_chunk):]
            else:
                raise ValueError("Unexpected response format")
        
        return final_document.strip()
    
    def process_document(self, file_path):
        try:
            print(f"\nReading file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            print("\nStep 1: Splitting the document into sections...")
            document_structure = self.split_into_sections(text)
            
            print("\nStep 2: Expanding each section...")
            expanded_sections = []
            for i, section in enumerate(document_structure['sections'], 1):
                expanded_content = self.expand_section(section, document_structure['document_title'])
                expanded_sections.append({
                    'title': section['title'],
                    'expanded_content': expanded_content
                })
            
            print("\nStep 3: Combining sections into final document...")
            final_document = self.combine_sections(expanded_sections, document_structure['document_title'])
            
            self._save_document(final_document, file_path)
            return final_document
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None
    
    def _create_section_prompt(self, chunk, current_chunk, total_chunks):
        return f"""
        Dela upp följande text i logiska sektioner. För varje sektion, ge en beskrivande rubrik.
        Detta är del {current_chunk} av {total_chunks} av hela dokumentet.
        
        Formatera ditt svar enligt följande:
        - Första raden: Övergripande dokumenttitel
        - För varje sektion:
          SECTION: Sektionsrubrik
          Innehållet i sektionen...

        Här är texten att bearbeta:

        {chunk}
        """
    
    def _create_expansion_prompt(self, section, document_title):
        return f"""
        Expandera följande sektion till en mycket mer detaljerad version. Behåll så mycket som möjligt av originalinnehållet, inklusive all relevant information, exempel, och specifika detaljer. Det är viktigt att bevara strukturen och ordningen i originalinnehållet. Lägg till förklaringar där det behövs för att förtydliga koncept.

        Dokumenttitel: {document_title}
        Sektionsrubrik: {section['title']}

        Originaltext:
        {section['content']}

        Formatera ditt svar enligt följande:
        EXPANDED_CONTENT:
        Den expanderade, detaljerade texten här...
        """
    
    def _create_combination_prompt(self, sections, document_title):
        sections_text = "\n\n".join([
            f"Sektion {i+1}: {section['title']}\n\n{section['expanded_content']}" 
            for i, section in enumerate(sections)
        ])
        
        return f"""
        Kombinera följande expanderade sektioner till en sammanhängande del av dokumentet. 
        Gör minimala ändringar för att få texten att flyta naturligt, men behåll så mycket detaljerad information som möjligt. 
        Undvik att komprimera eller sammanfatta för mycket.

        Dokumenttitel: {document_title}

        {sections_text}

        Formatera ditt svar enligt följande:
        PARTIAL_DOCUMENT:
        Den kombinerade, sammanhängande texten för denna del...
        """
    
    def _save_document(self, final_document, original_file_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(original_file_path))[0]
        output_file_path = f"{os.path.dirname(original_file_path)}/{base_name}_processed_{timestamp}.txt"
        
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(final_document)
        
        print(f"Document saved to: {output_file_path}")