class PromptManager:
    @staticmethod
    def create_section_prompt(text):
        return f"""
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

    @staticmethod
    def create_expansion_prompt(section, document_title):
        return f"""
        expandera följande sektion till en mycket mer detaljerad verion. Inkludera alll relevant information och exempel. Det är okej att upprepa information eller gå in på sidospår. Det är också okej att lägga in exempel eller kodblock i java för att förklara koncept.

        Dokumenttitel: {document_title}
        Sektionsrubrik: {section['title']}

        Originaltext:
        {section['content']}

        Ge svaret som ett JSON-objekt med följande struktur:
        {{
          "expanded_content": "Den expanderande, detaljerade texten här"
        }}
        """

    @staticmethod
    def create_combination_prompt(expanded_sections, document_title):
        sections_text = "\n\n".join([
            f"Sektion {i+1}: {section['title']}\n\n{section['expanded_content']}" 
            for i, section in enumerate(expanded_sections)
        ])
        
        return f"""
        Kombinera följande expanderade sektioner till ett sammanhängande dokument. Gör minimala ändringar för att få texten att flyta naturligt, men behåll så mycket detaljerad information som möjligt. Undvik att komprimera eller sammanfatta för mycket.

        Dokumenttitel: {document_title}

        {sections_text}

        Returnera det slutliga dokumentet som ett JSON-objekt med följande struktur:
        {{
          "final_document": "Det kombinerade, sammanhängande dokumentet här"
        }}
        """