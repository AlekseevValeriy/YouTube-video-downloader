import shutil

import requests

url = 'https://i.ytimg.com/vi/IlQ9BLV2Mm0/hqdefault.jpg?sqp=-oaymwExCJADEOABSFryq4qpAyMIARUAAIhCGAHwAQH4Af4JgALQBYoCDAgAEAEYZSBaKFEwDw==&rs=AOn4CLAV31JliI7FcQ50bU4KNna8FTqACA'
response = requests.get(url, stream=True)
with open('img.png', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
del response