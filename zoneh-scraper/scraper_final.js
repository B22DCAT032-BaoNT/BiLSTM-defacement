// scraper.js
const puppeteer = require('puppeteer');
const fs = require('fs');

async function getAndSaveDefacedUrls() {
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    try {
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        );

        if (fs.existsSync('urls.txt')) {
            console.log('📄 Phát hiện tệp urls.txt — sẽ ghi nối tiếp kết quả vào cuối tệp hiện có.');
        } else {
            console.log('🆕 Chưa có tệp urls.txt — sẽ tạo mới.');
        }

        for (let attempt = 41471240; attempt > 41471240 - 1000; attempt--) { // Vòng lặp

            try {
                const url = `https://www.zone-h.org/mirror/id/${attempt}`;
                console.log(`--- Đang xử lý url: ${url} ---`);

                await page.goto(url, { waitUntil: 'networkidle2' });

                const xpathSelector = "//li[contains(., 'Domain:')]";

                //Thêm timeout: 3000 (3 giây)
                await page.waitForSelector(`xpath/${xpathSelector}`, { timeout: 3000 });

                // Nếu không có lỗi timeout, code bên dưới sẽ được thực thi
                const extractedText = await page.evaluate((xpath) => {
                    const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    return result.singleNodeValue ? result.singleNodeValue.textContent : null;
                }, xpathSelector);

                if (extractedText) {
                    const defacedUrl = extractedText.split('Domain:')[1].split('IP address:')[0].trim();
                    fs.appendFileSync('urls.txt', defacedUrl + '\n');
                    console.log(`✅ Đã lưu Domain: ${defacedUrl} \n`);
                }
            } catch (error) {
                // Nếu có lỗi thông báo và bỏ qua
                if (error.name === 'TimeoutError') {
                    console.log(`🟡 Bỏ qua ID ${attempt} do hết thời gian chờ (3s).`);
                } else {
                    console.error(`❌ Lỗi không xác định với ID ${attempt}: ${error.message}`);
                }
                // Vòng lặp sẽ tự động chuyển sang ID tiếp theo
            }
        }
    } catch (error) {
        console.error('Đã xảy ra lỗi nghiêm trọng:', error);
    } finally {
        console.log('🎉 Hoàn tất quá trình quét!');
        if (browser) {
            await browser.close();
        }
    }
}

getAndSaveDefacedUrls();