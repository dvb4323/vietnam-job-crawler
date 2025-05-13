from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def handle_captcha(driver, page, max_retry=3):
    """
    Hàm xử lý CAPTCHA với phát hiện chính xác hơn để tránh cảnh báo sai

    Args:
        driver: WebDriver instance
        page: Số trang hiện tại
        max_retry: Số lần thử lại tối đa

    Returns:
        bool: True nếu CAPTCHA được xử lý thành công hoặc không có CAPTCHA, False nếu thất bại
    """
    # Danh sách các dấu hiệu CAPTCHA chính xác hơn
    primary_captcha_indicators = [
        # Google reCAPTCHA (chỉ phát hiện các phần tử chắc chắn)
        {"by": By.CSS_SELECTOR, "value": "iframe[src*='recaptcha/api2/anchor']"},
        {"by": By.CSS_SELECTOR, "value": "iframe[src*='recaptcha/api2/bframe']"},
        {"by": By.CSS_SELECTOR, "value": "div.g-recaptcha[data-sitekey]"},

        # hCaptcha (chỉ phát hiện khung iframe chính)
        {"by": By.CSS_SELECTOR, "value": "iframe[src*='hcaptcha.com/captcha']"},

        # CloudFlare protection rõ ràng
        {"by": By.CSS_SELECTOR, "value": "#cf-captcha-container"},
        {"by": By.CSS_SELECTOR, "value": "div.cf-captcha-container"},

        # Nút xác thực CAPTCHA cụ thể
        {"by": By.XPATH, "value": "//button[text()='Verify you are human' or text()='Xác minh bạn là người']"}
    ]

    # Kiểm tra các dấu hiệu CAPTCHA cụ thể
    captcha_detected = False
    captcha_element = None

    for indicator in primary_captcha_indicators:
        try:
            captcha_element = driver.find_element(indicator["by"], indicator["value"])
            if captcha_element.is_displayed():
                captcha_detected = True
                print(f"🚨 CAPTCHA phát hiện trên trang {page} (dấu hiệu: {indicator['value']})")
                break
        except NoSuchElementException:
            continue

    # Nếu không tìm thấy qua các chỉ báo chính, kiểm tra thêm các đặc điểm phổ biến
    # nhưng chỉ khi có dấu hiệu rõ ràng về CAPTCHA
    if not captcha_detected:
        page_text = driver.page_source.lower()

        # Kiểm tra các khung tương tác của captcha
        captcha_frames = driver.find_elements(By.TAG_NAME, "iframe")
        captcha_frame_detected = False

        for frame in captcha_frames:
            src = frame.get_attribute("src") or ""
            if ("recaptcha" in src or "hcaptcha" in src or "captcha" in src) and frame.is_displayed():
                captcha_frame_detected = True
                break

        # Chỉ khi có iframe CAPTCHA hiển thị hoặc có chứa cụm từ xác minh rõ ràng
        # mới xác định là có CAPTCHA
        specific_captcha_keywords = [
            'please complete the security check',
            'please verify you are a human',
            'i am not a robot',
            'captcha challenge',
            'security verification',
            'xác minh bạn không phải là robot',
            'xác minh bạn là người dùng',
            'vui lòng hoàn thành quá trình xác thực'
        ]

        if captcha_frame_detected or any(keyword in page_text for keyword in specific_captcha_keywords):
            captcha_detected = True
            print(f"🚨 CAPTCHA có thể được phát hiện qua nội dung trang {page}")

    # Nếu không phát hiện CAPTCHA, trả về thành công
    if not captcha_detected:
        return True

    # Nếu có CAPTCHA, thử từng cách khác nhau để xử lý
    retry_count = 0

    while retry_count < max_retry:
        # Tạm dừng để người dùng xử lý thủ công
        try:
            # Cố gắng chuyển sang khung iframe nếu có
            captcha_frames = []
            try:
                # Tìm các iframe có thể chứa CAPTCHA
                frames = driver.find_elements(By.TAG_NAME, "iframe")
                for frame in frames:
                    src = frame.get_attribute("src") or ""
                    if ("recaptcha" in src or "hcaptcha" in src or "captcha" in src) and frame.is_displayed():
                        captcha_frames.append(frame)
            except:
                pass

            # Nếu tìm thấy iframe CAPTCHA, chuyển đến iframe đầu tiên
            if captcha_frames:
                try:
                    driver.switch_to.frame(captcha_frames[0])
                    print("🔍 Đã chuyển đến iframe CAPTCHA")
                except:
                    driver.switch_to.default_content()
                    print("⚠️ Không thể chuyển đến iframe CAPTCHA")
            else:
                print("ℹ️ Không tìm thấy iframe CAPTCHA, xử lý trên trang chính")

            print(f"🔓 Vui lòng xử lý CAPTCHA thủ công (lần thử {retry_count + 1}/{max_retry})")
            print("⏸️ Sau khi hoàn thành, hãy nhấn Enter để tiếp tục...")
            input()

            # Chuyển về khung chính
            driver.switch_to.default_content()

            # Chờ một chút để trang cập nhật sau khi xử lý CAPTCHA
            time.sleep(3)

            # Xác minh CAPTCHA đã được xử lý bằng cách kiểm tra lại
            captcha_still_exists = False

            for indicator in primary_captcha_indicators:
                try:
                    element = driver.find_element(indicator["by"], indicator["value"])
                    if element.is_displayed():
                        captcha_still_exists = True
                        break
                except NoSuchElementException:
                    continue

            if not captcha_still_exists:
                print("✅ CAPTCHA đã được xử lý thành công!")
                return True

            # Kiểm tra xem trang có thay đổi không bằng cách xem URL
            # Một số trang sẽ chuyển hướng sau khi xử lý CAPTCHA
            current_url = driver.current_url
            if "captcha" not in current_url.lower() and "challenge" not in current_url.lower():
                print("✅ Trang đã được chuyển hướng, có vẻ CAPTCHA đã được xử lý!")
                return True

        except Exception as e:
            print(f"⚠️ Lỗi khi xử lý CAPTCHA: {e}")

        retry_count += 1

    print("❌ Đã hết số lần thử xử lý CAPTCHA")
    return False


