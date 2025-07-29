def cinsiyet_bulma(cinsiyet):
    cinsiyet_map = {
        "KADIN": "1",
        "ERKEK": "2",
        "ÇOCUK": "3",
        "belli değil": None,  # veya "" döndürülebilir
        "belirtilmemiş": None  # veya "" döndürülebilir

    }

    # Gelen değeri normalize et
    c = cinsiyet.strip().upper()

    return cinsiyet_map.get(c, None)
# print(cinsiyet_bulma("kadın"))
# wg=1

# print(cinsiyet_bulma("çocuk"))
# wg=3

# print(cinsiyet_bulma("belirtilmemiş"))
# None
