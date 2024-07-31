import asyncio
import streamlit as st
from openai import AzureOpenAI
from config import DEFAULT_PROMPT_ROLE, TITLE_STYLE, AZURE_OPENAI_API_KEY, \
    AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME
from utils import file_handlers, prompt_utils, pandoc_utils
from layout import main_content, sidebar
import io
import zipfile
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def debug_print(message):
    if st.session_state.debug_mode:
        st.write(f"DEBUG: {message}")

# Initialize AsyncOpenAI client
@st.cache_resource
def get_openai_client():
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

async def send_to_openai_api_async(prompt: str, options: dict) -> str:
    client = get_openai_client()
    try:
        completion = await client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": DEFAULT_PROMPT_ROLE},
                {"role": "user", "content": prompt}
            ],
            temperature=options.get('Temperature', 0.7),
            max_tokens=options.get('Max Tokens', 2000)
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        error_message = f"Azure OpenAI API Error: {str(e)}"
        logger.error(error_message)
        if st.session_state.debug_mode:
            st.error(error_message)
        else:
            st.error("An error occurred while processing your request. Please try again.")
        return None

async def process_article_async(title: str, content: str, options: dict,
                                template_content: str = None) -> list:
    debug_print(f"Processing article: {title}")
    debug_print(f"Initial content: {content[:100]}...")

    results = []
    original_content = content
    processed_content = original_content

    actions = options['Actions']
    perspectives = options['Perspective']
    languages = options['Translation Languages']

    # Step 1: Generate or Reauthor Content
    if 'Generate Content' in actions:
        processed_content = await generate_content(title, content, perspectives, options)
        debug_print(f"Content after generation: {processed_content[:100]}...")
    elif 'Reauthor Content' in actions or 'Format to Template' in actions:
        processed_content = await reauthor_content(processed_content, template_content, perspectives, options)
        debug_print(f"Content after reauthoring and/or formatting: {processed_content[:100]}...")

    # Step 2: Apply perspectives (if not already done in reauthoring)
    if perspectives and 'Reauthor Content' not in actions:
        processed_content = prompt_utils.create_perspective_sections(processed_content, perspectives)
        debug_print(f"Content after applying perspectives: {processed_content[:100]}...")

    # Step 3: Translation
    if 'Translate' in actions:
        for lang in languages:
            translated_content = await prompt_utils.translate_content(processed_content, lang, options)
            debug_print(f"Translated content ({lang}): {translated_content[:100]}...")

            # Convert markdown to Word
            docx_bytes = pandoc_utils.save_as_word(translated_content)

            results.append((docx_bytes, f"{title}_{lang}", translated_content, lang))
    else:
        # Convert markdown to Word
        docx_bytes = pandoc_utils.save_as_word(processed_content)

        results.append((docx_bytes, title, processed_content, 'Original'))

    return results

async def generate_content(title: str, content: str, perspectives: list, options: dict) -> str:
    debug_print("Generating content")
    prompt = f"Generate a detailed knowledge base article based on the following title and content. If the content is a specific request (e.g., 'write a recipe for chocolate cake'), create an article that fulfills that request. Title: {title}\n\nContent or Request: {content}\n\n"

    if perspectives:
        prompt += f"Include separate sections for the following perspectives: {', '.join(perspectives)}.\n\n"

    prompt += "Provide the generated content in markdown format, without any additional comments or questions."

    generated_content = await send_to_openai_api_async(prompt, options)
    if generated_content is None or generated_content.strip() == "":
        logger.error("Content generation failed or returned empty content")
        return content  # Return original content if generation fails
    return generated_content

async def reauthor_content(content: str, template_content: str, perspectives: list, options: dict) -> str:
    debug_print("Reauthoring content")
    prompt = "Reauthor the following content"

    if not content.strip():
        prompt = "Generate a knowledge base article based on the following template:"

    if template_content:
        prompt += f", using the provided template as a guide for formatting:\n\nTemplate:\n{template_content}\n\nContent to reauthor:"
    else:
        prompt += ", maintaining its core information but improving its clarity, structure, and readability:"

    prompt += f"\n\n{content}\n\n"

    if perspectives:
        prompt += f"Include separate sections for the following perspectives: {', '.join(perspectives)}.\n\n"

    prompt += "Provide the reauthored content directly, without any additional comments or questions."

    reauthored_content = await send_to_openai_api_async(prompt, options)
    if reauthored_content is None or reauthored_content.strip() == "":
        logger.error("Reauthoring failed or returned empty content")
        return content  # Return original content if reauthoring fails
    return reauthored_content

