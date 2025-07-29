from google import genai
import os
from dotenv import load_dotenv
import json
import re
from .kategoriBulma import kategori_bulma
from .beden import beden_bulma
from .cinsiyet import cinsiyet_bulma
from .create_url_trendyol import url_trendyol
from .search_trendyol_url import search_url
from .renk import renk_bulma

load_dotenv()  # .env dosyasını yükler

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("GEMINI_API_KEY ortam değişkeni bulunamadı!")

client = genai.Client(api_key=api_key)

chat_history = []

def chat_with_memory(user_message):
    # Promptu JSON çıktı üretecek şekilde ayarla
    prompt = (
        "Kullanıcı mesajını analiz et ve önce mesajın amacı sohbet mi yoksa alışveriş mi olduğunu belirle.\n"
        "Eğer sohbetse, Trendyol alışveriş asistanı gibi samimi, yardımcı ve doğal bir şekilde yanıt ver. Yanıt JSON formatında şu şekilde olmalı:\n"
        "{\n"
        "  \"niyet\": \"sohbet\",\n"
        "  \"cevap\": \"Trendyol asistanı tarzında samimi ve doğal bir yanıt\"\n"
        "}\n"
        "Örnek sohbet yanıtı: 'Merhaba! 😊 Trendyol’da alışveriş keyfini yaşamak için buradayım. Ne hakkında sohbet etmek istersin, yeni trendler mi, yoksa başka bir şey mi?' veya 'Hafta sonu için alışveriş planın var mı? 😄 Sana en güzel önerileri sunabilirim!'\n"
        "Eğer alışveriş isteği varsa, aşağıdaki gibi JSON çıktısı ver:\n"
        "{\n"
        "  \"niyet\": \"alisveris\",\n"
        "  \"istenen\": \"Ürün kategorisi veya hediye türü\",\n"
        "  \"fiyat_araligi\": \"min-max\",\n"
        "  \"cinsiyet\": \"erkek | kadın | çocuk | belli değil\",\n"
        "  \"marka\": \"belli değil veya marka adı\",\n"
        "  \"beden\": \"belli değil veya s,m,l,xl gibi\",\n"
        "  \"ozellik\": \"belli değil veya gb, ram, kapasite, ağırlık vb gibi\",\n"
        "  \"renk\": \"belli değil veya mavi, siyah, yeşil gibi\"\n"
        "}\n\n"
        "Kurallar:\n"
        "- Fiyat aralığı varsa '500-800' formatında yaz.\n"
        "- Fiyat tek belirtilmişse, örneğin '500 tl' ise '0-500' yaz.\n"
        "- Fiyat belli değilse 'belli değil' yaz, asla '0-0' yazma.\n"
        "- Cinsiyet belirtilmemişse 'belli değil' yaz.\n"
        "- Cinsiyeti bulmak için detaylı analiz yap! 'kardeşim', 'abim', 'ablam', 'babam', 'annem', 'dayım', 'halam', 'kuzenim' gibi kelimelerden çıkarım yap.\n"
        "- Marka belirtilmemişse 'belli değil' yaz.\n"
        "- Beden belirtilmemişse 'belli değil' yaz.\n"
        "- Birden fazla beden varsa virgülle ayır (örn: 's,m,l').\n"
        "- Eğer marka ve ürün adı açıkça belirtilmişse, 'istenen' kısmına ikisini birleştirerek yaz (örn: 'iphone 15 pro max 512 gb').\n"
        "- 'istenen' alanı mesajdaki ana ürünü özetlemeli, örneğin 'hediye', 'telefon', 'ayakkabı'.\n"
        "- Alışveriş isteğinde, Trendyol tarzında yardımcı bir üslup kullan. Örneğin, 'Hemen sana iPhone 16 Pro Max 512 GB için en iyi seçenekleri bulalım! 😊' gibi.\n\n"
        f"Kullanıcı mesajı: \"{user_message}\"\n"
        "JSON çıktıyı ver:"
    )

    # Önceki sohbetleri ekle
    full_conversation = ""
    for entry in chat_history:
        full_conversation += f"Kullanıcı: {entry['user']}\nAsistan: {entry['assistant']}\n"
    full_conversation += prompt

    # Model çağrısı
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_conversation
    )
    assistant_message = response.text.strip()
    cleaned = re.sub(r"```json|```", "", assistant_message).strip()

    # JSON parse et
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        data = {"niyet": "sohbet", "cevap": "Üzgünüm, mesajınızı anlayamadım. 😊 Alışveriş mi yapalım, yoksa başka bir konuda mı sohbet edelim?"}

    # Niyet kontrolü
    if data.get("niyet") == "sohbet":
        # Sohbet durumunda sadece cevabı döndür
        chat_response = data.get("cevap")
        chat_history.append({
            "user": user_message,
            "assistant": chat_response
        })
        return {
            "gemini_response": chat_response,
        }
    else:
        # Alışveriş durumunda mevcut iş mantığını koru
        kategori = data.get("istenen", "belli değil").lower()
        fiyat = data.get("fiyat_araligi", "belli değil").lower()
        beden = data.get("beden", "belli değil").lower()
        cinsiyet = data.get("cinsiyet", "belli değil").lower()
        marka = data.get("marka", "belli değil").lower()
        renk = data.get("renk", "belli değil").lower()
        ozellik = data.get("ozellik", "belli değil").lower()
        url = None
        if beden != "belli değil":
            beden = beden_bulma(beden=beden)
            print("beden:", beden)

        if cinsiyet != "belli değil":
            cinsiyet = cinsiyet_bulma(cinsiyet=cinsiyet)
            print("cinsiyet:", cinsiyet)

        if renk != "belli değil":
            renk = renk_bulma(renk)
            print("renk:", renk)

        if marka == "belli değil":
            print("marka yok")
            kategori = kategori_bulma(kategori=kategori)
            print("kategori:", kategori)
            url = url_trendyol(kategori=kategori, fiyat=fiyat, renk=renk, beden=beden, cinsiyet=cinsiyet)
        else:
            if ozellik != "belli değil" and ozellik not in kategori:
                kategori = kategori + " " + ozellik
            if marka not in kategori:
                kategori = marka + " " + kategori
                print("marka ve kategori birleştirildi:", kategori)
            else:
                print("marka kategori içinde var, işlem yapılmadı.")
            url = search_url(kategori=kategori, fiyat=fiyat, renk=renk, beden=beden, cinsiyet=cinsiyet)

        # Alışveriş yanıtını Trendyol asistanı tarzında oluştur
        alisveris_response = (
            f"Hemen sana en iyi seçenekleri bulalım! 😊 "
            "Trendyol’da harika ürünler seni bekliyor!"
        ).strip()

        print("gemini yanıtı ",alisveris_response , "url ,",url)
        # Sohbet geçmişini güncelle
        chat_history.append({
            "user": user_message,
            "assistant": alisveris_response
        })

        return {
            "gemini_response": alisveris_response,
            "url": url
        }

# TEST
if __name__ == "__main__":
    test_cases = [
        "Merhaba, nasılsın?",
        "Telefon Alacağım iPhone 16 Pro Max, 512 GB olsun yardımcı olur musun",
        "Çocuğum için defacto marka 500-800 TL arası xl,l gömlek istiyorum",
        "4 yaşındaki kardeşim için çizim tableti almak istiyorum 600 tl param var yardımıcı olur musun",
        "Annem için elbise arıyorum, beden M ve L bütçem 900 tl",
        "Ev için Arçelik Marka Çamaşır makinesi alacağım bütçem 55000 Tl ye kadar var beyaz renk olsun",
        "Çocuklar için mavi renk ayakkabı istiyorum, en fazla 900 TL olsun"
    ]

    for user_input in test_cases:
        print(f"\nKullanıcı: {user_input}")
        result = chat_with_memory(user_input)
        print("Gemini JSON output:", result["gemini_response"])
        print("URL:", result["url"])