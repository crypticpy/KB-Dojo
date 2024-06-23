import streamlit as st
from config import MODEL_OPTIONS, LANGUAGE_OPTIONS, CONSISTENCY_OPTIONS, USE_AZURE

def setup_sidebar(workflow_option: str):
    options = {}  # Initialize the options dictionary

    with st.sidebar:
        service_name = "Azure OpenAI" if USE_AZURE else "OpenAI"
        st.info(f"Using {service_name} service")

        st.subheader('AI Model Selection')
        selected_model = st.selectbox(
            'Choose AI Model',
            MODEL_OPTIONS,
            index=0,
            format_func=lambda x: x.replace('-', ' ').title()
        )

        st.subheader('KB Article Options')
        options['Actions'] = st.multiselect(
            'Select Actions',
            ['Generate Content', 'Reauthor Content', 'Format to Template', 'Translate'],
            default=['Generate Content']  # Changed default to 'Generate Content'
        )

        options['Translation Languages'] = st.multiselect(
            'Translation Languages',
            LANGUAGE_OPTIONS,
            default=['English']
        )

        options['Perspective'] = st.multiselect(
            'Perspective Sections',
            ['User', 'Support Analyst', 'Administrator']
        )

        if workflow_option == "Multiple Files":
            st.subheader('Consistency Options')
            options['Consistency'] = st.multiselect(
                'Ensure Consistency Across Articles',
                CONSISTENCY_OPTIONS
            )

        st.subheader('Advanced Options')
        options['Temperature'] = st.slider(
            'Temperature',
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Controls randomness in generation. Lower values make output more focused and deterministic."
        )

        options['Max Tokens'] = st.number_input(
            'Max Tokens',
            min_value=100,
            max_value=4000,
            value=3000,
            step=100,
            help="Maximum number of tokens to generate. One token is roughly 4 characters for normal English text."
        )

    return options, selected_model

    return options, selected_model