import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_all_comments(product_url):
    options = Options()
    options.add_argument("--start-maximized")
    # İstersen headless modda çalıştırmak için şunu ekleyebilirsin:
    # options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(product_url)
    time.sleep(3)  # Sayfanın yüklenmesini bekle

    scroll_pause_time = 0.5
    scroll_step = 300  # px
    max_same_scrolls = 3
    same_scrolls = 0

    last_position = driver.execute_script("return window.pageYOffset")

    print("🔽 Yorumlar için sayfa kaydırılıyor...")

    while True:
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(scroll_pause_time)

        current_position = driver.execute_script("return window.pageYOffset")
        if current_position == last_position:
            same_scrolls += 1
            print(f"Daha fazla kaydırılamıyor gibi görünüyor. ({same_scrolls}/{max_same_scrolls})")
            if same_scrolls >= max_same_scrolls:
                print("✅ Sayfanın sonuna ulaşıldı.")
                break
        else:
            same_scrolls = 0
            last_position = current_position

    time.sleep(2)  # Tüm yorumların yüklenmesini bekle

    # Yorum elementlerini topla
    comment_elements = driver.find_elements(By.CSS_SELECTOR, ".comment-text")
    comments = [el.text.strip() for el in comment_elements if el.text.strip()]

    print(f"💬 Toplam yorum sayısı: {len(comments)}")

    driver.quit()
    return comments