import requests
from playwright.sync_api import sync_playwright
import os

def tts(char,text,filename):
    if char == "peter griffin":
        voice = "Peter Griffin (Modern, New)"
    else:
        voice = "Stewie Griffin (Classic)"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Go to FakeYou TTS page
        page.goto("https://fakeyou.com/tts")
        page.wait_for_timeout(5000)
        
        # Login
        page.click("text=Login")
        page.fill("input[placeholder='Username or Email']", "yusuff.0279@gmail.com")
        page.fill("input[placeholder='Password']", "vVaq3psPCu6wdrC")
        page.click("button:has-text('Login')")
        page.wait_for_timeout(3000)

        # Navigate to TTS
        page.click('a[href="/tts"] >> svg[data-icon="arrow-right-long"]')
        page.fill("input[placeholder*='Search from 3500+ voices']", char)
        page.wait_for_timeout(5000)

        # Select Peter Griffin voice
        modal = page.locator('div.fy-modal-body-wide')
        modal.wait_for()
        modal.locator(f'h6:has-text("{voice}")').nth(0).click()
        print("✅ Voice selected")

        # Fill the text input
        page.fill("textarea[placeholder*='to say...']", text)
        print("✅ Text filled")
        page.click("button:has-text('Speak')")
        print("⏳ Generating voice...")
        page.wait_for_timeout(30000)

        # Open More Details for matching voice generation
        page.locator("div.session-tts-section").first.locator("a:has-text('More details')").nth(0).click()


        page.wait_for_timeout(3000)

        # Handle new tab opening when download button is clicked
        with context.expect_page() as new_page_info:
            page.click("button >> svg[data-icon='arrow-down-to-line']")
        
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        
        # Get the URL from the new tab (this should be the direct audio link)
        audio_url = new_page.url
        print(f"🎵 Audio URL: {audio_url}")
        
        # Close the new tab
        new_page.close()
        
        # Download the audio file using requests
        try:
            response = requests.get(audio_url)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded and saved as {filename}")
            print(f"📁 File size: {len(response.content)} bytes")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading file: {e}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")

        browser.close()
    return filename

if __name__ == "__main__":
    tts('stewie griffin', 'Hello, world!', 'stewie_audio.wav')
