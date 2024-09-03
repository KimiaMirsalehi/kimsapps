import streamlit as st
import os
import streamlit.components.v1 as components

# Constants
FILE_FOLDER = 'files'
JSON_FOLDER = 'JSON_FILES'

def list_files():
    """List PDF files in the FILE_FOLDER directory."""
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def pdf_viewer(file_url):
    """Display the PDF using PDF.js in an iframe."""
    pdf_display = f"""
        <iframe src="https://mozilla.github.io/pdf.js/web/viewer.html?file={file_url}" width="100%" height="800px">
        </iframe>
    """
    components.html(pdf_display, height=800)

def main():
    st.title("Advanced PDF Viewer")

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Document Library"])
        st.session_state.page = page

    if st.session_state.page == "Document Library":
        files = list_files()
        selected_file = st.sidebar.selectbox("Select a file", files)
        
        if selected_file:
            file_path = os.path.join(FILE_FOLDER, selected_file)
            # Serve the file via Streamlit's static file mechanism
            file_url = f"/files/{selected_file}"
            st.subheader(f"Viewing: {selected_file}")
            pdf_viewer(file_url)

# Set up file serving in the Streamlit app
st.set_page_config(page_title="PDF Viewer with Highlights", layout="wide")
# This line will allow serving files via a specific route in the Streamlit app
st.markdown(
    f"""
    <style>
    .reportview-container .main .block-container{{
        padding-top: 2rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    main()
