from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Khởi tạo driver (sử dụng Chrome)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Mở trang việc làm TopCV
driver.get("https://www.topcv.vn/viec-lam")
wait = WebDriverWait(driver, 10)

# # Mở "Danh mục Nghề"
# danh_muc_nghe_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Danh mục Nghề')]")))
# danh_muc_nghe_btn.click()
# time.sleep(1)
#
# # Lấy danh sách các ngành nghề chính (bên trái)
# nganh_nghe_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'MuiGrid-root') and contains(text(),'')]/..//input[@type='checkbox']/following-sibling::span")
#
# # Duyệt từng ngành nghề
# for i in range(len(nganh_nghe_elements)):
#     try:
#         # Mở lại danh mục nếu bị đóng
#         danh_muc_nghe_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Danh mục Nghề')]")))
#         danh_muc_nghe_btn.click()
#         time.sleep(1)
#
#         # Refresh lại danh sách ngành nghề
#         nganh_nghe_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'MuiGrid-root') and contains(text(),'')]/..//input[@type='checkbox']/following-sibling::span")
#
#         # Click vào ngành nghề thứ i
#         nganh_nghe_elements[i].click()
#         time.sleep(0.5)
#
#         # Click nút "Chọn"
#         chon_btn = driver.find_element(By.XPATH, "//button[text()='Chọn']")
#         chon_btn.click()
#
#         # Đợi danh sách job tải xong
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "job-list")))
#
#         # Cuộn xuống vài lần để tải thêm kết quả (nếu có)
#         for _ in range(3):
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
#
#         # Lấy các URL tin tuyển dụng
#         job_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/viec-lam/') and not(contains(@href, 'ung-tuyen'))]")
#         urls = set([link.get_attribute("href") for link in job_links])
#
#         # Ghi ra file
#         with open("job_urls.txt", "a", encoding="utf-8") as f:
#             for url in urls:
#                 f.write(url + "\n")
#
#         print(f"✅ Ngành {i+1}/{len(nganh_nghe_elements)}: Lưu {len(urls)} job")
#
#     except Exception as e:
#         print(f"❌ Lỗi ở ngành {i+1}: {e}")
#         continue
#
# # Đóng trình duyệt
# driver.quit()
