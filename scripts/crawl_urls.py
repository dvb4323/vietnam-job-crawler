import time
import random
from datetime import datetime
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from captcha_handle import check_for_captcha

def human_scroll(driver, scroll_pause=1.0):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_height = 0
    while current_height < scroll_height:
        scroll_amount = random.randint(250, 450)
        current_height += scroll_amount
        driver.execute_script(f"window.scrollTo(0, {current_height});")
        time.sleep(scroll_pause)


def random_sleep(min_sec=1, max_sec=2):
    time.sleep(random.uniform(min_sec, max_sec))


def init_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--ignore-certificate-errors")
    driver = uc.Chrome(options=chrome_options)
    return driver


def save_urls_to_file(urls, filepath):
    """
    Lưu danh sách URLs vào file với xử lý tạo thư mục nếu chưa tồn tại

    Args:
        urls (list): Danh sách URLs cần lưu
        filepath (str): Đường dẫn đầy đủ đến file
    """
    # Đảm bảo thư mục tồn tại
    directory = os.path.dirname(filepath)

    # Tạo thư mục nếu chưa tồn tại (bao gồm cả thư mục con)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"✅ Đã tạo thư mục: {directory}")
        except Exception as e:
            print(f"❌ Không thể tạo thư mục {directory}: {e}")
            return False

    # Lưu URLs vào file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lưu file {filepath}: {e}")
        return False


def crawl_urls(base_url, max_pages=50, output_path=None):
    driver = init_driver()
    wait = WebDriverWait(driver, 20)

    job_urls = []
    page = 1

    try:
        while page <= max_pages:
            url = f"{base_url}&page={page}"
            print(f"\n🔎 Crawling page {page}: {url}")

            # Tải trang với retry nếu lỗi
            try:
                driver.get(url)
            except TimeoutException:
                print(f"⏱️ Timeout trang {page}, thử lại sau 5 giây...")
                time.sleep(5)
                try:
                    driver.get(url)
                except Exception as e:
                    print(f"⚠️ Lỗi tiếp tục trang {page}: {e}")
                    page += 1
                    continue

            random_sleep(2, 3)

            # Kiểm tra CAPTCHA thông qua iframe chứa Google reCAPTCHA
            # try:
            #     captcha_frame = driver.find_element(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            #     print(f"🚨 CAPTCHA phát hiện trên trang {page}.")
            #     input("🔓 Vui lòng xử lý CAPTCHA thủ công, sau đó nhấn Enter để tiếp tục...")
            # except NoSuchElementException:
            #     pass  # Không có CAPTCHA, tiếp tục bình thường

            # Xử lý CAPTCHA với hàm nâng cao
            if not check_for_captcha(driver, page):
                print(f"⚠️ Không thể xử lý CAPTCHA trên trang {page}, thử trang tiếp theo")
                page += 1
                continue

            human_scroll(driver)
            # ActionChains(driver).move_by_offset(random.randint(0, 150), random.randint(0, 150)).perform()
            try:
                element = driver.find_element(By.TAG_NAME, "body")
                ActionChains(driver).move_to_element(element).perform()
            except Exception as e:
                print(f"⚠️ Không thể move_to_element: {e}")

            random_sleep(1, 2)

            try:
                job_cards = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h3.title a'))
                )
            except (NoSuchElementException, TimeoutException) as e:
                print(f"❌ Không tìm thấy job cards trên trang {page}: {e}")
                page += 1
                continue

            print(f"📌 Tìm thấy {len(job_cards)} job URLs trên trang {page}")
            for job_card in job_cards:
                job_url = job_card.get_attribute("href")
                if job_url and job_url not in job_urls:
                    job_urls.append(job_url)

            page += 1
            random_sleep(1, 2)

            # Tái khởi động trình duyệt sau mỗi 10 trang
            if page % 10 == 0:
                print("🔁 Đang khởi động lại trình duyệt để tránh crash...")
                driver.quit()
                driver = init_driver()
                wait = WebDriverWait(driver, 20)
                random_sleep(2, 3)

    except WebDriverException as e:
        print(f"❌ WebDriverException: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    # Lưu kết quả
    print(f"\n📦 Tổng số URL thu thập được: {len(job_urls)}")

    if job_urls:
        # Xác định đường dẫn file đầu ra
        if output_path is None:
            today = datetime.today().strftime("%Y-%m-%d")
            # Sử dụng đường dẫn tuyệt đối từ thư mục hiện tại
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            output_dir = os.path.join(parent_dir, "job_urls")
            output_path = os.path.join(output_dir, f"topcv_{today}.txt")

        # Lưu URLs vào file
        success = save_urls_to_file(job_urls, output_path)
        if success:
            print(f"✅ Đã lưu {len(job_urls)} URLs vào '{output_path}'")
        else:
            print(f"❌ Không thể lưu URLs vào '{output_path}'")
    else:
        print("⚠️ Không có URL nào được lưu.")

    return job_urls


if __name__ == "__main__":
    BASE_URL = "https://www.topcv.vn/tim-viec-lam-moi-nhat?type_keyword=0&sba=1"

    # Lấy đường dẫn tuyệt đối của thư mục hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Tạo đường dẫn đến thư mục job_urls (cùng cấp với thư mục scripts)
    parent_dir = os.path.dirname(current_dir)

    # Tạo tên file
    today = datetime.today().strftime("%Y-%m-%d")
    output_file = os.path.join(parent_dir, "job_urls", f"topcv_{today}.txt")

    # Crawl và lưu URLs
    crawl_urls(BASE_URL, max_pages=200, output_path=output_file)