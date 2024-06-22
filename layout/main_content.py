import streamlit as st
from utils import file_handlers
from config import ALLOWED_FILE_TYPES


def setup_main_content():
    st.subheader('Enter KB Article Details')
    workflow_option = st.radio("Select Workflow", ("Single File", "Multiple Files"))

    if workflow_option == "Single File":
        kb_article_titles, kb_article_contents = handle_single_file_workflow()
    else:
        kb_article_titles, kb_article_contents = handle_multiple_files_workflow()

    template_file = st.file_uploader(
        "Upload a template document (optional)",
        type=ALLOWED_FILE_TYPES
    )

    # Debug output
    st.write(f"Debug: Workflow option: {workflow_option}")
    st.write(f"Debug: Number of articles: {len(kb_article_titles)}")
    for title, content in zip(kb_article_titles, kb_article_contents):
        st.write(f"Debug: Article '{title}' content preview: {content[:100]}...")

    return kb_article_titles, kb_article_contents, workflow_option, template_file


def handle_single_file_workflow():
    kb_article_title = st.text_input('Input a Title for the KB Article')
    kb_article_content = st.text_area('Input the Article Content', height=200)

    uploaded_file = st.file_uploader(
        "Upload a file to import the text into the content field below",
        type=ALLOWED_FILE_TYPES
    )

    if uploaded_file is not None:
        file_content = file_handlers.load_file_content(uploaded_file)
        if file_content:
            kb_article_title = uploaded_file.name
            kb_article_content = file_content
            st.success(f"File '{uploaded_file.name}' loaded successfully!")
        else:
            st.error("Failed to load the file content. Please try again.")

    # Debug output
    st.write(f"Debug: Single file title: {kb_article_title}")
    st.write(f"Debug: Single file content preview: {kb_article_content[:100]}...")

    return [kb_article_title], [kb_article_content]


def handle_multiple_files_workflow():
    uploaded_files = st.file_uploader(
        "Upload files to process",
        type=ALLOWED_FILE_TYPES,
        accept_multiple_files=True
    )

    kb_article_titles = []
    kb_article_contents = []

    if uploaded_files:
        for file in uploaded_files:
            content = file_handlers.load_file_content(file)
            if content:
                kb_article_titles.append(file.name)
                kb_article_contents.append(content)

        st.success(f"Number of files loaded successfully: {len(kb_article_titles)}")

        # Debug output
        for title, content in zip(kb_article_titles, kb_article_contents):
            st.write(f"Debug: Multiple files - '{title}' content preview: {content[:100]}...")
    else:
        st.info("Please upload one or more files to process.")

    return kb_article_titles, kb_article_contents
