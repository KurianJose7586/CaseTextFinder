# main.py

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from llm import *

import fitz  # PyMuPDF
import markdown
import pdfkit

def setup_driver(download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    })
    return webdriver.Chrome(options=chrome_options)

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n\n".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"❌ Error reading PDF with PyMuPDF: {e}")
        return ""

def wait_for_pdf_download(download_dir, existing_files, timeout=60):
    """
    Waits up to `timeout` seconds for a new PDF file to appear in `download_dir`.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        new_files = set(os.listdir(download_dir)) - existing_files
        pdf_files = [f for f in new_files if f.lower().endswith(".pdf")]
        if pdf_files:
            return pdf_files[0]
        time.sleep(1)
    return None

def generate_case_brief(case_title):
    from llm import normalize_case_title

    download_dir = os.path.abspath("downloads")
    os.makedirs(download_dir, exist_ok=True)

    case_title = normalize_case_title(case_title)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in case_title)
    pdf_path = os.path.join(download_dir, f"{safe_title}.pdf")
    brief_pdf_path = os.path.join("briefs", f"{safe_title}.pdf")

    # ❗ If judgment PDF doesn't exist, use Selenium to download it
    if not os.path.exists(pdf_path):
        print(f"📥 PDF not found for '{case_title}', attempting to download...")
        try:
            driver = setup_driver(download_dir)

            driver.get("https://indiankanoon.org/search/")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Advanced Search"))
            ).click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.catselectall[name='doctypes']"))
            )
            for checkbox in driver.find_elements(By.CSS_SELECTOR, "input.catselectall[name='doctypes']"):
                if checkbox.get_attribute("value") != "sc" and checkbox.is_selected():
                    checkbox.click()

            title_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "title"))
            )
            title_input.clear()
            title_input.send_keys(case_title)

            driver.find_element(By.ID, "advsearchbutton").click()

            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.result_title a"))
            )
            first_result.click()

            try:
                pdf_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "pdfdoc"))
                )

                existing_files = set(os.listdir(download_dir))
                pdf_button.click()

                new_pdf = wait_for_pdf_download(download_dir, existing_files, timeout=60)
                if new_pdf:
                    new_pdf_path = os.path.join(download_dir, new_pdf)
                    os.rename(new_pdf_path, pdf_path)
                    print(f"✅ PDF downloaded and renamed to: {safe_title}.pdf")
                else:
                    driver.quit()
                    return f"❌ Timed out waiting for PDF download: {case_title}"

            except Exception as e:
                driver.quit()
                return f"❌ PDF button not found or failed to click for: {case_title}"

            driver.quit()

        except Exception as e:
            return f"❌ Error during PDF download: {e}"

    # ✅ Extract text from judgment and generate brief
    if not os.path.exists(pdf_path):
        return f"❌ PDF not found for: {case_title}"

    text = extract_text_from_pdf(pdf_path)
    if not text or len(text) < 1000:
        return f"⚠️ Not enough extractable text in PDF for: {case_title}"

    brief = generate_brief_from_judgment(case_title, text[:6000])
    brief = clean_llm_brief_response(brief)
    brief = format_brief_markdown(brief)

    os.makedirs("briefs", exist_ok=True)

    # ✅ Save brief as properly formatted PDF using pdfkit
    try:
        html_body = markdown.markdown(brief, extensions=["fenced_code", "tables"])

        html_template = f"""
<html>
<head>
    <meta charset='UTF-8'>
    <style>
        body {{
            font-family: 'Georgia', serif;
            margin: 40px;
            line-height: 1.7;
            color: #222;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        strong {{
            font-weight: bold;
            color: #000;
        }}
        p {{
            margin-bottom: 12px;
        }}
        .watermark {{
            position: fixed;
            top: 45%;
            left: 25%;
            transform: rotate(-45deg);
            font-size: 60px;
            color: rgba(150, 150, 150, 0.2);
            z-index: 0;
            width: 100%;
            text-align: center;
            pointer-events: none;
        }}
    </style>
</head>
<body>
<div class="watermark">LEGAL RESEARCH ASSISTANT</div>
{html_body}
</body>
</html>
"""


        config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(html_template, brief_pdf_path, configuration=config)
        print(f"✅ Brief PDF saved with styling: {brief_pdf_path}")
        return f"✅ Brief generated as styled PDF: {case_title}"

    except Exception as e:
        return f"❌ Failed to generate styled PDF brief: {e}"

def download_case_pdfs(case_titles):
    for title in case_titles:
        generate_case_brief(title)
