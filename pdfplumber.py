import streamlit as st
import streamlit.components.v1 as components
import os

# Define file locations
FILE_FOLDER = 'files'
JSON_FOLDER = 'JSON_FILES'

def list_files():
    return [f for f in os.listdir(FILE_FOLDER) if f.endswith('.pdf') and os.path.isfile(os.path.join(FILE_FOLDER, f))]

def pdf_viewer(file_path):
    pdf_display = f"""
        <iframe src="https://mozilla.github.io/pdf.js/web/viewer.html?file=file://{file_path}" width="100%" height="800px">
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
            st.subheader(f"Viewing: {selected_file}")
            pdf_viewer(file_path)

if __name__ == "__main__":
    main()
