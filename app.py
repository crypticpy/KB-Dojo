import asyncio
import streamlit as st
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, DEFAULT_PROMPT_ROLE
from utils import file_handlers, prompt_utils, pandoc_utils
from layout import main_content, sidebar
import io
import zipfile
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Initialize AsyncOpenAI client
@st.cache_resource
def get_openai_client():
    return AsyncOpenAI(api_key=OPENAI_API_KEY)


async def send_to_openai_api_async(prompt: str, selected_model: str, options: dict) -> str:
    client = get_openai_client()
    try:
        completion = await client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": DEFAULT_PROMPT_ROLE},
                {"role": "user", "content": prompt}
            ],
            temperature=options.get('Temperature', 0.7),
            max_tokens=options.get('Max Tokens', 2000)
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        st.error(f"OpenAI API Error: {str(e)}")
        return None


async def process_article_async(title: str, content: str, options: dict, selected_model: str,
                                template_content: str = None) -> list:
    logger.debug(f"Processing article: {title}")
    logger.debug(f"Initial content: {content[:100]}...")

    results = []
    original_content = content
    processed_content = original_content

    actions = options['Actions']
    perspectives = options['Perspective']
    languages = options['Translation Languages']

    # Step 1: Reauthoring (including template formatting if provided)
    if 'Reauthor Content' in actions or 'Format to Template' in actions:
        processed_content = await reauthor_content(processed_content, template_content, perspectives, selected_model,
                                                   options)
        logger.debug(f"Content after reauthoring and/or formatting: {processed_content[:100]}...")

    # Step 2: Apply perspectives (if not already done in reauthoring)
    if perspectives and 'Reauthor Content' not in actions:
        processed_content = prompt_utils.create_perspective_sections(processed_content, perspectives)
        logger.debug(f"Content after applying perspectives: {processed_content[:100]}...")

    # Step 3: Translation
    if 'Translate' in actions:
        for lang in languages:
            translated_content = await prompt_utils.translate_content(processed_content, lang, selected_model, options)
            logger.debug(f"Translated content ({lang}): {translated_content[:100]}...")

            # Convert markdown to Word
            docx_bytes = pandoc_utils.save_as_word(translated_content)

            results.append((docx_bytes, f"{title}_{lang}", translated_content, lang))
    else:
        # Convert markdown to Word
        docx_bytes = pandoc_utils.save_as_word(processed_content)

        results.append((docx_bytes, title, processed_content, 'Original'))

    return results


async def reauthor_content(content: str, template_content: str, perspectives: list, selected_model: str,
                           options: dict) -> str:
    logger.debug("Reauthoring content")
    prompt = f"Reauthor the following content"

    if template_content:
        prompt += f", using the provided template as a guide for formatting:\n\nTemplate:\n{template_content}\n\nContent to reauthor:"
    else:
        prompt += ", maintaining its core information but improving its clarity, structure, and readability:"

    prompt += f"\n\n{content}\n\n"

    if perspectives:
        prompt += f"Include separate sections for the following perspectives: {', '.join(perspectives)}.\n\n"

    prompt += "Provide the reauthored content directly, without any additional comments or questions."

    reauthored_content = await send_to_openai_api_async(prompt, selected_model, options)
    if reauthored_content is None or reauthored_content.strip() == "":
        logger.error("Reauthoring failed or returned empty content")
        return content  # Return original content if reauthoring fails
    return reauthored_content


async def format_to_template(content: str, template: str, selected_model: str, options: dict) -> str:
    logger.debug("Formatting content to template")
    prompt = f"Format the following content to match the provided template structure, maintaining the original information:\n\nContent:\n{content}\n\nTemplate:\n{template}"
    return await send_to_openai_api_async(prompt, selected_model, options)


async def translate_content(content: str, language: str, selected_model: str, options: dict) -> str:
    logger.debug(f"Translating content to {language}")
    prompt = f"Translate the following content to {language}, maintaining its original structure and formatting. Provide the translated content directly, without any additional comments or questions:\n\n{content}"
    return await send_to_openai_api_async(prompt, selected_model, options)


