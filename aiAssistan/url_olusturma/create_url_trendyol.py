def url_trendyol(kategori=None, fiyat=None,renk=None, beden=None, cinsiyet=None):
    base_url = "https://www.trendyol.com/"
    trendyol_url = base_url

    # Parametre kodları
    kategori_kod = "wc="
    fiyat_kod = "prc="
    beden_kod = "vr="
    cinsiyet_kod = "wg="
    renk_kod = "wcl="    
    print("gelen bilgiler:", str(kategori), str(fiyat),str(renk), str(beden), str(cinsiyet))
    if kategori:
        if kategori.startswith("/"):
            # Kategori direkt path ise
            trendyol_url += kategori.lstrip("/")
        else:
            # sr? ile başlayacak
            trendyol_url += "sr?"

            params = []
            params.append(f"{kategori_kod}{kategori}")  # kategori zorunlu ise ekle

            # Opsiyonel parametreler
            if fiyat and fiyat.lower() != "belli değil":
                params.append(f"{fiyat_kod}{fiyat}")

            if renk and renk.lower() != "belli değil":
                params.append(f"{renk_kod}{renk}")

            if beden and beden.lower() != "belli değil":
                params.append(f"{beden_kod}{beden}")

            if cinsiyet and cinsiyet.lower() not in ["belli değil", "belirtilmemiş"]:
                params.append(f"{cinsiyet_kod}{cinsiyet}")

            # Hepsini & ile birleştir
            trendyol_url += "&".join(params)

    print("Oluşan URL:", trendyol_url)
    return trendyol_url
