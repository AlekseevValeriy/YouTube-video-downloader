import json


class JsonReader:
    def read_file(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_file(self, data: dict, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file)

a = {'1': 2, "3": 4}

print((str(a.values())[12:-1]).strip('[]').replace("'", '').split(', '))
print((str(a.keys())[10:-1]).strip('[]').replace("'", '').split(', '))