async def process_multiple_articles_async(titles, contents, options, selected_model, template_content):
    all_results = []
    total_operations = len(titles) * (len(options['Actions']) + (
        len(options['Translation Languages']) if 'Translate' in options['Actions'] else 0))
    progress_bar = st.progress(0)
    completed_operations = 0

    for title, content in zip(titles, contents):
        logger.debug(f"Processing article: {title}")
        results = await process_article_async(title, content, options, selected_model, template_content)
        all_results.extend(results)
        completed_operations += len(options['Actions']) + (
            len(options['Translation Languages']) if 'Translate' in options['Actions'] else 0)
        progress_bar.progress(completed_operations / total_operations)

    return all_results


def main():
    st.set_page_config(page_title="KB Dojo", layout="wide")

    st.markdown("""
        <style>
            .title {
                font-size: 2.5em;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
                color: #4F8BF9;
                animation: glow 2s infinite alternate;
            }
            @keyframes glow {
                0% { filter: drop-shadow(0 0 5px #FFA07A); }
                50% { filter: drop-shadow(0 0 20px #4F8BF9); }
                100% { filter: drop-shadow(0 0 5px #FFA07A); }
            }
        </style>
        <div class="title">KB Dojo</div>
    """, unsafe_allow_html=True)

    if 'results' not in st.session_state:
        st.session_state.results = []

    col1, col2 = st.columns([2, 1])

    with col1:
        kb_article_titles, kb_article_contents, workflow_option, template_file = main_content.setup_main_content()

    with col2:
        options, selected_model = sidebar.setup_sidebar(workflow_option)

    if template_file:
        template_content = file_handlers.load_file_content(template_file, is_template=True)
    else:
        template_content = None

    if st.button('Generate KB Article'):
        logger.debug(f"Workflow option: {workflow_option}")
        logger.debug(f"Selected model: {selected_model}")
        logger.debug(f"Selected options: {options}")

        if workflow_option == "Single File":
            logger.debug(f"Single file content: {kb_article_contents[0][:100]}...")
            st.session_state.results = asyncio.run(
                process_single_article(kb_article_titles[0], kb_article_contents[0], options, selected_model,
                                       template_content))
        else:
            logger.debug(f"Multiple files, number of files: {len(kb_article_titles)}")
            st.session_state.results = asyncio.run(
                process_multiple_articles(kb_article_titles, kb_article_contents, options, selected_model,
                                          template_content))

        display_results(st.session_state.results)


async def process_single_article(title, content, options, selected_model, template_content):
    with st.spinner('Generating KB article...'):
        return await process_article_async(title, content, options, selected_model, template_content)


async def process_multiple_articles(titles, contents, options, selected_model, template_content):
    with st.spinner('Generating KB articles...'):
        return await process_multiple_articles_async(titles, contents, options, selected_model, template_content)


def display_results(results):
    st.subheader("Generated Articles")
    for i, (docx_bytes, title, api_response, lang) in enumerate(results):
        with st.expander(f"{title} - {lang}"):
            st.markdown(api_response)
            if docx_bytes is not None:
                st.download_button(
                    label=f"Download {title} ({lang}) as Word",
                    data=docx_bytes.getvalue(),
                    file_name=f"{title}_{lang}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            else:
                st.error(f"Failed to generate Word document for {title} ({lang})")

    if len(results) > 1:
        create_zip_download(results)


def create_zip_download(results):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for docx_bytes, title, _, lang in results:
            zip_file.writestr(f"{title}_{lang}.docx", docx_bytes.getvalue())

    st.download_button(
        label="Download All Articles as ZIP",
        data=zip_buffer.getvalue(),
        file_name="kb_articles.zip",
        mime="application/zip",
    )


if __name__ == "__main__":
    pandoc_utils.ensure_pandoc()
    main()
