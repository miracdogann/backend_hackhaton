from django.http import HttpResponse
from rest_framework.views import APIView 
from rest_framework import status
from rest_framework.response import Response
from .url_olusturma.chat import chat_with_memory
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import base64
from aiAssistan.scraper.trendyol_scraper_selenium import get_all_comments
from .gemini.comment_summary import analyze_emotions, summarize_comments
from .scraper.qna_scraper import get_all_questions_and_answers
from .gemini.qna_answering import answer_question_from_data
import traceback
from dotenv import load_dotenv
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types
from .utils.base64_helpers import array_buffer_to_base64

def home(request):
    return HttpResponse("Merhaba, burası anasayfa asistan!")

class Chat(APIView):
    def get(self, request):
        data = {"message": "Merhaba chat API!"}
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user_input = request.data.get("message")  # Önyüzden "message" alanını bekliyoruz
        print("apiden gelen mesaj",user_input)
        if not user_input:
            return Response({"error": "Mesaj bulunamadı"}, status=status.HTTP_400_BAD_REQUEST)
        user_input = str(user_input)
        # chat_with_memory fonksiyonunu çağır
        result = chat_with_memory(user_input)

        # Dönen sonucu JSON olarak dön
        return Response(result, status=status.HTTP_200_OK)
   

qa_cache = {}

