import streamlit as st
import os

# Constants
FILE_FOLDER = 'files'  # Folder where original PDFs are stored

def list_files():
    """List PDF files in the FILE_FOLDER directory."""
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def pdf_viewer(file_path):
    """Display the PDF using an embed tag."""
    with open(file_path, "rb") as f:
        base64_pdf = f.read()
        # Display PDF inside an iframe
        pdf_display = f"""
            <iframe src="data:application/pdf;base64,{base64_pdf.decode('latin-1')}" width="100%" height="800px">
            </iframe>
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
            file_path = os.path.join(FILE_FOLDER, selected_file)
            st.subheader(f"Viewing: {selected_file}")
            pdf_viewer(file_path)

if __name__ == "__main__":
    main()
