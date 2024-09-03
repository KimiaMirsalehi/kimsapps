import streamlit as st
import os
import shutil

# Define directories
FILE_FOLDER = 'files'
STATIC_FOLDER = 'static'

# Ensure the STATIC_FOLDER exists
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

def list_files():
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf')]

def copy_file_to_static(pdf_filename):
    src = os.path.join(FILE_FOLDER, pdf_filename)
    dst = os.path.join(STATIC_FOLDER, pdf_filename)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    file_url = f"/{STATIC_FOLDER}/{pdf_filename}"
    st.write(f"File URL: {file_url}")
    return file_url

def main():
    st.title("PDF Viewer Debugging")

    files = list_files()
    selected_file = st.selectbox("Select a PDF file", files)

    if selected_file:
        file_url = copy_file_to_static(selected_file)
        st.write(f"PDF URL: {file_url}")
        st.markdown(f"[Open PDF]({file_url})")

if __name__ == "__main__":
    main()
