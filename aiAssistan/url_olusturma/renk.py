import json
from rapidfuzz import process
import os 

dosya_yolu = os.path.join(os.path.dirname(__file__), "renkler.json")
print(dosya_yolu)
def renk_bulma(renk):
     # kategori kodu wcl
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        renkler = json.load(f)

    best_match, score, _ = process.extractOne(renk, renkler.keys())
    #  eşleşen key ile value'yu al
    print(best_match,score)
    value = renkler[best_match]
    print("renk kodu",value)

    return value


# renk_bulma("siyah")