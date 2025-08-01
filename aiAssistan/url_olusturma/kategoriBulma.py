import json
from rapidfuzz import process
from .create_url_trendyol import url_trendyol
import os 

dosya_yolu = os.path.join(os.path.dirname(__file__), "categories.json")

def kategori_bulma(kategori):
    # kategori kodu wc
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        CATEGORIES = json.load(f)

    best_match, score, _ = process.extractOne(kategori, CATEGORIES.keys())

    # eşleşen key ile value'yu al
    print(best_match,score)
    value = CATEGORIES[best_match]
    print("kategori kodu",value)
    # url_trendyol(kategori=value)
    return value

# kategori_bulma("telefon")
