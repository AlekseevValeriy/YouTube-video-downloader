import json

f = open('errors_presets.json')

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# list
for i in data:
    print(i)

# Closing file
f.close()