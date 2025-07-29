import requests
import json
import random

API_KEY = "AIzaSyA7wxG0O5EypomEwGErAkg39iVZPZL6u_E"
MODEL = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def answer_question_from_data(question, qa_data: list[dict]) -> str:
    if not qa_data:
        return "Maalesef şu anda bu ürünle ilgili yeterli bilgiye ulaşamıyorum 😔 Ama dilersen başka bir soruda yardımcı olabilirim!"

    # Soru-cevap örneklerini hazırlıyoruz
    examples = "\n".join([f"Soru: {qa['question']}\nCevap: {qa['answer']}" for qa in qa_data])

    prompt = (
        "Sen Trendyol'da çalışan samimi, yardımsever ve bilgili bir asistan botsun. "
        "Aşağıda bazı kullanıcıların ürünle ilgili sorduğu sorular ve cevapları var. "
        "Şimdi bir kullanıcı yeni bir soru soruyor. Bu soruya elindeki bilgilere göre doğal ve kullanıcı dostu bir dille cevap ver. "
        "Eğer elindeki bilgilerden tam bir cevap çıkaramıyorsan, dürüstçe bunu belirt ama kullanıcıyı hayal kırıklığına uğratma.\n\n"
        f"{examples}\n\n"
        f"Kullanıcı Sorusu: {question}\n"
        f"Asistan Yanıtı:"
    )

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        res = requests.post(API_URL, headers=headers, data=json.dumps(data))
        result = res.json()

        if "candidates" in result and result["candidates"]:
            response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Ek filtreleme: Çok kısa, yetersiz ya da hatalı yanıtları kontrol edelim
            if not response_text or "üzgünüm" in response_text.lower() or len(response_text.split()) < 4:
                return random.choice([
                    "Şu an elimde bu konuda net bir bilgi yok 🙈 ama dilersen farklı bir ürünle ilgili yardımcı olabilirim!",
                    "Bu soruya doğrudan bir cevabım yok ama ürünü inceleyip daha fazla bilgi toplayabilirim 🧐",
                    "Maalesef bu konuda kesin bir bilgi bulamadım 😓 ama başka soruların varsa seve seve yardımcı olurum!"
                ])
            return response_text

        elif "error" in result:
            return f"Gemini API Hatası: {result['error'].get('message', 'Bilinmeyen hata')}"
        else:
            return "Beklenmeyen bir durum oluştu, daha sonra tekrar denemeni öneririm."
    except Exception as e:
        return f"İşlem sırasında bir hata oluştu: {str(e)}"
