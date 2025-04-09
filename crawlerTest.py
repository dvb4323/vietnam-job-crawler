from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.topcv.vn/viec-lam/nhan-vien-kinh-doanh-sales-tu-van-noi-that-thu-nhap-upto-30-trieu-thang/1651788.html")

# Đợi tiêu đề hiển thị
wait = WebDriverWait(driver, 10)

# Thu thập thông tin
title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-detail__info--title"))).text
salary = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(1) .job-detail__info--section-content-value").text
location = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(2) .job-detail__info--section-content-value").text
experience = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(3) .job-detail__info--section-content-value").text
deadline = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--deadline").text
#
company_name = driver.find_element(By.CSS_SELECTOR, ".company-name-label").text

job_description = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(1) .job-description__item--content").text
requirements = driver.find_element(By.CSS_SELECTOR, ".job-description__item:nth-child(2) .job-description__item--content").text

# Danh sách ngành nghề liên quan
tags = driver.find_elements(By.CSS_SELECTOR, ".box-category-tags > .box-category-tag")
career_tags = [tag.text for tag in tags]

# In kết quả
print("Tiêu đề:", title)
print("Lương:", salary)
print("Địa điểm:", location)
print("Kinh nghiệm:", experience)
print("Hạn nộp:", deadline)
print("Công ty:", company_name)

print("Mô tả công việc:\n", job_description)
print("Yêu cầu ứng viên:\n", requirements)
print("Ngành nghề liên quan:", career_tags)

driver.quit()
