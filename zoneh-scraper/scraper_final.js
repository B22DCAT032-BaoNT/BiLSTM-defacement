const puppeteer = require('puppeteer');
const fs = require('fs');

async function getAndSaveDefacedUrls() {
    const browser = await puppeteer.launch({
        headless: false,
        slowMo: 50,
        defaultViewport: null,
        args: ['--start-maximized']
    });

    const page = await browser.newPage();
    const OUTPUT_FILE = 'defacement_url.txt';

    if (fs.existsSync(OUTPUT_FILE)) {
        console.log(`📄 Tìm thấy ${OUTPUT_FILE}, sẽ ghi nối tiếp.`);
    } else {
        console.log(`🆕 Tạo mới tệp ${OUTPUT_FILE}.`);
    }

    for (let attempt = 41471031; attempt > 41471031 - 1000; attempt--) {
        const url = `https://www.zone-h.org/mirror/id/${attempt}`;
        console.log(`🟢 Truy cập: ${url}`);

        try {
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });

            // 1. Kiểm tra xem có captcha không
            const isCaptcha = await page.$('img[src*="captcha"]');
            if (isCaptcha) {
                console.log('🛑 Phát hiện CAPTCHA — vui lòng nhập tay và nhấn "Gửi" trong trình duyệt.');
                await page.waitForFunction(
                    () => !document.querySelector('img[src*="captcha"]'),
                    { timeout: 120000 } // chờ tối đa 2 phút
                );
                console.log('✅ CAPTCHA đã qua — tiếp tục thu thập dữ liệu...');
            }

            // 2. Trích thông tin từ mirror nếu captcha đã vượt
            const domainText = await page.evaluate(() => {
                const el = [...document.querySelectorAll("li")].find(e =>
                    e.textContent.includes("Domain:")
                );
                return el ? el.textContent : null;
            });

            if (domainText) {
                const extracted = domainText.split('Domain:')[1].split('IP address:')[0].trim();
                fs.appendFileSync(OUTPUT_FILE, extracted + '\n');
                console.log(`✅ Đã lưu: ${extracted}\n`);
            } else {
                console.log('⚠️ Không tìm thấy domain trong trang.');
            }

        } catch (err) {
            console.log(`❌ Lỗi với ID ${attempt}: ${err.message}`);
        }
    }

    await browser.close();
    console.log('🎉 Quét hoàn tất!');
}

getAndSaveDefacedUrls();
