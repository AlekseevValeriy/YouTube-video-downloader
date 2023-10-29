import json


def create_buttons(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)

    data['test'] = True

    with open(file_name, 'w') as file:
        json.dump(data, file)

create_buttons('settings_presets.json')