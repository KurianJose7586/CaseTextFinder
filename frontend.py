# frontend.py

import streamlit as st
from llm import get_case_titles
from main import download_case_pdfs, generate_case_brief

# --- Sidebar ---
st.sidebar.title("ℹ️ About")
st.sidebar.markdown(
    """
    **Legal Research Assistant** helps you find and download Supreme Court of India judgments and generate concise case briefs.\n\n
    - Enter a legal issue in plain English
    - Search for relevant cases
    - Download judgments as PDFs
    - Generate AI-powered case briefs
    """
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit")

st.set_page_config(page_title="Legal Research Assistant", layout="centered", page_icon="⚖️")

st.markdown("""
# ⚖️ Legal Research Assistant

<span style='color:#4F8BF9;font-size:18px;'>Find Supreme Court of India judgments and generate case briefs with AI.</span>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Session State for case results ---
if "case_titles" not in st.session_state:
    st.session_state.case_titles = []

# 📝 Input
with st.container():
    st.markdown("### 📝 Enter Legal Issue")
    user_query = st.text_area("", placeholder="E.g., Fundamental rights and national security")
    st.caption("Describe your legal issue in plain English.")

# 🔘 Trigger search
search_col, _ = st.columns([1, 5])
with search_col:
    if st.button("🔍 Search Relevant Cases", use_container_width=True):
        if user_query.strip():
            with st.spinner("Finding relevant case titles..."):
                st.session_state.case_titles = get_case_titles(user_query.strip())
        else:
            st.warning("Please enter a legal issue first.")

# ✅ Always define 'selected' so it exists regardless of the flow
selected = []

# ✅ If results exist, allow downloads
if st.session_state.case_titles:
    st.success(f"Found {len(st.session_state.case_titles)} case(s).", icon="✅")
    with st.expander("📚 View Found Cases", expanded=True):
        selected = st.multiselect("Select Case(s) to Download or Brief:", st.session_state.case_titles)
        if selected:
            st.markdown(
                "<ul>" + "".join([f"<li>{case}</li>" for case in selected]) + "</ul>", unsafe_allow_html=True
            )

    col1, col2 = st.columns(2)

    with col1:
        if selected and st.button("⬇️ Download Selected PDFs", use_container_width=True):
            with st.spinner("Downloading selected cases..."):
                download_case_pdfs(selected)
            st.success("✅ Selected PDFs downloaded. Check your 'downloads' folder.")

    with col2:
        if st.button("📦 Download All Case PDFs", use_container_width=True):
            with st.spinner("Downloading all found cases..."):
                download_case_pdfs(st.session_state.case_titles)
            st.success("✅ All PDFs downloaded. Check your 'downloads' folder.")

# 📄 Case briefs section
st.markdown("---")
st.subheader("🧾 Generate Case Briefs")
st.caption("Generate concise summaries for selected cases.")

if selected and st.button("🧠 Generate Case Briefs", use_container_width=True):
    with st.spinner("Generating case briefs..."):
        for title in selected:
            result = generate_case_brief(title)
            with st.expander(f"Brief for: {title}"):
                st.write(result)
    st.success("✅ All briefs generated. Check your 'briefs' folder.")

# --- Footer ---
st.markdown("""
---
<center><sub>Legal Research Assistant &copy; 2024. Not affiliated with the Supreme Court of India.</sub></center>
""", unsafe_allow_html=True)
