import json


class JsonReader:
    def read_file(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
