from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from aiAssistan.scraper.trendyol_scraper_selenium import get_all_comments
from .gemini.comment_summary import analyze_emotions, summarize_comments
from .scraper.qna_scraper import get_all_questions_and_answers
from .gemini.qna_answering import answer_question_from_data


@api_view(['GET'])
def home(request):
    return Response({"message": "Merhaba dünya!"})


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
