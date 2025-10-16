from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
# XÓA DÒNG NÀY: from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# ... (Hàm get_domain_from_mirror_id không thay đổi) ...
def get_domain_from_mirror_id(mirror_id, driver):
    url = f"https://www.zone-h.org/mirror/id/{mirror_id}"
    try:
        driver.get(url)
        time.sleep(2)
        page_source = driver.page_source
        if "record not found" in page_source:
            return "ID không tồn tại"
        soup = BeautifulSoup(page_source, 'html.parser')
        domain_strong_tag = soup.find('strong', string='Domain:')
        if domain_strong_tag:
            domain = domain_strong_tag.next_sibling
            if domain and domain.strip():
                return domain.strip()
        return "Không tìm thấy domain trong HTML"
    except Exception as e:
        return f"Đã xảy ra lỗi: {e}"


# --- CHƯƠG TRÌNH CHÍNH ---
if __name__ == "__main__":
    test_ids = [
        '41468682',
        '41470554',
        '41470553',
        '41471125'
    ]
    
    print("🚀 Bắt đầu kiểm tra với Selenium...")

    # --- PHẦN THAY ĐỔI QUAN TRỌNG ---
    # Selenium sẽ tự động tải và quản lý driver phù hợp
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    
    # KHỞI TẠO TRÌNH DUYỆT ĐƠN GIẢN HƠN
    driver = webdriver.Chrome(options=options)
    # --------------------------------

    try:
        for i, mid in enumerate(list(set(test_ids))):
            print(f"\n[{i+1}/{len(set(test_ids))}] Đang kiểm tra ID: {mid}")
            result = get_domain_from_mirror_id(mid, driver)
            if not result.startswith(("ID không", "Không tìm", "Đã xảy")):
                result = f"http://{result}"
            print(f"  -> Kết quả: {result}")
    finally:
        driver.quit()

    print("\n🎉 Hoàn tất kiểm tra!")