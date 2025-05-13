import os
import json
import time
import random
from captcha_handle import check_for_captcha
from tqdm import tqdm
from multiprocessing import Process, current_process
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === Project base path ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL_LIST_PATH = os.path.join(BASE_DIR, "job_urls", "topcv_2025-05-08.txt")
DATA_DIR = os.path.join(BASE_DIR, "raw_data")
LOG_FILE = os.path.join(BASE_DIR, "crawled_jobs.txt")
ERROR_LOG_FILE = os.path.join(BASE_DIR, "error_jobs.txt")  # Thêm file log lỗi riêng
COOKIES_DIR = os.path.join(BASE_DIR, "cookies")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(COOKIES_DIR, exist_ok=True)

# === Read URLs ===
with open(URL_LIST_PATH, "r", encoding="utf-8") as f:
    job_urls = [line.strip() for line in f.readlines()]

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        crawled_ids = set(line.strip() for line in f)
else:
    crawled_ids = set()


# === WebDriver config ===
def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={random.randint(1024, 1600)},{random.randint(700, 900)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=vi-VN")

    # Thêm các tùy chọn để tránh phát hiện bot từ Cloudflare
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")

    # Thêm tùy chọn để ngăn tự động chuyển hướng
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.automatic_downloads": 1
    })

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(executable_path="C:/driver/undetected_chromedriver.exe")  # ← dùng bản patch sẵn
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def simulate_user_behavior(driver):
    """Mô phỏng hành vi người dùng để tránh phát hiện bot"""
    # Lướt trang với tốc độ ngẫu nhiên
    scroll_times = random.randint(2, 5)
    for _ in range(scroll_times):
        scroll_amount = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.2))

    # Di chuyển chuột
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(5, 50), random.randint(5, 50)).perform()
    time.sleep(random.uniform(0.5, 1))

    # Thêm một số hành vi người dùng ngẫu nhiên
    if random.random() < 0.3:  # 30% khả năng
        # Lướt lên đầu trang
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(0.5, 1))

    if random.random() < 0.2:  # 20% khả năng
        # Di chuyển đến một phần tử ngẫu nhiên
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "h2, h3, p, div.box")
            if elements:
                element = random.choice(elements)
                actions = ActionChains(driver)
                actions.move_to_element(element).perform()
                time.sleep(random.uniform(0.3, 0.7))
        except:
            pass


