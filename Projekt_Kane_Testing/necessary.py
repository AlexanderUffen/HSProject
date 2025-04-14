import json
import base64
import re


def speichern_in_datei(daten, dateiname):
    with open(dateiname, 'w') as datei:
        json.dump(daten, datei)


def laden_aus_datei(dateiname):
    with open(dateiname, 'r') as datei:
        return json.load(datei)

def encode_image(image_path):
   
    with open(image_path, 'rb') as image_file:
       return base64.b64encode(image_file.read()).decode('utf-8')

def extract_code(text):
    # Pattern to match the code block
    pattern = r'```python\s+(.*?)\s+```'
    #Extract the code
    match = re.search(patter, text, re.DOTALL)
    if match:
        return match.group(1)
    return None