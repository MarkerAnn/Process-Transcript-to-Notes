import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def split_into_sections(text):
    """
    STEP 1: Split the text file into logical sections and generate headers
    """
    prompt = f"""
    Dela upp följande text i logiska sektioner. För varje sektion, ge en beskrivande rubrik.
    Returnera resultatet som ett JSON-objekt med följande struktur:
    {{
        "document_title": "Övergripande titel för hela dokumentet",
        "sections": [
            {{
                "title": "Sektionsrubrik",
                "content": "Oförändrad text för sektionen"
            }},
            ...
        ]
    }}

    Här är texten att bearbeta:

    {text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

def expand_section(section, document_title):
    """
    STEP 2: Expand each section with a detailed version = more text
    """
    prompt = f"""
    expandera följande sektion till en mycket mer detaljerad verion. Inkludera alll relevant information och exempel. Det är okej att upprepa information eller gå in på sidospår. Det är också okej att lägga in exempel eller kodblock i java för att förklara koncept.

    Dokumenttitel: {document_title}
    Sektionsrubrik: {section['title']}

    Originaltext:
    {section['content']}

    Ge svaret som ett JSON-objekt med följande struktur:
    {{
      "expanded_content": "Den expanderande, detaljerade texten här
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)['expanded_content']

def combine_sections(expanded_sections, document_title):
    """
    STEP 3: Combine the sections into a single document
    """
    sections_text = "\n\n".join([f"Sektion {i+1}: {section['title']}\n\n{section['expanded_content']}" 
                                 for i, section in enumerate(expanded_sections)])
    
    prompt = f"""
    Kombinera följande expanderade sektioner till ett sammanhängande dokument. Gör minimala ändringar för att få texten att flyta naturligt, men behåll så mycket detaljerad information som möjligt. Undvik att komprimera eller sammanfatta för mycket.

    Dokumenttitel: {document_title}

    {sections_text}

    Returnera det slutliga dokumentet som ett JSON-objekt med följande struktur:
    {{
      "final_document": "Det kombinerade, sammanhängande dokumentet här"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)['final_document']

def process_document(file_path):
    """
    STEP 4: MAIN FUNCTION to process the entire document
    """
    try:
        # Read the text-file
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        print("Step 1: Splitting the document into sections...")
        document_structure = split_into_sections(text)

        print("Step 2: Expanding each section...")
        expanded_sections = []
        for i, section in enumerate(document_structure['sections'], 1):
            print(f"  Processing section {i} of {len(document_structure['sections'])}...")
            expanded_content = expand_section(section, document_structure['document_title'])
            expanded_sections.append({
                'title': section['title'],
                'expanded_content': expanded_content
            })

        print("Step 3: Combining sections into final document...")
        final_document = combine_sections(expanded_sections, document_structure['document_title'])

        # Save the final document to a new file
        output_file_path = file_path.rsplit('.', 1)[0] + '_processed.txt'
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(final_document)

        print(f"Document processing complete. Processed document saved to: {output_file_path}")
        return final_document
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please check the file path and try again.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return None

# Example usage
if __name__ == "__main__":
    print("Welcome to the GPT Document Processor!")
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