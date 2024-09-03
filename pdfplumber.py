import streamlit as st
import os
import base64

# Path where PDFs are located
FILE_FOLDER = 'files'

def list_files():
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf')]

def get_file_path(pdf_filename):
    return os.path.join(FILE_FOLDER, pdf_filename)

def main():
    st.title("PDF Viewer - Direct Load Test")

    files = list_files()
    selected_file = st.selectbox("Select a PDF file", files)

    if selected_file:
        file_path = get_file_path(selected_file)
        st.write(f"File Path: {file_path}")
        try:
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading file: {e}")

if __name__ == "__main__":
    main()
