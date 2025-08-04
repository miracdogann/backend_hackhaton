from google import genai
import random

# Gemini istemcisi
GEMINI_API_KEY  = "AIzaSyDy1WEWDCXyVV2ee1N67SORE7QjDsbL6lc"

client = genai.Client(api_key=GEMINI_API_KEY)

def answer_question_from_data(question: str, qa_data: list[dict]) -> str:
    if not qa_data:
        return (
            "Maalesef şu anda bu ürünle ilgili yeterli bilgiye ulaşamıyorum 😔 "
            "Ama dilersen başka bir soruda yardımcı olabilirim!"
        )

    # Örnekleri oluştur
    examples = "\n".join(
        [f"Soru: {qa['question']}\nCevap: {qa['answer']}" for qa in qa_data]
    )

    # Prompt
    prompt = (
        "Sen Trendyol'da çalışan samimi, yardımsever ve bilgili bir asistan botsun. "
        "Aşağıda bazı kullanıcıların ürünle ilgili sorduğu sorular ve cevapları var. "
        "Şimdi bir kullanıcı yeni bir soru soruyor. Bu soruya elindeki bilgilere göre doğal ve kullanıcı dostu bir dille cevap ver. "
        "Eğer elindeki bilgilerden tam bir cevap çıkaramıyorsan, dürüstçe bunu belirt ama kullanıcıyı hayal kırıklığına uğratma.\n\n"
        f"{examples}\n\n"
        f"Kullanıcı Sorusu: {question}\n"
        f"Asistan Yanıtı:"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"parts": [{"text": prompt}]}]
        )
        result = response.text.strip()

        # Ek filtreleme
        if not result or "üzgünüm" in result.lower() or len(result.split()) < 4:
            return random.choice([
                "Şu an elimde bu konuda net bir bilgi yok 🙈 ama dilersen farklı bir ürünle ilgili yardımcı olabilirim!",
                "Bu soruya doğrudan bir cevabım yok ama ürünü inceleyip daha fazla bilgi toplayabilirim 🧐",
                "Maalesef bu konuda kesin bir bilgi bulamadım 😓 ama başka soruların varsa seve seve yardımcı olurum!"
            ])
        return result

    except Exception as e:
        return f"İşlem sırasında bir hata oluştu: {str(e)}"