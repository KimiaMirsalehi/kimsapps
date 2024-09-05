import streamlit as st
import os
import shutil

# Constants
FILE_FOLDER = 'files'  # Folder where original PDFs are stored
STATIC_FOLDER = 'static'  # Folder from which Streamlit will serve static files

# Ensure STATIC_FOLDER exists
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

def list_files():
    """List PDF files in the FILE_FOLDER directory."""
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def copy_pdf_to_static_folder(pdf_filename):
    """Copy the selected PDF to the static folder for serving."""
    src = os.path.join(FILE_FOLDER, pdf_filename)
    dst = os.path.join(STATIC_FOLDER, pdf_filename)
    if not os.path.exists(dst):
        shutil.copy(src, dst)
    file_url = f"/static/{pdf_filename}"  # URL for the static file
    return file_url

def pdf_viewer(file_url):
    """Display the PDF using an iframe."""
    pdf_display = f"""
        <iframe src="{file_url}" width="100%" height="800px"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

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
