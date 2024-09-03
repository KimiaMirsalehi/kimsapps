import streamlit as st
import fitz  # PyMuPDF
import json
import os

# Constants
FILE_FOLDER = 'files'
JSON_FOLDER = 'JSON_FILES'

def list_files():
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def extract_text(page):
    """Extract text and position from a PDF page."""
    text = page.get_text("dict")
    return text

def highlight_text(text, highlights):
    """Return text with highlights."""
    for highlight in highlights:
        start_idx, end_idx = highlight['range']
        text = (
            text[:start_idx] +
            f"<mark>{text[start_idx:end_idx]}</mark>" +
            text[end_idx:]
        )
    return text

def display_pdf(file_path):
    doc = fitz.open(file_path)
    num_pages = len(doc)

    if 'page_num' not in st.session_state:
        st.session_state.page_num = 0

    page = doc.load_page(st.session_state.page_num)
    page_text = extract_text(page)
    
    # Display text
    st.markdown(f"### Page {st.session_state.page_num + 1}")
    
    text_blocks = page_text["blocks"]

    # Load existing highlights
    highlights_file = os.path.join(JSON_FOLDER, f"{os.path.basename(file_path)}_highlights.json")
    if os.path.exists(highlights_file):
        with open(highlights_file, 'r') as f:
            highlights_data = json.load(f)
    else:
        highlights_data = {}

    # Get highlights for current page
    highlights = highlights_data.get(str(st.session_state.page_num), [])

    for block in text_blocks:
        if block["type"] == 0:  # Text block
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if highlights:
                        text = highlight_text(text, highlights)
                    st.markdown(text, unsafe_allow_html=True)

    # Navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous") and st.session_state.page_num > 0:
            st.session_state.page_num -= 1
    with col2:
        st.write(f"Page {st.session_state.page_num + 1} of {num_pages}")
    with col3:
        if st.button("Next") and st.session_state.page_num < num_pages - 1:
            st.session_state.page_num += 1

    # Highlighting functionality
    st.subheader("Highlight Text")
    highlight_start = st.number_input("Start Index", min_value=0, value=0)
    highlight_end = st.number_input("End Index", min_value=0, value=0)

    if st.button("Highlight"):
        if highlight_start < highlight_end:
            new_highlight = {"range": [highlight_start, highlight_end]}
            highlights.append(new_highlight)

            # Save highlights
            highlights_data[str(st.session_state.page_num)] = highlights
            with open(highlights_file, 'w') as f:
                json.dump(highlights_data, f)
            
            st.success("Text highlighted!")

def main():
    st.set_page_config(page_title="PDF Viewer with Highlights", layout="wide")

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Document Library"])
        st.session_state.page = page

    if st.session_state.page == "Document Library":
        files = list_files()
        selected_file = st.sidebar.selectbox("Select a file", files)
        
        if selected_file and selected_file != st.session_state.get('selected_file'):
            st.session_state.selected_file = selected_file
            st.session_state.page_num = 0

        if st.session_state.get('selected_file'):
            st.title("PDF Viewer")
            file_path = os.path.join(FILE_FOLDER, st.session_state.selected_file)
            display_pdf(file_path)

if __name__ == "__main__":
    main()

