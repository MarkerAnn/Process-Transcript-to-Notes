class FileManager:
    @staticmethod
    def read_file(file_path):
        """
        Read content from a file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' was not found.")
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    @staticmethod
    def save_file(content, original_file_path):
        """
        Save content to a new file
        """
        try:
            output_file_path = original_file_path.rsplit('.', 1)[0] + '_processed.txt'
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(content)
            return output_file_path
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")