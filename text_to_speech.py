import asyncio
from playwright.async_api import async_playwright
import os
import requests
import time

async def clone_voice_nicevoice(audio_path, text_to_speak, output_path="cloned_voice.mp3"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True for silent
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        print("🌐 Opening NiceVoice...")
        await page.goto("https://nicevoice.org", timeout=60000)

        # Step 1: Click "Start Voice Cloning"
        print("🎬 Clicking 'Start Voice Cloning'...")
        await page.click("text=Start Voice Cloning")

        # Step 2: Click "My Device"
        print("💻 Selecting 'My Device'...")
        

        # Step 3: Upload audio file
        print(f"📤 Uploading file: {audio_path}")
        await page.set_input_files("input[type=file]", audio_path)
        await page.click("button:has(span:text('CLONE VOICE'))")
        await page.wait_for_timeout(20000)
        # Step 4: Wait for text box and type
        print("✍️ Entering text...")
        await page.fill("textarea[placeholder='Enter the text you want AI to speak here']", text_to_speak)

        # Step 5: Click "Generate Voiceover"
        print("⚙️ Clicking 'Generate Voiceover'...")
        await page.click("text=Generate Voiceover")

        # Step 6: Wait 20 seconds (or longer depending on load)
        print("⏳ Waiting for audio to generate...")
        await page.wait_for_timeout(40000)

        # Step 7: Click Download button
        print("📥 Clicking download icon...")
        download_button = await page.query_selector("button >> xpath=//*[name()='svg' and @data-icon='download']")
        if not download_button:
            raise RuntimeError("❌ Download button not found.")
        
        with page.expect_download() as download_info:
            await download_button.click()
        download = await download_info.value
        await download.save_as(output_path)

        print(f"✅ Cloned voice saved as: {output_path}")
        await browser.close()

# Example usage
if __name__ == "__main__":
    asyncio.run(clone_voice_nicevoice("test1.mp3", "This is a Peter Griffin impression!"))
