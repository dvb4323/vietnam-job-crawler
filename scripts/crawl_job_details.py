import os
import json
import time
import random
from tqdm import tqdm
from multiprocessing import Process, current_process
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import undetected_chromedriver as uc
# import undetected_chromedriver.patcher

# === Project base path ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
URL_LIST_PATH = os.path.join(BASE_DIR, "job_urls", "topcv_2025-05-08.txt")
DATA_DIR = os.path.join(BASE_DIR, "raw_data")
LOG_FILE = os.path.join(BASE_DIR, "crawled_jobs.txt")
os.makedirs(DATA_DIR, exist_ok=True)

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
    # options = uc.ChromeOptions()
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={random.randint(1024, 1600)},{random.randint(700, 900)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=vi-VN")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(executable_path="C:/driver/undetected_chromedriver.exe")  # ← dùng bản patch sẵn
    driver = webdriver.Chrome(service=service, options=options)
    # driver = uc.Chrome(options=options)
    return driver

def simulate_user_behavior(driver):
    scroll_times = random.randint(2, 5)
    for _ in range(scroll_times):
        driver.execute_script(f"window.scrollBy(0, {random.randint(100, 500)});")
        time.sleep(random.uniform(0.5, 1.2))
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(5, 50), random.randint(5, 50)).perform()
    time.sleep(random.uniform(0.5, 1))

def crawl_job(url):
    driver = get_driver()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(url)
        simulate_user_behavior(driver)
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-detail__info--title"))).text
        salary = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(1) .job-detail__info--section-content-value").text
        location = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(2) .job-detail__info--section-content-value").text
        experience = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(3) .job-detail__info--section-content-value").text
        company_name = driver.find_element(By.CSS_SELECTOR, ".company-name-label").text
        job_description = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(1) .job-description__item--content").text
        requirements = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(2) .job-description__item--content").text
        tags = driver.find_elements(By.CSS_SELECTOR, ".box-category-tags > .box-category-tag")
        career_tags = [tag.text for tag in tags]
        job_data = {
            "url": url,
            "title": title,
            "salary": salary,
            "location": location,
            "experience": experience,
            "company_name": company_name,
            "job_description": job_description,
            "requirements": requirements,
            "career_tags": career_tags
        }
        return job_data
    except Exception as e:
        print(f"❌ {current_process().name} lỗi với URL {url}: {e}")
        return None
    finally:
        driver.quit()

def crawl_range(start, end, proc_id):
    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
        for url in tqdm(job_urls[start:end], desc=f"🔄 Process {proc_id}"):
            job_id = url.split("/")[-1].split("?")[0].split(".")[0]
            if job_id in crawled_ids:
                continue
            file_path = os.path.join(DATA_DIR, f"{job_id}.json")
            if os.path.exists(file_path):
                continue
            job_data = crawl_job(url)
            if job_data:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(job_data, f, ensure_ascii=False, indent=2)
                log_f.write(f"{job_id}\n")
                log_f.flush()
                tqdm.write(f"✅ Process {proc_id}: Đã lưu job {job_id}")
            else:
                tqdm.write(f"⚠️ Process {proc_id}: Bỏ qua job {job_id} do lỗi.")
            time.sleep(random.uniform(3.5, 7.5))

if __name__ == "__main__":
    num_processes = 4
    chunk_size = len(job_urls) // num_processes
    # Patch driver một lần duy nhất
    import undetected_chromedriver.patcher

    _ = undetected_chromedriver.patcher.Patcher().executable_path
    processes = []
    for i in range(num_processes):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != num_processes - 1 else len(job_urls)
        p = Process(target=crawl_range, args=(start, end, i))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
