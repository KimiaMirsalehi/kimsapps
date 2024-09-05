import streamlit as st
import os

# Constants
FILE_FOLDER = 'files'  # Folder where original PDFs are stored

def list_files():
    """List PDF files in the FILE_FOLDER directory."""
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def pdf_viewer(file_path):
    """Display the PDF directly using Streamlit's built-in method."""
    with open(file_path, "rb") as f:
        # Display the PDF in the app
        st.download_button(label="Download PDF", data=f, file_name=os.path.basename(file_path), mime="application/pdf")
        st.write("### PDF Preview")
        st.download_button(label="Preview PDF", data=f, file_name=os.path.basename(file_path), mime="application/pdf")
        st.pdf(f.read())

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
