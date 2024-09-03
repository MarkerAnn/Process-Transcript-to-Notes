import datetime
import time
import os
from dotenv import load_dotenv
from anthropic import Anthropic, RateLimitError
import json

# Load environment variables from .env file
load_dotenv()

# Configure Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def split_into_sections(text, max_retries=5, initial_delay=1):
    def chunk_text(text, chunk_size=15000):
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        for word in words:
            if current_size + len(word) + 1 > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def parse_response(response_text):
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

    chunks = chunk_text(text)
    all_sections = []
    document_title = ""

    print(f"Text split into {len(chunks)} chunks for processing")

    for i, chunk in enumerate(chunks):
        print(f"\nProcessing chunk {i+1} of {len(chunks)}...")

        prompt = f"""
        Dela upp följande text i logiska sektioner. För varje sektion, ge en beskrivande rubrik.
        Detta är del {i+1} av {len(chunks)} av hela dokumentet.
        
        Formatera ditt svar enligt följande:
        - Första raden: Övergripande dokumenttitel
        - För varje sektion:
          SECTION: Sektionsrubrik
          Innehållet i sektionen...

        Här är texten att bearbeta:

        {chunk}
        """
        
        for attempt in range(max_retries):
            try:
                print(f"  Attempt {attempt + 1} of {max_retries}")
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=8192,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                print(f"Raw response from Claude for chunk {i+1}:")
                print(response.content)
                
                # Extrahera texten från TextBlock-objektet
                response_text = response.content[0].text if response.content else ""
                
                chunk_title, chunk_sections = parse_response(response_text)
                if not document_title:
                    document_title = chunk_title
                    print(f"Document title extracted: {document_title}")
                
                all_sections.extend(chunk_sections)
                print(f"Chunk {i+1} processed. Sections in this chunk: {len(chunk_sections)}")
                print("Sections in this chunk:")
                for section in chunk_sections:
                    print(f"  - {section['title']} ({len(section['content'])} characters)")
                
                print(f"Total sections so far: {len(all_sections)}")
                break
                
            except RateLimitError:
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"  Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("  Max retries reached. Unable to process request.")
                    raise
            except Exception as e:
                print(f"  An error occurred: {str(e)}")
                if attempt == max_retries - 1:
                    raise

        # Respect rate limit
        if i < len(chunks) - 1:  # Don't wait after the last chunk
            print(f"Waiting 12 seconds before processing next chunk...")
            time.sleep(12)  # Wait 12 seconds between chunks to respect 5 requests/minute limit

    print(f"\nAll chunks processed. Total sections: {len(all_sections)}")
    return {
        "document_title": document_title,
        "sections": all_sections
    }

def expand_section(section, document_title, max_retries=5, initial_delay=1):
    print(f"Expanding section: {section['title']}")
    prompt = f"""
    Expandera följande sektion till en mycket mer detaljerad version. Behåll så mycket som möjligt av originalinnehållet, inklusive all relevant information, exempel, och specifika detaljer. Det är viktigt att bevara strukturen och ordningen i originalinnehållet. Lägg till förklaringar där det behövs för att förtydliga koncept.

    Inkludera all relevant information och exempel. Det är okej att upprepa information eller gå in på sidospår om det hjälper till att förklara koncepten bättre. Det är också okej att lägga in exempel eller kodblock i java för att förklara koncept.

    Försök att fånga föreläsarens stil och ton. Om det finns några skämt, anekdoter eller personliga reflektioner, inkludera dem.

    Dokumenttitel: {document_title}
    Sektionsrubrik: {section['title']}

    Originaltext:
    {section['content']}

    Formatera ditt svar enligt följande:
    EXPANDED_CONTENT:
    Den expanderade, detaljerade texten här...
    """

    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1} of {max_retries}")
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text if response.content else ""
            if response_text.startswith("EXPANDED_CONTENT:"):
                print(f"Section '{section['title']}' expanded successfully")
                return response_text[18:].strip()
            else:
                raise ValueError("Unexpected response format")
        
        except RateLimitError:
            print(f"Rate limit exceeded on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Unable to process request.")
                raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise
        
    print (f"Failed to expand section '{section['title']}' after {max_retries} attempts")
    raise Exception(f"Failed to expand section '{section['title']}' after {max_retries} attempts")

