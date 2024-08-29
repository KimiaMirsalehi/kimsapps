import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import json
import matplotlib.pyplot as plt

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

def apply_theme(theme):
    """Apply the selected theme."""
    if theme == "Light":
        st.markdown("""
            <style>
            body {
                color: black;
                background-color: white;
            }
            [data-testid="stSidebar"] {
                background-color: #D8BFD8;
                color: black;
            }
            [data-testid="stSidebarNav"] {
                color: black;
            }
            </style>
            """, unsafe_allow_html=True)
    elif theme == "Dark":
        st.markdown("""
            <style>
            body {
                color: white;
                background-color: #BDB5D5;
            }
            [data-testid="stSidebar"] {
                background-color: #483248;
                color: #C0C0C0;
            }
            [data-testid="stSidebar"] *,
            [data-testid="stSidebarNav"] a, 
            [data-testid="stSidebarNav"] div,
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] .stRadio > label,
            [data-testid="stSidebar"] .stCheckbox > label,
            [data-testid="stSidebar"] .stSelectbox > label,
            [data-testid="stSidebar"] .stTextInput > label {
                color: #C0C0C0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        # Default theme
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background-color: #D8BFD8;
            }
            [data-testid="stSidebarNav"] {
                font-size: 18px;
                color: black;
            }
            </style>
            """, unsafe_allow_html=True)

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

    # Load votes from JSON
    votes_file = os.path.join(JSON_FOLDER, "pdf_votes.json")
    if not os.path.exists(JSON_FOLDER):
        os.makedirs(JSON_FOLDER)

    if os.path.exists(votes_file):
        with open(votes_file, 'r') as f:
            votes = json.load(f)
    else:
        votes = {}

    pdf_name = os.path.basename(file_path)
    current_votes = votes.get(pdf_name, 0)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("👍 Upvote"):
            current_votes += 1
            votes[pdf_name] = current_votes
            with open(votes_file, 'w') as f:
                json.dump(votes, f)
            st.success(f"Upvoted! Current Votes: {current_votes}")
    with col2:
        st.write(f"Votes: {current_votes}")
    with col3:
        if st.button("👎 Downvote"):
            current_votes -= 1
            votes[pdf_name] = current_votes
            with open(votes_file, 'w') as f:
                json.dump(votes, f)
            st.success(f"Downvoted! Current Votes: {current_votes}")

    # Display existing votes count
    st.write(f"Current votes for this PDF: {current_votes}")



def display_dashboard():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        st.title("Dashboard")

        page_size = 20
        total_pages = len(df) // page_size + 1
        page_num = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, step=1)
        start_idx = (page_num - 1) * page_size

        # Updated to remove index
        st.table(df.iloc[start_idx:start_idx + page_size].reset_index(drop=True).style.hide(axis='index'))

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Available PDF Files")
            available_pdfs = list_files()

            # Load votes from JSON
            votes_file = os.path.join(JSON_FOLDER, "pdf_votes.json")
            if os.path.exists(votes_file):
                with open(votes_file, 'r') as f:
                    votes = json.load(f)
            else:
                votes = {}

            for pdf in available_pdfs:
                pdf_name = os.path.basename(pdf)
                current_votes = votes.get(pdf_name, 0)

                if st.button(pdf, key=pdf):
                    st.session_state.selected_file = pdf
                    st.session_state.page = "Document Library"

                st.write(f"Votes: {current_votes}")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"👍 Upvote {pdf}", key=f'up_{pdf}'):
                        votes[pdf_name] = votes.get(pdf_name, 0) + 1
                        with open(votes_file, 'w') as f:
                            json.dump(votes, f)
                        st.success(f"Upvoted! Current Votes: {votes[pdf_name]}")
                with col2:
                    st.write(f"Votes: {votes[pdf_name]}")
                with col3:
                    if st.button(f"👎 Downvote {pdf}", key=f'down_{pdf}'):
                        votes[pdf_name] = votes.get(pdf_name, 0) - 1
                        with open(votes_file, 'w') as f:
                            json.dump(votes, f)
                        st.success(f"Downvoted! Current Votes: {votes[pdf_name]}")
                st.markdown("---")

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

    # Initialize default theme in session state if it doesn't exist
    if 'default_theme' not in st.session_state:
        st.session_state.default_theme = "Default"

    theme = st.radio("Theme", ["Default", "Light", "Dark"], index=["Default", "Light", "Dark"].index(st.session_state.default_theme))

    if st.button("Set as Default Theme"):
        st.session_state.default_theme = theme
        st.success(f"Default theme set to: {theme}")

    apply_theme(theme)

    default_zoom = st.slider("Default Zoom Level", 1.0, 5.0, 5.0, 0.1)
    st.write(f"Default zoom level set to: {default_zoom}")

    save_location = st.text_input("Notes' Default Save Location", JSON_FOLDER)
    st.write(f"Files will be saved to: {save_location}")

def main():
    st.set_page_config(page_title="Dashboard", layout="wide")

    # Ensure default theme is applied on app load
    if 'default_theme' not in st.session_state:
        st.session_state.default_theme = "Default"

    apply_theme(st.session_state.default_theme)

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
                zoom_level = st.sidebar.slider("Zoom Level", 1.0, 5.0, 5.0, 0.1)
                display_pdf(file_path, zoom_level)
            else:
                st.error("Unsupported file type")
    elif st.session_state.page == "Settings":
        display_settings()

if __name__ == "__main__":
    main()
