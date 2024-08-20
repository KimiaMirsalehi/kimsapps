import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import matplotlib.pyplot as plt
import json

# Constants
FILE_FOLDER = 'files'
JSON_FOLDER = 'JSON_FILES'
EXCEL_FILE = os.path.join(FILE_FOLDER, 'pdf_details.xlsx')

# Utility functions
def list_files():
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def render_page(page, zoom_level):
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))
    img = Image.open(io.BytesIO(pix.tobytes()))
    return img

def display_pdf(file_path, zoom_level):
    doc = fitz.open(file_path)
    num_pages = len(doc)

    if 'page_num' not in st.session_state:
        st.session_state.page_num = 0

    page = doc.load_page(st.session_state.page_num)
    img = render_page(page, zoom_level)
    st.image(img, caption=f"Page {st.session_state.page_num + 1}", use_column_width=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous") and st.session_state.page_num > 0:
            st.session_state.page_num -= 1
    with col2:
        st.write(f"Page {st.session_state.page_num + 1} of {num_pages}")
    with col3:
        if st.button("Next") and st.session_state.page_num < num_pages - 1:
            st.session_state.page_num += 1

    notes_file = os.path.join(JSON_FOLDER, f"{os.path.basename(file_path)}_notes.json")
    annotations = ""
    if os.path.exists(notes_file):
        with open(notes_file, 'r') as f:
            saved_notes = json.load(f)
            annotations = saved_notes.get(str(st.session_state.page_num), "")
    
    st.text_area("Add your notes here", value=annotations, key="annotation")
    if st.button("Save Note"):
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                saved_notes = json.load(f)
        else:
            saved_notes = {}
        
        saved_notes[str(st.session_state.page_num)] = st.session_state.annotation
        with open(notes_file, 'w') as f:
            json.dump(saved_notes, f)
        st.success("Note saved!")

def display_dashboard():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        st.title("Dashboard")

        page_size = 20
        total_pages = len(df) // page_size + 1
        page_num = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page_num - 1) * page_size
        st.dataframe(df.iloc[start_idx:start_idx + page_size], use_container_width=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Available PDF Files")
            available_pdfs = [f for f in list_files() if f.endswith('.pdf')]
            for pdf in available_pdfs:
                if st.button(pdf, key=pdf):
                    st.session_state.selected_file = pdf
                    st.session_state.page = "Document Library"

        with col2:
            st.subheader("Source Distribution")
            source_counts = df['Source'].value_counts()
            
            purple_shades = [
                '#E6E6FA',  # Lavender
                '#D8BFD8',  # Thistle
                '#DDA0DD',  # Plum
                '#EE82EE',  # Violet
                '#DA70D6',  # Orchid
                '#FF00FF',  # Fuchsia
                '#BA55D3',  # MediumOrchid
                '#8A2BE2'   # BlueViolet
            ]
            
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(source_counts, labels=source_counts.index, autopct='%1.1f%%', startangle=90, colors=purple_shades)
            ax.axis('equal')
            st.pyplot(fig)
    else:
        st.error(f"Excel file not found at {EXCEL_FILE}")

def display_settings():
    st.title("Settings")
    st.write("Adjust your preferences below:")

    theme = st.radio("Theme", ["Light", "Dark"], index=0)
    if theme == "Light":
        st.markdown("""
            <style>
            body {
                color: black;
                background-color: white;
            }
            [data-testid="stSidebar"] {
                background-color: #D8BFD8;
            }
            [data-testid="stSidebarNav"] {
                font-size: 18px;
                color: black;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            body {
                color: black; /* Ensure body text remains dark */
                background-color: #121212;
            }
            [data-testid="stSidebar"] {
                background-color: #333333;
                color: white;
            }
            [data-testid="stSidebarNav"] {
                color: white;
            }
            [data-testid="stMarkdownContainer"] {
                color: black; /* Ensure markdown container text is dark */
            }
            </style>
            """, unsafe_allow_html=True)

    default_zoom = st.slider("Default Zoom Level", 1.0, 5.0, 5.0, 0.1)  # Default to 5.0
    st.write(f"Default zoom level set to: {default_zoom}")

    save_location = st.text_input("Notes' Default Save Location", JSON_FOLDER)
    st.write(f"Files will be saved to: {save_location}")

def main():
    st.set_page_config(page_title="Dashboard", layout="wide")

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Dashboard", "Document Library", "Settings"])
        st.session_state.page = page

    if st.session_state.page == "Dashboard":
        st.session_state.selected_file = None
        display_dashboard()
    elif st.session_state.page == "Document Library":
        files = list_files()
        selected_file = st.sidebar.selectbox("Select a file", files)
        if selected_file:
            st.session_state.selected_file = selected_file

        if st.session_state.get('selected_file'):
            st.title("Regulation Viewer")
            file_path = os.path.join(FILE_FOLDER, st.session_state.selected_file)
            if st.session_state.selected_file.lower().endswith('.pdf'):
                st.sidebar.header("View Options")
                zoom_level = st.sidebar.slider("Zoom Level", 1.0, 5.0, 5.0, 0.1)  # Default to 5.0
                display_pdf(file_path, zoom_level)
            else:
                st.error("Unsupported file type")
    elif st.session_state.page == "Settings":
        display_settings()

if __name__ == "__main__":
    main()
