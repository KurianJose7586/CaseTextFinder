# llm.py

import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# --- Load API key ---
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# --- Normalize function (exact as provided) ---
def normalize_case_title(title: str) -> str:
    title = title.strip()

    # Replace "v." or "vs." with "vs"
    title = re.sub(r'\bv[.]?\b', 'vs', title, flags=re.IGNORECASE)

    # Replace "versus" with "vs"
    title = re.sub(r'\bversus\b', 'vs', title, flags=re.IGNORECASE)

    # Replace "and others" or "and ors" with "And Ors"
    title = re.sub(r'and\s+(others|ors[.]?)', 'And Ors', title, flags=re.IGNORECASE)

    # Capitalize first letter of each word
    title = title.title()

    # Fix specific known issues (optional fine-tuning)
    title = title.replace("Vs", "vs").replace("And Ors", "And Ors")

    return title


# --- Main function to fetch and normalize case titles ---
def get_case_titles():
    context = input("🗣️ Describe the legal issue (natural language):\n")
    print("🧠 Thinking...")

    prompt = f"""
You are a legal research assistant helping a user find Indian Supreme Court cases.

🎯 Given the following legal issue, return a list of the most relevant Indian Supreme Court case titles.
IMPORTANT: Make sure the case title is a valid case title from the Indian Supreme Court.
IMPORTANT: NO explanation or date or commentary or anything else just the case titles.

📋 Respond in the following format ONLY:
Case Titles:
1. <Case Title One>
2. <Case Title Two>
3. <Case Title Three>

Legal Issue:
{context}
"""

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free", 
        messages=[
            {"role": "system", "content": "You are a helpful legal assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )

    raw_output = response.choices[0].message.content.strip()

    # Extract numbered case titles from LLM response
    case_titles = re.findall(r"\d+\.\s*(.+)", raw_output)

    # Apply normalization
    normalized = [normalize_case_title(t) for t in case_titles]

    if not normalized:
        print("⚠️ No valid case titles found in the response.")
    return normalized
