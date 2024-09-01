import os

from click import File

class FileHandler:

    
    folder_path = "./files/csv"    

    @staticmethod
    def save_file(file_name: str, file_bytes: bytes, file_extension: str = "csv"):
        
        try:
            full_file_name = f"{file_name}.{file_extension}"
            file_path = os.path.join(FileHandler.folder_path, full_file_name)
            with open(file_path, 'wb') as file:
                file.write(file_bytes)
            print(f"Successfully saved file: {file_path}")
            return True
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return False
    
    @staticmethod    
    def read_file(file_name : str, file_extension : str = "csv"):
        try:
            csv_path = os.path.join(FileHandler.folder_path,f"{file_name}.{file_extension}")

            # Check if the file exists
            if not os.path.exists(csv_path):
                print(f"CSV file {file_name} not found in {FileHandler.folder_path}")
            
            # Read the file and return its contents as bytes
            with open(csv_path, 'rb') as file:
                file_contents = file.read()
            print(f"Successfully read file: {csv_path}")
            return file_contents
            
            
        except Exception as e:
            print(f"Error reading file {file_name}")
            return None
           
                    




