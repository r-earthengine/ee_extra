import json

import requests

# Request ee-appshot
eeAppshot = requests.get(
    "https://raw.githubusercontent.com/samapriya/ee-appshot/main/app_urls.json"
).json()
# Save the dict as json file
with open("./ee_extra/data/ee-appshot.json", "w") as fp:
    json.dump(eeAppshot, fp, indent=4, sort_keys=True)