def load_cookies(driver, proc_id):
    """Tải cookies nếu có sẵn"""
    cookies_file = os.path.join(COOKIES_DIR, f"process_{proc_id}_cookies.json")
    if os.path.exists(cookies_file):
        try:
            # Truy cập trang chủ trước khi thêm cookies
            driver.get("https://www.topcv.vn")
            time.sleep(2)

            with open(cookies_file, "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        pass
            return True
        except Exception as e:
            print(f"⚠️ Process {proc_id}: Lỗi khi tải cookies: {e}")
    return False


def save_cookies(driver, proc_id):
    """Lưu cookies để sử dụng sau"""
    cookies_file = os.path.join(COOKIES_DIR, f"process_{proc_id}_cookies.json")
    try:
        cookies = driver.get_cookies()
        with open(cookies_file, "w") as f:
            json.dump(cookies, f)
        return True
    except Exception as e:
        print(f"⚠️ Process {proc_id}: Lỗi khi lưu cookies: {e}")
    return False


def log_error(proc_id, url, error_message):
    """Ghi lỗi vào file log riêng với đầy đủ thông tin"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Process {proc_id}: {url} - {error_message}\n")
    except Exception as e:
        print(f"❌ Không thể ghi log lỗi: {e}")


def crawl_range(start, end, proc_id):
    """Crawl một dải các URLs được phân công"""
    driver = None  # Khởi tạo driver ở cấp cao hơn để tái sử dụng
    captcha_count = 0  # Đếm số lần gặp CAPTCHA

    try:
        driver = get_driver()  # Khởi tạo driver
        wait = WebDriverWait(driver, 10)

        # Tải cookies nếu có
        load_cookies(driver, proc_id)

        with open(LOG_FILE, "a", encoding="utf-8") as log_f:
            for index, url in enumerate(tqdm(job_urls[start:end], desc=f"🔄 Process {proc_id}")):
                job_id = url.split("/")[-1].split("?")[0].split(".")[0]

                # URL ngắn để hiển thị trong log (tối đa 40 ký tự)
                short_url = url if len(url) <= 40 else f"{url[:37]}..."

                # Kiểm tra nếu đã crawl
                if job_id in crawled_ids:
                    continue

                # Kiểm tra nếu file đã tồn tại
                file_path = os.path.join(DATA_DIR, f"{job_id}.json")
                if os.path.exists(file_path):
                    continue

                try:
                    # Truy cập URL
                    driver.get(url)
                    original_url = driver.current_url  # Lưu URL gốc
                    time.sleep(random.uniform(2, 3))  # Đợi trang tải

                    # Kiểm tra CAPTCHA
                    if not check_for_captcha(driver, f"process-{proc_id}-job-{job_id}", wait_after_solve=15):
                        captcha_count += 1
                        error_msg = f"Không thể xử lý CAPTCHA cho job {job_id}"
                        tqdm.write(f"⚠️ Process {proc_id}: {error_msg} - URL: {url}")
                        log_error(proc_id, url, error_msg)
                        continue  # Bỏ qua job này và chuyển sang job tiếp theo

                    # Kiểm tra xem URL có thay đổi không sau khi xử lý captcha
                    if driver.current_url != original_url and "cloudflare" not in driver.current_url:
                        tqdm.write(
                            f"⚠️ Process {proc_id}: URL đã thay đổi sau khi xử lý CAPTCHA. Đang quay lại URL gốc...")
                        driver.get(url)
                        time.sleep(5)  # Đợi lâu hơn để trang tải

                    # Kiểm tra CAPTCHA
                    if not check_for_captcha(driver, f"process-{proc_id}-job-{job_id}"):
                        captcha_count += 1
                        error_msg = f"Không thể xử lý CAPTCHA cho job {job_id}"
                        tqdm.write(f"⚠️ Process {proc_id}: {error_msg} - URL: {url}")
                        log_error(proc_id, url, error_msg)

                        # Nếu gặp nhiều CAPTCHA liên tiếp, khởi động lại driver
                        if captcha_count >= 2:
                            restart_msg = f"Khởi động lại driver sau {captcha_count} lần gặp CAPTCHA"
                            tqdm.write(f"🔄 Process {proc_id}: {restart_msg}")
                            # Lưu cookies trước khi khởi động lại
                            save_cookies(driver, proc_id)
                            driver.quit()
                            time.sleep(random.uniform(10, 15))  # Đợi lâu hơn trước khi khởi động lại
                            driver = get_driver()
                            wait = WebDriverWait(driver, 10)
                            load_cookies(driver, proc_id)  # Tải lại cookies
                            captcha_count = 0  # Reset bộ đếm

                        continue  # Bỏ qua job này và chuyển sang job tiếp theo

                    captcha_count = 0  # Reset bộ đếm nếu không gặp CAPTCHA

                    # Mô phỏng hành vi người dùng
                    simulate_user_behavior(driver)

                    # Lấy dữ liệu từ trang
                    try:
                        # Sử dụng try-except cho từng phần tử để không bị lỗi toàn bộ job nếu 1 phần bị thiếu
                        job_data = {"url": url}

                        try:
                            title = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-detail__info--title"))).text
                            job_data["title"] = title
                        except Exception as e:
                            error_msg = f"Không lấy được tiêu đề job - lỗi: {str(e)}"
                            tqdm.write(f"⚠️ Process {proc_id}: {error_msg} - URL: {url}")
                            log_error(proc_id, url, error_msg)
                            job_data["title"] = ""

                        try:
                            salary = driver.find_element(By.CSS_SELECTOR,
                                                         ".job-detail__info--section:nth-child(1) .job-detail__info--section-content-value").text
                            job_data["salary"] = salary
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được salary - lỗi: {str(e)}")
                            job_data["salary"] = "Không công bố"

                        try:
                            location = driver.find_element(By.CSS_SELECTOR,
                                                           ".job-detail__info--section:nth-child(2) .job-detail__info--section-content-value").text
                            job_data["location"] = location
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được location - lỗi: {str(e)}")
                            job_data["location"] = ""

                        try:
                            experience = driver.find_element(By.CSS_SELECTOR,
                                                             ".job-detail__info--section:nth-child(3) .job-detail__info--section-content-value").text
                            job_data["experience"] = experience
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được experience - lỗi: {str(e)}")
                            job_data["experience"] = ""

                        try:
                            company_name = driver.find_element(By.CSS_SELECTOR, ".company-name-label").text
                            job_data["company_name"] = company_name
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được company_name - lỗi: {str(e)}")
                            job_data["company_name"] = ""

                        try:
                            job_description = driver.find_element(By.CSS_SELECTOR,
                                                                  ".job-description__item:nth-child(1) .job-description__item--content").text
                            job_data["job_description"] = job_description
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được job_description - lỗi: {str(e)}")
                            job_data["job_description"] = ""

                        try:
                            requirements = driver.find_element(By.CSS_SELECTOR,
                                                               ".job-description__item:nth-child(2) .job-description__item--content").text
                            job_data["requirements"] = requirements
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được requirements - lỗi: {str(e)}")
                            job_data["requirements"] = ""

                        try:
                            tags = driver.find_elements(By.CSS_SELECTOR, ".box-category-tags > .box-category-tag")
                            career_tags = [tag.text for tag in tags]
                            job_data["career_tags"] = career_tags
                        except Exception as e:
                            log_error(proc_id, url, f"Không lấy được career_tags - lỗi: {str(e)}")
                            job_data["career_tags"] = []

                        # Thêm timestamp
                        job_data["crawled_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

                        # Kiểm tra xem có đủ dữ liệu cần thiết không
                        required_fields = ["title", "company_name", "job_description"]
                        missing_fields = [field for field in required_fields if not job_data.get(field)]

                        if missing_fields:
                            error_msg = f"Thiếu các trường quan trọng: {', '.join(missing_fields)}"
                            tqdm.write(f"⚠️ Process {proc_id}: {error_msg} - URL: {url}")
                            log_error(proc_id, url, error_msg)
                            # Vẫn lưu dữ liệu bất kể thiếu

                        # Lưu dữ liệu vào file
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(job_data, f, ensure_ascii=False, indent=2)

                        # Ghi log
                        log_f.write(f"{job_id}\n")
                        log_f.flush()

                        # Hiển thị thông báo thành công với URL đầy đủ
                        tqdm.write(f"✅ Process {proc_id}: Đã lưu job {job_id} - URL: {url}")

                    except Exception as e:
                        error_msg = f"Lỗi khi crawl job: {str(e)}"
                        tqdm.write(f"❌ Process {proc_id}: {error_msg} - URL: {url}")
                        log_error(proc_id, url, error_msg)

                except Exception as e:
                    error_msg = f"Lỗi truy cập URL: {str(e)}"
                    tqdm.write(f"❌ Process {proc_id}: {error_msg} - URL: {url}")
                    log_error(proc_id, url, error_msg)

                # Đợi một khoảng thời gian ngẫu nhiên trước khi tiếp tục
                time.sleep(random.uniform(3.5, 7.5))

                # Lưu cookies định kỳ
                if (index + 1) % 10 == 0:
                    save_cookies(driver, proc_id)

                # Khởi động lại driver sau một số lần nhất định
                if (index + 1) % 20 == 0:
                    tqdm.write(f"🔄 Process {proc_id}: Khởi động lại driver sau 20 jobs")
                    save_cookies(driver, proc_id)  # Lưu cookies trước khi khởi động lại
                    driver.quit()
                    time.sleep(random.uniform(5, 10))
                    driver = get_driver()
                    wait = WebDriverWait(driver, 10)
                    load_cookies(driver, proc_id)  # Tải lại cookies

    except Exception as e:
        error_msg = f"Process gặp lỗi nghiêm trọng: {str(e)}"
        print(f"❌ Process {proc_id}: {error_msg}")
        log_error(proc_id, "global_error", error_msg)
    finally:
        if driver:
            # Lưu cookies trước khi thoát
            save_cookies(driver, proc_id)
            driver.quit()


if __name__ == "__main__":
    # Hiển thị thông tin
    print(f"📊 Tổng số URLs cần crawl: {len(job_urls)}")
    print(f"📊 Đã crawl trước đó: {len(crawled_ids)}")
    print(f"📊 Còn lại: {len(job_urls) - len(crawled_ids)}")

    # Khởi tạo log file lỗi nếu chưa tồn tại
    if not os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Bắt đầu log lỗi\n")

    # Tùy chỉnh số lượng processes
    num_processes = 4  # Có thể điều chỉnh dựa trên cấu hình máy
    chunk_size = len(job_urls) // num_processes

    # Khởi tạo các processes
    processes = []

    # Tạo và khởi động từng process
    for i in range(num_processes):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != num_processes - 1 else len(job_urls)
        p = Process(target=crawl_range, args=(start, end, i))
        processes.append(p)
        p.start()
        time.sleep(2)  # Đợi một chút giữa các process để tránh quá tải

    # Đợi tất cả các processes hoàn thành
    for p in processes:
        p.join()

    print("✅ Hoàn thành crawl tất cả job URLs!")