import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Cấu hình trình duyệt
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL cụ thể
url = "https://www.topcv.vn/viec-lam/nhan-vien-tu-van-tuyen-sinh-education-consultant-thu-nhap-upto-20-trieu/1708433.html"
driver.get(url)

wait = WebDriverWait(driver, 10)

# Thu thập dữ liệu
title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-detail__info--title"))).text
salary = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(1) .job-detail__info--section-content-value").text
location = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(2) .job-detail__info--section-content-value").text
experience = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(3) .job-detail__info--section-content-value").text
deadline = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--deadline").text
company_name = driver.find_element(By.CSS_SELECTOR, ".company-name-label").text
job_description = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(1) .job-description__item--content").text
requirements = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(2) .job-description__item--content").text
tags = driver.find_elements(By.CSS_SELECTOR, ".box-category-tags > .box-category-tag")
career_tags = [tag.text for tag in tags]

driver.quit()

# Tạo đối tượng dữ liệu
job_data = {
    "url": url,
    "title": title,
    "salary": salary,
    "location": location,
    "experience": experience,
    "deadline": deadline,
    "company_name": company_name,
    "job_description": job_description,
    "requirements": requirements,
    "career_tags": career_tags
}

# Lưu vào file JSON
os.makedirs("raw_data", exist_ok=True)
job_id = url.split("/")[-1].split("?")[0].split(".")[0]  # Lấy ID job từ URL
file_path = os.path.join("raw_data", f"{job_id}.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(job_data, f, ensure_ascii=False, indent=2)

print(f"✅ Đã lưu dữ liệu vào {file_path}")
