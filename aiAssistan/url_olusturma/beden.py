def beden_bulma(beden):
    # Haritalama
    # beden size kodu vr
    beden_map = {
        "XS": "xs",
        "S": "s",
        "M": "m",
        "L": "l",
        "XL": "xl",
        "2XL": "2xl",
        "3XL": "3xl"
    }

    # Gelen beden string'ini parçala
    bedenler = [b.strip().upper() for b in beden.split(",")]

    # Geçerli olanları map'e göre çevir
    secimler = [beden_map[b] for b in bedenler if b in beden_map]

    if not secimler:
        return None  # ya da "" dönebilirsin

    # İstenilen formatta birleştir
    return f"size|group-{'_group-'.join(secimler)}"

# print(beden_bulma("Xs,l,3Xl"))