# aiAssistan/scraper/qna_scraper.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_all_questions_and_answers(product_url):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  # Gerekirse görünmez mod için aç
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    # Q&A sayfasına yönlendirme
    if "/saticiya-sor" not in product_url:
        if not product_url.endswith("/"):
            product_url += "/"
        product_url += "saticiya-sor"

    driver.get(product_url)
    time.sleep(3)
    print("📄 Q&A sayfası açıldı, yavaş scroll başlatılıyor...")

    scroll_pause_time = 0.4
    scroll_step = 300  # px
    max_same_scrolls = 5
    same_scrolls = 0

    last_position = driver.execute_script("return window.pageYOffset")

    while True:
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(scroll_pause_time)

        current_position = driver.execute_script("return window.pageYOffset")
        if current_position == last_position:
            same_scrolls += 1
            if same_scrolls >= max_same_scrolls:
                print("✅ Sayfanın sonuna ulaşıldı (daha fazla kaydırılamıyor).")
                break
        else:
            same_scrolls = 0
            last_position = current_position

    time.sleep(2)

    qna_items = driver.find_elements(By.CSS_SELECTOR, ".qna-item")
    print(f"\n🔍 Toplam Q&A bloğu bulundu: {len(qna_items)}")

    questions = []
    question_count = 0
    answer_count = 0
    valid_pairs = 0

    for item in qna_items:
        try:
            question_el = item.find_element(By.CSS_SELECTOR, ".item-content h4")
            question_text = question_el.text.strip()
            if question_text:
                question_count += 1

            answer_el = item.find_element(By.CSS_SELECTOR, ".answer h5")
            answer_text = answer_el.text.strip()
            if answer_text:
                answer_count += 1

            if question_text and answer_text:
                questions.append({"question": question_text, "answer": answer_text})
                valid_pairs += 1

        except Exception:
            continue

    print(f"❓ Toplam Soru: {question_count}")
    print(f"✅ Toplam Cevap: {answer_count}")
    print(f"🧩 Geçerli Soru-Cevap Çifti: {valid_pairs}\n")

    driver.quit()
    return questions





