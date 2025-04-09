from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.topcv.vn/viec-lam/nhan-vien-kinh-doanh-sales-tu-van-noi-that-thu-nhap-upto-30-trieu-thang/1651788.html")

# Đợi tiêu đề hiển thị
wait = WebDriverWait(driver, 10)
title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".job-detail__info--title"))).text

# Thu thập thông tin
title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.job-detail__info--title"))).text
salary = driver.find_element(By.CSS_SELECTOR, ".job-detail__info--section:nth-child(1) .job-detail__info--section-content-value").text
location = driver.find_element(By.XPATH, ".job-detail__info--section:nth-child(2) .job-detail__info--section-content-value").text
# experience = driver.find_element(By.XPATH, "//div[@class='box-main']//div[contains(text(), 'Kinh nghiệm')]/following-sibling::strong").text
# deadline = driver.find_element(By.XPATH, "//div[@class='box-main']//div[contains(text(), 'Hạn nộp hồ sơ')]/following-sibling::strong").text
#
# company_name = driver.find_element(By.CSS_SELECTOR, ".box-company h3").text
# industry = driver.find_element(By.XPATH, "//div[contains(text(), 'Lĩnh vực')]/following-sibling::div").text
# work_type = driver.find_element(By.XPATH, "//div[contains(text(), 'Hình thức làm việc')]/following-sibling::div").text
# education = driver.find_element(By.XPATH, "//div[contains(text(), 'Học vấn')]/following-sibling::div").text
# position = driver.find_element(By.XPATH, "//div[contains(text(), 'Cấp bậc')]/following-sibling::div").text
# num_hiring = driver.find_element(By.XPATH, "//div[contains(text(), 'Số lượng tuyển')]/following-sibling::div").text
#
# job_description = driver.find_element(By.XPATH, "//h3[contains(text(), 'Mô tả công việc')]/following-sibling::div").text
# requirements = driver.find_element(By.XPATH, "//h3[contains(text(), 'Yêu cầu ứng viên')]/following-sibling::div").text

# Danh sách ngành nghề liên quan
# tags = driver.find_elements(By.CSS_SELECTOR, ".box-related-career .tag")
# career_tags = [tag.text for tag in tags]

# In kết quả
print("Tiêu đề:", title)
print("Lương:", salary)
# print("Địa điểm:", location)
# print("Kinh nghiệm:", experience)
# print("Hạn nộp:", deadline)
# print("Công ty:", company_name)
# print("Ngành nghề:", industry)
# print("Hình thức:", work_type)
# print("Học vấn:", education)
# print("Cấp bậc:", position)
# print("Số lượng:", num_hiring)
# print("Mô tả công việc:\n", job_description)
# print("Yêu cầu ứng viên:\n", requirements)
# print("Ngành nghề liên quan:", career_tags)

driver.quit()