# Hàm xử lý captcha rút gọn chỉ phát hiện các loại CAPTCHA phổ biến
def detect_captcha(driver):
    """
    Hàm chỉ dùng để phát hiện CAPTCHA, không xử lý
    Sử dụng phương pháp phát hiện chính xác hơn để tránh cảnh báo sai

    Args:
        driver: WebDriver instance

    Returns:
        bool: True nếu phát hiện CAPTCHA, False nếu không
    """
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException

    # Danh sách các dấu hiệu CAPTCHA chắc chắn
    captcha_selectors = [
        # Google reCAPTCHA
        ("css", "iframe[src*='recaptcha/api2/anchor']"),
        ("css", "iframe[src*='recaptcha/api2/bframe']"),
        ("css", "div.g-recaptcha[data-sitekey]"),

        # hCaptcha
        ("css", "iframe[src*='hcaptcha.com/captcha']"),

        # CloudFlare
        ("css", "#cf-captcha-container"),

        # Text rõ ràng về CAPTCHA
        ("xpath", "//div[contains(text(), 'I am not a robot') and not(ancestor::script)]"),
        ("xpath", "//div[contains(text(), 'Tôi không phải là robot') and not(ancestor::script)]"),
        ("xpath", "//button[text()='Verify you are human' or text()='Xác minh bạn là người']")
    ]

    # Kiểm tra các selector CAPTCHA
    for selector_type, selector in captcha_selectors:
        try:
            if selector_type == "css":
                element = driver.find_element(By.CSS_SELECTOR, selector)
            else:
                element = driver.find_element(By.XPATH, selector)

            if element.is_displayed():
                return True
        except NoSuchElementException:
            continue

    # Kiểm tra iframe CAPTCHA
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for frame in frames:
        src = frame.get_attribute("src") or ""
        if src and ("recaptcha" in src or "hcaptcha" in src) and "api2" in src and frame.is_displayed():
            return True

    return False


# Ví dụ sử dụng hàm detect_captcha
def check_for_captcha(driver, page_identifier, wait_after_solve=10):
    """
    Hàm kiểm tra CAPTCHA trên trang và xử lý nếu cần

    Args:
        driver: WebDriver instance
        page_identifier: Định danh trang (dùng cho log)
        wait_after_solve: Số giây chờ sau khi giải captcha (mặc định 10s)

    Returns:
        bool: True nếu trang không có CAPTCHA hoặc đã xử lý thành công, False nếu không xử lý được
    """
    if detect_captcha(driver):
        print(f"🚨 Phát hiện CAPTCHA trên {page_identifier}")

        # Lưu URL hiện tại trước khi xử lý captcha
        current_url = driver.current_url

        # Xử lý captcha
        if handle_captcha(driver, page_identifier):
            # Đợi thêm thời gian sau khi giải captcha
            print(f"⏳ Đợi {wait_after_solve}s sau khi giải captcha...")
            time.sleep(wait_after_solve)

            # Kiểm tra xem URL có thay đổi không
            if driver.current_url != current_url:
                print(f"⚠️ URL đã thay đổi sau khi giải captcha: {driver.current_url}")
                # Quay lại URL ban đầu
                print(f"🔙 Quay lại URL ban đầu: {current_url}")
                driver.get(current_url)
                time.sleep(3)  # Đợi trang tải lại

                # Kiểm tra lại captcha sau khi quay lại
                if detect_captcha(driver):
                    print("🚨 Vẫn còn CAPTCHA sau khi quay lại URL ban đầu")
                    return False

            return True
        return False
    return True

# Sử dụng trong vòng lặp crawl
# while page <= max_pages:
#     url = f"{base_url}&page={page}"
#     driver.get(url)
#
#     # Kiểm tra và xử lý CAPTCHA
#     if not check_for_captcha(driver, page):
#         print(f"⚠️ Không thể xử lý CAPTCHA trên trang {page}, thử trang tiếp theo")
#         page += 1
#         continue
#
#     # Tiếp tục crawl trang...