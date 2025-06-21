from playwright.sync_api import sync_playwright

print('Testing Playwright...')
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('✅ Chromium launched successfully!')
    browser.close()
    print('✅ Playwright is working correctly!')
