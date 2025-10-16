import requests
from bs4 import BeautifulSoup
import time

def get_defaced_domains_from_page(page_number):
    """
    Trích xuất các domain bị deface từ một trang cụ thể của Zone-H.
    """
    # URL của trang lưu trữ, page=X để chuyển trang
    url = f"https://zone-h.org/archive/page={page_number}"
    domains = []
    
    try:
        # Gửi yêu cầu với User-Agent để giả lập trình duyệt
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Báo lỗi nếu request không thành công

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các hàng <tr> trong bảng, bỏ qua hàng tiêu đề đầu tiên
        # Dựa trên cấu trúc HTML của Zone-H, các hàng dữ liệu không có thuộc tính 'class'
        table_rows = soup.find_all('tr', onmouseover=True)
        
        for row in table_rows:
            # Các ô dữ liệu trong hàng là <td>
            cells = row.find_all('td')
            if len(cells) > 3:
                # Domain nằm ở ô thứ 4 (index 3) và chứa một thẻ <a>
                domain_cell = cells[3]
                domain_text = domain_cell.get_text(strip=True)
                
                # Làm sạch domain, loại bỏ phần "..." và các ký tự không mong muốn
                if '...' in domain_text:
                    full_domain_link = domain_cell.find('a')
                    if full_domain_link and 'title' in full_domain_link.attrs:
                        domain_text = full_domain_link['title']
                
                # Thêm http:// để tạo thành URL hoàn chỉnh
                full_url = f"http://{domain_text}"
                domains.append(full_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập trang {page_number}: {e}")
        
    return domains

# --- CHẠY CÔNG CỤ ---
if __name__ == "__main__":
    all_defaced_urls = []
    # Ví dụ: lấy dữ liệu từ 5 trang đầu tiên
    for page in range(1, 6): 
        print(f"Đang quét trang {page}...")
        urls_on_page = get_defaced_domains_from_page(page)
        if not urls_on_page:
            print(f"Không tìm thấy dữ liệu hoặc đã hết trang.")
            break
        
        all_defaced_urls.extend(urls_on_page)
        
        # Thêm độ trễ 1-2 giây giữa các lần request để tránh bị chặn
        time.sleep(1.5)

    # Lưu kết quả vào file
    with open('defaced_urls.txt', 'w') as f:
        for url in all_defaced_urls:
            f.write(f"{url}\n")
            
    print(f"\n🎉 Hoàn tất! Đã trích xuất và lưu {len(all_defaced_urls)} URL vào file defaced_urls.txt")