@api_view(['POST'])
def answer_question_view(request):
    url = request.data.get("url")
    user_question = request.data.get("question")

    if not url or not user_question:
        return Response({"error": "Lütfen url ve question parametrelerini sağlayın."}, status=status.HTTP_400_BAD_REQUEST)

    parsed_url = urlparse(url)
    path = parsed_url.path

    if "/saticiya-sor" not in path:
        query_params = parse_qs(parsed_url.query)
        new_path = path.rstrip("/") + "/saticiya-sor"
        url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            parsed_url.params,
            urlencode(query_params, doseq=True),
            parsed_url.fragment
        ))

    if url not in qa_cache:
        qa_data = get_all_questions_and_answers(url)
        if not qa_data:
            return Response({"error": "Soru-cevap verisi bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        qa_cache[url] = qa_data
    else:
        qa_data = qa_cache[url]

    ai_answer = answer_question_from_data(user_question, qa_data)

    return Response({
        "question": user_question,
        "ai_answer": ai_answer,
        "qa_data_length": len(qa_data),
    })


@api_view(['POST'])
def analyze_trendyol_product(request):
    url = request.data.get("url")
    if not url:
        return Response({"error": "URL parametresi eksik."}, status=status.HTTP_400_BAD_REQUEST)

    parsed_url = urlparse(url)
    path = parsed_url.path

    if "/yorumlar" not in path:
        query_params = parse_qs(parsed_url.query)
        new_path = path.rstrip("/") + "/yorumlar"
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            parsed_url.params,
            urlencode(query_params, doseq=True),
            parsed_url.fragment
        ))
        target_url = new_url
    else:
        target_url = url

    comments = get_all_comments(target_url)
    if not comments:
        return Response({"error": "Yorum bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

    summary = summarize_comments(comments)
    comments_with_emotion = analyze_emotions(comments)

    emotion_stats = {"Mutlu": 0, "Üzgün": 0, "Kızgın": 0, "Nötr": 0}
    for c in comments_with_emotion:
        for key in emotion_stats.keys():
            if key in c:
                emotion_stats[key] += 1

    return Response({
        "product_url": url,
        "target_url": target_url,
        "comment_count": len(comments),
        "summary": summary,
        "raw_comments": comments_with_emotion,
        "emotion_stats": emotion_stats,
    })





load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY  = "AIzaSyDy1WEWDCXyVV2ee1N67SORE7QjDsbL6lc"
client = genai.Client(api_key=GEMINI_API_KEY)

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def try_on_view(request):
    if request.method == 'GET':
        return Response({"message": "Bu endpoint sadece POST yöntemiyle çalışır. Lütfen bir görsel yükleyin."}, status=200)

    try:
        person_image = request.FILES.get("person_image")
        cloth_image = request.FILES.get("cloth_image")
        instructions = request.POST.get("instructions", "")
        
        if not person_image or not cloth_image:
            return Response({"error": "Görseller eksik."}, status=status.HTTP_400_BAD_REQUEST)

        ALLOWED_MIME_TYPES = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
            "image/heif",
        }

        MAX_IMAGE_SIZE_MB = 16

        if person_image.content_type not in ALLOWED_MIME_TYPES or cloth_image.content_type not in ALLOWED_MIME_TYPES:
            return Response({"error": "Desteklenmeyen dosya formatı."}, status=status.HTTP_400_BAD_REQUEST)

        if person_image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024 or cloth_image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            return Response({"error": "Görsel boyutu 10MB'den büyük olamaz."}, status=status.HTTP_400_BAD_REQUEST)

        user_bytes = person_image.read()
        cloth_bytes = cloth_image.read()

        # Gemini prompt
        prompt = f"""
            Kullanıcı aşağıda iki adet görsel yükledi:

            1. **Kullanıcının kendi görseli:** Bu görselde bir kişi, belden yukarısı net şekilde görülecek şekilde, doğrudan kameraya bakan bir pozisyondadır. Üzerinde mevcutta başka bir kıyafet (örneğin tişört veya gömlek) olabilir.
            2. **Denenmek istenen kıyafet görseli:** Bu görsel, kullanıcı tarafından denenmek istenen yeni bir kıyafeti (örneğin gömlek, tişört, elbise vb.) içermektedir. Kıyafet düz bir yüzeye veya manken üzerine serilmiş olabilir.

            ### Hedef:
            Bu iki görseli kullanarak, kullanıcı sanki bu kıyafeti gerçekten giyiyormuş gibi **gerçekçi**, **orantılı**, **doğal ışık ve gölge uyumu olan** bir sanal deneme görseli üret.

            ### Teknik Beklentiler:
            - Kıyafet, kişinin vücut hatlarına ve duruşuna uygun şekilde oturtulmalı.
            - Kıyafetin üzerindeki doku, desen ve renkler orijinaline sadık kalmalı.
            - Kıyafetin önceden giydiği kıyafetin üzerine katman olarak değil, onun yerine giydirilmiş gibi görünmesi beklenir.
            - Giydirilen kıyafetin yakası, kol açıklıkları, boy uzunluğu gibi detaylar kişiye göre orantılanmalı.
            - Oluşturulan görselde kesme/ekleme hataları, bozulmalar veya yapaylık hissi olmamalı.

            Lütfen görsel ile birlikte kısa bir açıklama metni de üret:
            - Kullanıcının bu kıyafeti nasıl taşıdığı
            - Uyumlu olup olmadığı
            - Giysinin hangi tarza hitap ettiği hakkında bir özet

            Varsa ek kullanıcı talimatları:
            {instructions}

            Yanıtı lütfen Türkçe olarak ver.
            """


        contents = [
            prompt,
            types.Part.from_bytes(data=user_bytes, mime_type=person_image.content_type),
            types.Part.from_bytes(data=cloth_bytes, mime_type=cloth_image.content_type)

        ]

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        image_data = None
        text_response = "Açıklama yok."
        if response.candidates:
            parts = response.candidates[0].content.parts
            for part in parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data
                    image_mime_type = getattr(part.inline_data, "mime_type", "image/png")
                elif hasattr(part, "text") and part.text:
                    text_response = part.text

        
        image_url = None
        if image_data:
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{image_mime_type};base64,{image_base64}"

            

        return Response({
    "image": image_url,
    "text": text_response
})


    except Exception as e:
        traceback.print_exc()
        return Response({"error": "Sunucu hatası", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)