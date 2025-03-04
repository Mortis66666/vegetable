import json
from langdetect import detect


with open("langcode.json", "r") as f:
    langcode = json.load(f)

def get_source_lang(txt):
    return langcode.get(detect(txt), "Unknown")