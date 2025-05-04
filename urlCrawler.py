import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc


def human_scroll(driver, scroll_pause=1.5):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    while current_height < scroll_height:
        current_height += random.randint(300, 700)
        driver.execute_script(f"window.scrollTo(0, {current_height});")
        time.sleep(scroll_pause)


def random_sleep(min_sec=2, max_sec=4):
    time.sleep(random.uniform(min_sec, max_sec))


def crawl_urls(base_url, max_pages=3):
    # Cài đặt Chrome giả lập người dùng thật
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = uc.Chrome(options=options)

    job_urls = []

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}&page={page}"
            print(f"🔎 Crawling page {page}: {url}")
            driver.get(url)
            random_sleep(3, 5)

            # Mô phỏng hành vi người dùng
            human_scroll(driver)
            ActionChains(driver).move_by_offset(random.randint(0, 200), random.randint(0, 200)).perform()
            random_sleep()

            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, 'h3.title a')  # Cập nhật selector
            except NoSuchElementException as e:
                print("❌ Không tìm thấy phần tử:", e)
                continue

            print(f"📌 Tìm thấy {len(job_cards)} job URLs trên trang {page}")
            for job_card in job_cards:
                job_url = job_card.get_attribute("href")
                print(f"📌 Đang lấy URL: {job_url}")  # In URL để kiểm tra
                if job_url and job_url not in job_urls:
                    job_urls.append(job_url)

            random_sleep(2, 4)

    except Exception as e:
        print("❌ Lỗi khi crawl:", e)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print("❌ Lỗi khi đóng trình duyệt:", e)

    # Lưu kết quả
    print(f"📌 Tổng số URL thu thập được: {len(job_urls)}")
    with open("topcv_job_urls.txt", "w", encoding="utf-8") as f:
        for url in job_urls:
            f.write(url + "\n")

    print(f"\n✅ Đã lưu {len(job_urls)} job URL vào 'topcv_job_urls.txt'")


# Chạy thử
if __name__ == "__main__":
    BASE_URL = "https://www.topcv.vn/tim-viec-lam-moi-nhat?type_keyword=0&sba=1"
    crawl_urls(BASE_URL, max_pages=1)  # Crawl 1 trang đầu
