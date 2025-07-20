import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# --- Load API key from .env ---
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
#meta-llama/llama-3.3-70b-instruct:free
#deepseek/deepseek-r1-0528:free

DEFAULT_MODEL = os.getenv("LLM_MODEL", "moonshotai/kimi-k2:free")

# --- OpenRouter client ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# --- Normalize case titles ---
def normalize_case_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r'\(.*?\)', '', title)  # remove anything in parentheses
    title = re.sub(r'\bv[.]?\b', 'vs', title, flags=re.IGNORECASE)
    title = re.sub(r'\bversus\b', 'vs', title, flags=re.IGNORECASE)
    title = re.sub(r'\bvs\s+vs\b', 'vs', title, flags=re.IGNORECASE)  # <--- NEW LINE
    title = re.sub(r'and\s+(others|ors[.]?)', 'And Ors', title, flags=re.IGNORECASE)
    title = title.title()
    title = title.replace("Vs", "vs").replace("And Ors", "And Ors")
    return title.strip()

# --- Case Title Retrieval ---
def get_case_titles(context: str):
    prompt = f"""
You are a legal research assistant helping a law student find landmark **Indian Supreme Court cases**.

🎯 Task:
Given the following legal issue, return a list of real and relevant **Indian Supreme Court case titles**.

🔒 Constraints:
- Only return official and verifiable case titles (no hallucinations or fabrications).
- These should be major or cited judgments that appear on Indian Kanoon or in legal databases.
- IMPORTANT: DO NOT include explanations, commentary, dates, or metadata — JUST THE CASE TITLES.

📋 Respond in this format ONLY:
Case Titles:
1. <Valid Supreme Court Case Title>
2. <Another Real and related Supreme Court Case Title>
3. <Another One...>

Example:
Case Titles:
1. Kesavananda Bharati vs State of Kerala
2. Maneka Gandhi vs Union of India
3. Navtej Singh Johar vs Union of India

REMINDER: Under no circamstances should you include any explanations, commentary, dates, or metadata — JUST THE CASE TITLES.
INCENTIVE: If you include any explanations, commentary, dates, or metadata, you will be fired and for each correct and valid case title you will be rewarded.
Example of a invalid case title: M. Siddiq (D) Thr Lrs vs Mahant Suresh Das (Ram Janmabhoomi Case)
Example of a valid case title: M. Siddiq (D) Thr Lrs vs Mahant Suresh Das

Legal Issue:
{context}
"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        raw_output = response.choices[0].message.content.strip()
        case_titles = re.findall(r"\d+\.\s*(.+)", raw_output)
        return [normalize_case_title(t) for t in case_titles]

    except Exception as e:
        print("Error fetching case titles:", e)
        return []

# --- Case Brief Generator from Judgment Text ---
def generate_brief_from_judgment(case_title: str, judgment_text: str, retries=2) -> str:
    prompt = 
    f"""
"You are a legal research assistant. Your only job is to output a structured case brief based on the judgment text provided — without any internal reasoning, thinking steps, or commentary. Do not explain your actions. Only return the final formatted brief as per the sections defined below."

CASE NAME
{case_title}

Court: (e.g., Constitution Bench of the Supreme Court of India)
Area of Law: (e.g., Criminal Procedure / Human Rights / Policing)
Citations

🟩 Brief Facts:
Summarize the background and factual context in 3–5 sentences.

🟨 Issues for Consideration:
List the most crucial key legal issues the court considered.

🟦 Observations by the Court:
Provide a well-structured paragraph summarizing the court's judgment, clearly explaining what the court held, how it interpreted the law, and the reasoning that led to its conclusion. Avoid bullet points and ensure the explanation flows smoothly with logical coherence and clarity.

🟪 Judgment:
key directions, verdicts, or legal principles laid down.

🟫 Developments in Law (if any):
Provide a well-structured paragraph summarizing how this case influenced or changed the law or has been cited in later decisions.Avoid bullet points and ensure the explanation flows smoothly with logical coherence and clarity.

IMPORTANT:
- Use the actual case title "{case_title}" in your response, not any example case titles.
- DO NOT include any reasoning steps like "Let me think", "Let's consider", or "Thinking step-by-step".
- ONLY return the final output in the structured format.
- DO NOT use first-person statements.

JUDGMENT TEXT TO ANALYZE:
{judgment_text}
"""


    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            if attempt < retries:
                print(f"⚠️ Retry {attempt+1} after error: {e}")
                time.sleep(2)
            else:
                return f"❌ Error generating summary after {retries+1} attempts: {e}"

def clean_llm_brief_response(text: str) -> str:
    """
    Removes any preamble (e.g., 'Let's think step-by-step') before the actual brief.
    Looks for the first line containing 'CASE NAME' or 'Case Title' etc.
    """
    trigger_keywords = ["CASE NAME", "Case Title", "Court:"]
    for keyword in trigger_keywords:
        idx = text.find(keyword)
        if idx != -1:
            return text[idx:].strip()
    return text.strip()  # fallback, return original if nothing found

def format_brief_markdown(raw_text: str) -> str:
    """
    Formats raw LLM output for better Markdown rendering.
    Adds proper spacing, bold headers, fixes common artifacts.
    """
    sections = [
        "CASE NAME",
        "Court:",
        "Area of Law:",
        "Citations",
        "Brief Facts:",
        "Issues for Consideration:",
        "Observations by the Court:",
        "Judgment:",
        "Developments in Law (if any):"
    ]

    # Replace common garbage characters
    clean_text = raw_text.replace("�", "").strip()

    # Add bold to section headers
    for section in sections:
        pattern = re.escape(section)
        clean_text = re.sub(
        rf"(?:^|\n){pattern}",
        lambda m: m.group(0).replace(section, f"**{section}**"),
        clean_text
        )


    # Add spacing after headers
    clean_text = re.sub(r"(\*\*[^\n]+:\*\*)", r"\1\n", clean_text)

    # Ensure two newlines between sections
    clean_text = re.sub(r'\n{2,}', '\n\n', clean_text)

    return clean_text.strip()