async def format_to_template(content: str, template: str, options: dict) -> str:
    debug_print("Formatting content to template")
    prompt = f"Format the following content to match the provided template structure, maintaining the original information:\n\nContent:\n{content}\n\nTemplate:\n{template}"
    return await send_to_openai_api_async(prompt, options)

async def process_multiple_articles_async(titles, contents, options, template_content):
    all_results = []
    total_operations = len(titles) * (len(options['Actions']) + (
        len(options['Translation Languages']) if 'Translate' in options['Actions'] else 0))
    progress_bar = st.progress(0)
    completed_operations = 0

    for title, content in zip(titles, contents):
        debug_print(f"Processing article: {title}")
        results = await process_article_async(title, content, options, template_content)
        all_results.extend(results)
        completed_operations += len(options['Actions']) + (
            len(options['Translation Languages']) if 'Translate' in options['Actions'] else 0)
        progress_bar.progress(completed_operations / total_operations)

    return all_results

def main():
    st.set_page_config(page_title="KB Dojo", layout="wide")

    st.markdown(TITLE_STYLE, unsafe_allow_html=True)
    st.markdown('<div class="kb-dojo-title">KB Dojo</div>', unsafe_allow_html=True)
    st.markdown("""
        <style>
            .generated-content {
                font-family: Arial, sans-serif;
                color: var(--text-color);
            }
            .generated-content h1 {
                font-size: 1.8em;
                color: var(--header-color);
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 0.3em;
            }
            .generated-content h2 {
                font-size: 1.5em;
                color: var(--header-color);
            }
            .generated-content h3 {
                font-size: 1.3em;
                color: var(--header-color);
            }
            .generated-content p {
                font-size: 1em;
                line-height: 1.6;
                margin-bottom: 1em;
            }
            .generated-content ul, .generated-content ol {
                margin-bottom: 1em;
                padding-left: 2em;
            }
            .generated-content li {
                margin-bottom: 0.5em;
            }
            .generated-content code {
                background-color: var(--code-bg-color);
                color: var(--code-text-color);
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: monospace;
            }
            /* Light mode */
            @media (prefers-color-scheme: light) {
                .generated-content {
                    --text-color: #0a0a0a;  /* Very dark gray, almost black */
                    --header-color: #000000;  /* Pure black for headers */
                    --border-color: #cccccc;
                    --code-bg-color: #f0f0f0;
                    --code-text-color: #0a0a0a;
                }
            }
            /* Dark mode */
            @media (prefers-color-scheme: dark) {
                .generated-content {
                    --text-color: #e0e0e0;
                    --header-color: #ffffff;
                    --border-color: #555555;
                    --code-bg-color: #2a2a2a;
                    --code-text-color: #f0f0f0;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    if 'results' not in st.session_state:
        st.session_state.results = []

    col1, col2 = st.columns([2, 1])

    with col1:
        kb_article_titles, kb_article_contents, workflow_option, template_file = main_content.setup_main_content()

    with col2:
        options = sidebar.setup_sidebar(workflow_option)

    # Set debug mode in session state
    st.session_state.debug_mode = options.get('Debug Mode', False)

    if template_file:
        template_content = file_handlers.load_file_content(template_file, is_template=True)
    else:
        template_content = None

    if st.button('Generate KB Article'):
        debug_print(f"Workflow option: {workflow_option}")
        debug_print(f"Selected options: {options}")

        if workflow_option == "Single File":
            debug_print(f"Single file content: {kb_article_contents[0][:100]}...")
            st.session_state.results = asyncio.run(
                process_single_article(kb_article_titles[0], kb_article_contents[0], options, template_content))
        else:
            debug_print(f"Multiple files, number of files: {len(kb_article_titles)}")
            st.session_state.results = asyncio.run(
                process_multiple_articles(kb_article_titles, kb_article_contents, options, template_content))

        display_results(st.session_state.results)

    if st.session_state.debug_mode:
        st.subheader("Debug Information")
        st.json({
            "Workflow Option": workflow_option,
            "Options": options,
            "Number of Articles": len(kb_article_titles),
            "Template Used": template_file is not None,
        })

async def process_single_article(title, content, options, template_content):
    with st.spinner('Generating KB article...'):
        return await process_article_async(title, content, options, template_content)

async def process_multiple_articles(titles, contents, options, template_content):
    with st.spinner('Generating KB articles...'):
        return await process_multiple_articles_async(titles, contents, options, template_content)

def display_results(results):
    st.subheader("Generated Articles")
    for docx_bytes, title, api_response, lang in results:
        with st.expander(f"{title} - {lang}"):
            st.markdown(f'<div class="generated-content">{api_response}</div>', unsafe_allow_html=True)
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