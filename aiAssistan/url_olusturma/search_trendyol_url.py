from urllib.parse import quote

def search_url(kategori=None, fiyat=None,renk=None, beden=None, cinsiyet=None, sort=True):
    print("markalı işleme girildi")
    base_url = "https://www.trendyol.com/sr?"
    params = []

    print("gelen bilgiler:", str(kategori), str(fiyat), str(beden), str(cinsiyet))

    # Arama kelimesi varsa q=, qt=, st= eklenir
    if kategori:
        encoded_kategori = quote(kategori.strip())
        params.append(f"q={encoded_kategori}")
        params.append(f"qt={encoded_kategori}")
        params.append(f"st={encoded_kategori}")

    # Opsiyonel: beden
    if beden and beden.lower() not in ["belli değil", "belirtilmemiş"]:
        params.append(f"vr={quote(beden)}")

    # Opsiyonel: fiyat
    if fiyat and fiyat.lower() not in ["belli değil", "belirtilmemiş"]:
        params.append(f"prc={quote(fiyat)}")

    if renk and renk.lower() not in ["belli değil", "belirtilmemiş"]:
        params.append(f"wcl={quote(renk)}")

    # Opsiyonel: cinsiyet
    if cinsiyet and cinsiyet.lower() not in ["belli değil", "belirtilmemiş"]:
        params.append(f"wg={quote(cinsiyet)}")

    # Sıralama parametreleri (isteğe bağlı)
    if sort:
        params.append("os=1")  # otomatik sıralama
        params.append("sk=1")  # varsayılan sıralama

    # Parametreleri birleştir
    url = base_url + "&".join(params) if params else base_url.rstrip("?")
    
    print("Oluşan URL:", url)
    return url
