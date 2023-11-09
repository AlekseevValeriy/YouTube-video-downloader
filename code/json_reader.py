import json

"""
Класс, который считывает или записывает информацию с или в .json файл
"""


class JsonReader:
    @staticmethod
    def read_file(file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def write_file(data: dict, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
