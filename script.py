import requests
from bs4 import BeautifulSoup
import os
import re

def clean_filename(url):
    """Tạo tên file an toàn từ URL."""
    # Loại bỏ scheme (http, https)
    if url.startswith(('http://', 'https://')):
        url = url[url.find('//')+2:]
    
    # Thay thế các ký tự không hợp lệ bằng dấu gạch dưới
    return re.sub(r'[\\/*?:"<>|]', "_", url)

def extract_text_from_url(url, session):
    """
    Tải HTML từ một URL, trích xuất và trả về nội dung văn bản thuần.
    """
    try:
        # Sử dụng headers để giả lập một trình duyệt thông thường
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Tải trang web với timeout là 15 giây
        response = session.get(url, timeout=15, headers=headers)
        # Báo lỗi nếu yêu cầu không thành công
        response.raise_for_status()

        # Sử dụng BeautifulSoup để phân tích HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Loại bỏ các thẻ <script> và <style> vì chúng chứa mã, không phải nội dung 
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Lấy văn bản từ nội dung còn lại
        text = soup.get_text()

        # Dọn dẹp văn bản: loại bỏ dòng trống và khoảng trắng thừa
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        return cleaned_text

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Lỗi khi xử lý URL {url}: {e}")
        return None

def process_url_list(input_file, output_dir):
    """
    Đọc danh sách URL từ file, trích xuất văn bản và lưu vào thư mục đầu ra.
    """
    print(f"\n🚀 Bắt đầu xử lý file: {input_file}")
    
    # Tạo thư mục đầu ra nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Đã tạo thư mục: {output_dir}")

    # Đọc danh sách URLs từ file
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file '{input_file}'. Vui lòng kiểm tra lại đường dẫn.")
        return

    if not urls:
        print("File URL trống, không có gì để xử lý.")
        return

    # Sử dụng session để tái sử dụng kết nối, tăng hiệu suất
    with requests.Session() as session:
        for i, url in enumerate(urls):
            print(f"   ({i+1}/{len(urls)}) Đang lấy dữ liệu từ: {url}")
            
            # Trích xuất văn bản
            plain_text = extract_text_from_url(url, session)

            if plain_text:
                # Tạo tên file từ URL và lưu kết quả
                file_name = f"{clean_filename(url)}.txt"
                output_path = os.path.join(output_dir, file_name)
                
                try:
                    with open(output_path, 'w', encoding='utf-8') as out_file:
                        out_file.write(plain_text)
                    # print(f"      ✅ Đã lưu thành công vào: {output_path}")
                except Exception as e:
                    print(f"      ❌ Lỗi khi lưu file {output_path}: {e}")

    print(f"🎉 Hoàn tất xử lý {len(urls)} URLs từ {input_file}.")

# --- CẤU HÌNH VÀ CHẠY ---
if __name__ == "__main__":
    # 1. Dữ liệu cho các trang web bình thường
    NORMAL_URLS_FILE = 'normal_urls.txt'
    NORMAL_OUTPUT_DIR = 'data/normal_text'
    process_url_list(NORMAL_URLS_FILE, NORMAL_OUTPUT_DIR)

    # 2. Dữ liệu cho các trang web bị thay đổi giao diện
    DEFACED_URLS_FILE = 'defaced_urls.txt'
    DEFACED_OUTPUT_DIR = 'data/defaced_text'
    process_url_list(DEFACED_URLS_FILE, DEFACED_OUTPUT_DIR)