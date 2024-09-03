import streamlit as st
import os
import streamlit.components.v1 as components

# Constants
FILE_FOLDER = 'files'  # Ensure this folder exists and has the correct PDFs
PDF_SERVER_FOLDER = 'static_files'

# Ensure the PDF_SERVER_FOLDER exists
if not os.path.exists(PDF_SERVER_FOLDER):
    os.makedirs(PDF_SERVER_FOLDER)

def list_files():
    """List PDF files in the FILE_FOLDER directory."""
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def copy_pdf_to_static_folder(pdf_filename):
    """Copy the selected PDF to the static folder for serving."""
    src = os.path.join(FILE_FOLDER, pdf_filename)
    dst = os.path.join(PDF_SERVER_FOLDER, pdf_filename)
    if not os.path.exists(dst):
        with open(src, "rb") as src_file:
            with open(dst, "wb") as dst_file:
                dst_file.write(src_file.read())
    return f"/{PDF_SERVER_FOLDER}/{pdf_filename}"

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
            # Copy the PDF to the static folder
            file_url = copy_pdf_to_static_folder(selected_file)
            st.subheader(f"Viewing: {selected_file}")
            pdf_viewer(file_url)

if __name__ == "__main__":
    main()
