import requests
import json
import textwrap

API_KEY = "AIzaSyA7wxG0O5EypomEwGErAkg39iVZPZL6u_E"
MODEL = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def summarize_comments(comments: list[str]) -> str:
    prompt = (
        "Sen bir Trendyol ürün asistanısın. Aşağıdaki müşteri yorumlarını dikkatle analiz et.\n"
        "Yorumları başlıklar altında UX/UI açısından okunabilir şekilde kısa ve öz özetle.\n"
        "- Eğer mümkünse: olumlu, olumsuz, ürün kalitesi, kullanım deneyimi, paketleme gibi kategorilere ayır.\n"
        "- Her başlık sadece 1-2 cümlelik samimi, kullanıcı dostu açıklamalar içersin.\n"
        "- Kuru teknik metinler yerine doğal, içten, insani bir üslup kullan.\n"
        "- Sonuçları bullet-point şeklinde ve göze hitap edecek şekilde düzenle.\n"
        "- Ayrıca yorumları genel anlamda yeniden toparlayarak etkileyici ve kullanıcıyı bilgilendirici bir metinle sonuçlandır.\n\n"
        "Yorumlar:\n" + "\n".join(comments)
    )

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        result = response.json()
        summary_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return format_summary(summary_text)
    except Exception as e:
        return f"\n❌ Hata oluştu: {str(e)}"


def format_summary(summary: str) -> str:
    """
    Özetlenen metni başlıklar ve içeriklere göre biçimlendirir (başlıklar emoji ile vurgulanır).
    """
    lines = summary.strip().split("\n")
    formatted_output = []

    for line in lines:
        if line.strip().endswith(":"):
            formatted_output.append(f"\n🟨 **{line.strip()}**")
        elif line.strip().startswith("-") or line.strip().startswith("•"):
            formatted_output.append(f"  {line.strip()}")
        else:
            wrapped = textwrap.fill(line.strip(), width=90, subsequent_indent="  ")
            formatted_output.append(f"  {wrapped}")

    return "\n".join(formatted_output)


def analyze_emotions(comments: list[str]) -> list[str]:
    """
    Her yorum için duygu analizi yapar ve sonucu doğrudan kullanıcıya sunulabilecek şekilde biçimlendirir.
    """
    analyzed = []

    for comment in comments:
        prompt = (
            f"Sen bir Trendyol ürün asistanısın. Aşağıdaki müşteri yorumunun duygu durumunu analiz et.\n"
            f"Sadece şu 4 kelimeden birini döndür: Mutlu, Üzgün, Kızgın, Nötr.\n"
            f"Yorum: \"{comment}\"\n\nDuygu:"
        )

        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            result = response.json()
            emotion = result["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Göze hitap edecek şekilde format
            formatted_comment = (
                f"💬 {comment}\n"
                f"👉 **Duygu Analizi:** {emotion}"
            )
            analyzed.append(formatted_comment)

        except Exception as e:
            analyzed.append(f"{comment}\n👉 **Duygu Analizi:** Analiz edilemedi ")

    return analyzed
