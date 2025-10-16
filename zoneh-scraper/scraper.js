// scraper.js
const puppeteer = require('puppeteer');
const fs = require('fs');

async function getAndSaveDefacedUrl() {
    // headless true là đủ (khỏi "new")
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    try {
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        );

        const url = 'https://www.zone-h.org/mirror/id/41471125';
        console.log(`Đang truy cập vào trang: ${url}`);

        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        // Chờ item chứa phần "Domain:" – linh hoạt: .defaces hoặc class có chữ deface
        await page.waitForSelector('li.defaces, li[class*=deface]', { timeout: 15000 });

        // Lấy text từ các <li> rồi bóc riêng URL sau "Domain:"
        const extractedText = await page.evaluate(() => {
            // Ưu tiên: <strong>Domain:</strong><text-sau-đó>
            const nodes = Array.from(document.querySelectorAll('li.defaces, li[class*="deface"]'));
            for (const li of nodes) {
                const strong = li.querySelector('strong');
                if (strong && /Domain:?/i.test(strong.textContent)) {
                    // gom text sau <strong>Domain:</strong>
                    let acc = '';
                    for (let n = strong.nextSibling; n; n = n.nextSibling) {
                        if (n.nodeType === Node.TEXT_NODE) acc += n.nodeValue;
                        else if (n.nodeType === Node.ELEMENT_NODE) acc += ' ' + n.textContent;
                    }
                    return acc.trim();
                }
            }
            // Fallback: nếu không có <strong>, lấy toàn bộ text của <li> có chữ Domain:
            const fallback = nodes.find(li => /Domain:/i.test(li.textContent));
            return fallback ? fallback.textContent : null;
        });

        if (!extractedText) {
            console.log('Không tìm thấy đoạn text chứa "Domain:".');
            return;
        }

        // CHỈ lấy URL bằng regex (loại bỏ IP address và text khác)
        const urlMatch = extractedText.match(/https?:\/\/[^\s"'<>]+/i);
        if (!urlMatch) {
            console.log('Không bắt được URL trong chuỗi:', extractedText);
            return;
        }

        // Làm sạch dấu câu ở cuối nếu có
        const defacedUrl = urlMatch[0].replace(/[),.;]+$/, '').trim();

        fs.appendFileSync('urls.txt', defacedUrl + '\n', { encoding: 'utf8' });
        console.log(`✅ THÀNH CÔNG! Đã lưu URL: ${defacedUrl} vào tệp urls.txt`);
    } catch (error) {
        console.error('Đã xảy ra lỗi:', error);
    } finally {
        await browser.close();
    }
}

getAndSaveDefacedUrl();
