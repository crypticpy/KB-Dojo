import logging
import streamlit as st
import aiohttp
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME

logger = logging.getLogger(__name__)


def debug_print(message):
    if st.session_state.get('debug_mode', False):
        st.write(f"DEBUG: {message}")


def validate_headers_and_numbers(content: str) -> str:
    """
    Validate headers and document numbers in the content.
    Ensure they're correct or leave them blank.
    """
    if "Header" not in content:
        content = "Header: \n" + content
    if "Document Number" not in content:
        content = "Document Number: \n" + content
    return content


def create_perspective_sections(content: str, perspectives: list) -> str:
    """
    Create sections for different perspectives within the content.
    """
    sections = [
        f"### {perspective} Section\n\n{content}\n"
        for perspective in perspectives
    ]
    return "\n".join(sections)


def create_base_prompt(title: str, content: str, template_content: str = None, options: dict = None) -> str:
    """
    Create the base prompt for the OpenAI API.
    """
    if template_content:
        return f"\n- Construct a KB article from the following user information using the provided template: Title\n\n{title}\n\nContent\n\n{content}\n\nTemplate\n\n{template_content}\n\n"
    else:
        return f"\n- Construct a KB article from the following user information: Title\n\n{title}\n\nContent\n\n{content}\n\n"


def modify_prompt_with_options(prompt: str, options: dict) -> str:
    """
    Modify the prompt based on the selected options.
    """
    consistency_prompt = "Consistency requirements:\n"
    for option, value in options.items():
        if option.startswith("Consistent") and value:
            consistency_prompt += f"- {option}\n"
    prompt += f"\n{consistency_prompt}"

    if options.get('Action') == 'Reauthor Content':
        prompt = "Reauthor the following content, maintaining its core information but improving its clarity, structure, and readability. Follow KCS 6 standards and write for Service Now KB publication:\n\n" + prompt
    elif options.get('Action') == 'Format to Template':
        prompt = "Format the following content to match the provided template structure, maintaining the original information as much as possible:\n\n" + prompt

    return prompt


async def send_to_openai_api_async(prompt: str, options: dict) -> str:
    async with aiohttp.ClientSession() as session:
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        }
        payload = {
            "model": AZURE_OPENAI_DEPLOYMENT_NAME,
            "messages": [
                {"role": "system",
                 "content": "You are a professional translator skilled in preserving markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            "temperature": options.get('Temperature', 0.1),
            "max_tokens": options.get('Max Tokens', 4000)
        }
        url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

        try:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    error_message = f"Azure OpenAI API Error: {response.status} - {await response.text()}"
                    logger.error(error_message)
                    if options.get('Debug Mode', False):
                        st.error(error_message)
                    else:
                        st.error("An error occurred while processing your request. Please try again.")
                    return None
        except Exception as e:
            error_message = f"Azure OpenAI API Error: {str(e)}"
            logger.error(error_message)
            if options.get('Debug Mode', False):
                st.error(error_message)
            else:
                st.error("An error occurred while processing your request. Please try again.")
            return None


async def translate_content(content: str, language: str, options: dict) -> str:
    """
    Translate the given content to the specified language while preserving markdown formatting.
    """
    debug_print(f"Translating content to {language}")
    prompt = f"""Translate the following markdown-formatted text to {language}. 
    Maintain all markdown formatting, including headers, bold text, italics, lists, and code blocks.
    Ensure that the structure and formatting of the original text is preserved in the translation.
    Here's the text to translate:

    {content}
    """

    try:
        translated_content = await send_to_openai_api_async(prompt, options)
        return translated_content
    except Exception as e:
        error_message = f"Translation error: {str(e)}"
        logger.error(error_message)
        if options.get('Debug Mode', False):
            st.error(error_message)
        else:
            st.error("An error occurred during translation. Please try again.")
        return content  # Return original content if translation fails
