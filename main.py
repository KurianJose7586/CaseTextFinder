# main.py

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from llm import get_case_titles

# --- Get list of case titles ---
case_list = get_case_titles()
print("📚 Relevant Case Titles:")
for i, title in enumerate(case_list, start=1):
    print(f"{i}. {title}")

# --- Choose which to download ---
choices = input("\n🔽 Enter case numbers to download (comma-separated, e.g., 1,3): ")
try:
    selected_indexes = [int(i.strip()) - 1 for i in choices.split(",") if i.strip().isdigit()]
    selected_cases = [case_list[i] for i in selected_indexes if 0 <= i < len(case_list)]
except Exception as e:
    print("❌ Invalid selection:", e)
    exit()

if not selected_cases:
    print("⚠️ No valid cases selected.")
    exit()

# --- Setup download directory ---
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

# --- Configure browser ---
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "plugins.always_open_pdf_externally": True,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True
})
chrome_options.add_argument("--incognito")

# --- Launch browser once ---
driver = webdriver.Chrome(options=chrome_options)

# --- Search and download loop ---
for case_title in selected_cases:
    print(f"\n🔎 Searching for: {case_title}")
    try:
        driver.get("https://indiankanoon.org/search/")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Advanced Search"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.catselectall[name='doctypes']"))
        )
        for checkbox in driver.find_elements(By.CSS_SELECTOR, "input.catselectall[name='doctypes']"):
            value = checkbox.get_attribute("value")
            if value != "sc" and checkbox.is_selected():
                checkbox.click()

        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        title_input.clear()
        title_input.send_keys(case_title)
        print(f"✅ Entered case title: {case_title}")

        driver.find_element(By.ID, "advsearchbutton").click()

        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.result_title a"))
        )
        first_result.click()

        pdf_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pdfdoc"))
        )
        pdf_button.click()
        print("⏳ Waiting for PDF to download...")
        time.sleep(8)
    except Exception as e:
        print(f"❌ Error processing '{case_title}': {e}")
        continue

# --- Close browser ---
driver.quit()

# --- Confirm PDFs ---
pdfs = [f for f in os.listdir(download_dir) if f.endswith(".pdf")]
if pdfs:
    print(f"\n✅ Downloaded PDFs:")
    for pdf in pdfs:
        print("📄", pdf)
else:
    print("❌ No PDFs found.")