def combine_sections(expanded_sections, document_title, max_retries=5, initial_delay=1):
    print(f"Combining {len(expanded_sections)} expanded sections into final document...")
    sections_text = "\n\n".join([f"Sektion {i+1}: {section['title']}\n\n{section['expanded_content']}" 
                                 for i, section in enumerate(expanded_sections)])
    
    prompt = f"""
    Kombinera följande expanderade sektioner till ett sammanhängande dokument. Gör minimala ändringar för att få texten att flyta naturligt, men behåll så mycket detaljerad information som möjligt. Undvik att komprimera eller sammanfatta för mycket.

    Dokumenttitel: {document_title}

    {sections_text}

    Formatera ditt svar enligt följande:
    FINAL_DOCUMENT:
    Det kombinerade, sammanhängande dokumentet här...
    """

    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1} of {max_retries}")
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text if response.content else ""
            if response_text.startswith("FINAL_DOCUMENT:"):
                print(f"Sections combined successfully")
                return response_text[16:].strip()
            else:
                raise ValueError("Unexpected response format")
        
        except RateLimitError:
            print(f"Rate limit exceeded on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Unable to process request.")
                raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise

    print(f"Failed to combine sections after {max_retries} attempts")
    raise Exception(f"Failed to combine sections after {max_retries} attempts")

def process_document(file_path):
    try:
        print(f"\nReading file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        print(f"File read successfully. Total characters: {len(text)}")

        print("\nStep 1: Splitting the document into sections...")
        try:
            document_structure = split_into_sections(text)
            print(f"Document split into {len(document_structure['sections'])} sections")
        except Exception as e:
            print(f"Error in split_into_sections: {str(e)}")
            return None

        if not document_structure or 'sections' not in document_structure or not document_structure['sections']:
            print("No valid sections found in the document structure")
            return None

        print("\nStep 2: Expanding each section...")
        expanded_sections = []
        for i, section in enumerate(document_structure['sections'], 1):
            print(f"  Processing section {i} of {len(document_structure['sections'])}: {section['title']}")
            try:
                expanded_content = expand_section(section, document_structure.get('document_title', 'Unknown Title'))
                if expanded_content:
                    expanded_sections.append({
                        'title': section['title'],
                        'expanded_content': expanded_content
                    })
                    print(f"  Section {i} expanded successfully")
                else:
                    print(f"  Failed to expand section {i}: Empty content returned")
            except Exception as e:
                print(f"  Error expanding section {i}: {str(e)}")
            
            if i < len(document_structure['sections']):
                print("  Waiting 12 seconds before processing next section...")
                time.sleep(12)  # Pause between sections to respect rate limits

        if not expanded_sections:
            print("Failed to expand any sections")
            return None

        print(f"\nStep 3: Combining {len(expanded_sections)} sections into final document...")
        try:
            final_document = combine_sections(expanded_sections, document_structure.get('document_title', 'Unknown Title'))
            if not final_document:
                print("Failed to combine sections: Empty document returned")
                return None
            print("Sections combined successfully")
        except Exception as e:
            print(f"Error combining sections: {str(e)}")
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file_path = f"{os.path.dirname(file_path)}/{base_name}_processed_{timestamp}.txt"

        print(f"\nSaving processed document to: {output_file_path}")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(final_document)

        print(f"Document processing complete. Processed document saved.")
        return final_document
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please check the file path and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return None

# Example usage
if __name__ == "__main__":
    print("Welcome to the Claude Document Processor!")
    print("This script will process your text file and create an expanded version.")
    print("You can paste the full file path, even if it contains spaces.")
    file_path = input("Please enter the full path to the document you want to process: ").strip()
    
    # Remove any surrounding quotes if present
    if (file_path.startswith('"') and file_path.endswith('"')) or \
       (file_path.startswith("'") and file_path.endswith("'")):
        file_path = file_path[1:-1]
    
    print(f"Processing file: {file_path}")
    result = process_document(file_path)
    if result:
        print("Processing successful. Please check the output file for the processed document.")
    else:
        print("Processing failed. Please check the error messages above for more details.")

    input("Press Enter to exit...")