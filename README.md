```markdown
# 🏛️ CaseTextFinder

A Python tool for Indian legal researchers to **automatically retrieve Supreme Court case titles** and **download their judgments (PDFs)** based on a natural language description of a legal issue.

---

## 🚀 Features

- 🧠 Uses LLMs to identify relevant Supreme Court case titles from a legal issue.
- 🔎 Scrapes **Indian Kanoon** to find and download the PDFs of judgments.
- 📄 Lets you choose multiple relevant cases to download in one go.
- 🔤 Smart formatting of case titles (`v.` → `vs`, consistent casing, etc.).

---

## 🛠️ Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/CaseTextFinder.git
   cd CaseTextFinder
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenRouter API key:

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

---

## 🧠 Models Used

LLMs are called via [OpenRouter](https://openrouter.ai/). You can change the model in `llm.py`.

Example:
```python
model="anthropic/claude-3-haiku:free"
```

You can also try:
- `openai/gpt-3.5-turbo`
- `mistralai/mixtral-8x7b-instruct:free`
- `google/gemma-7b`

---

## ▶️ Usage

```bash
python main.py
```

1. Enter a natural language legal issue (e.g. *"Violation of fundamental rights due to internet shutdowns in Jammu and Kashmir."*).
2. The assistant will suggest the most relevant case titles.
3. Choose one or more cases to download.
4. PDFs are saved in the `/downloads` directory.

---

## 📂 Project Structure

```text
CaseTextFinder/
├── main.py               # Main script for running the tool
├── llm.py                # LLM functions for title generation
├── .env                  # API key (not included)
├── requirements.txt      # Python dependencies
├── downloads/            # Output folder for judgment PDFs
```

---

## 📌 Notes

- Currently filters only **Supreme Court** judgments.
- Accuracy depends on LLM response and Indian Kanoon search results.
- Title normalization improves match quality.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for more info.

---

## ✨ Future Ideas

- Add relevance scoring for multiple case suggestions.
- Extend to High Courts.
- Optional summary previews using LLMs.

---

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/)
- [Indian Kanoon](https://indiankanoon.org/)
- [Selenium](https://www.selenium.dev/)

---

> Made with ❤️ to make legal research easier.
```
