import json


class JsonReader:
    def read_file(self, file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_file(self, file_path: str, *elements: (list,)) -> None:
        with open(file_path, 'w', encoding='utf-8') as file:
            data = json.load(file)
            for element in elements:
                data[element[0]] = element[1]
            json.dump(data, file)


if __name__ == '__main__':
    jw = JsonReader()
    # print(jw.read_file('errors_presets.json'))
    jw.write_file('errors_presets.json', ['Error', 'ничего'])
