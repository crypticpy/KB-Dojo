import re
import os
from openai import AzureOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME

import streamlit as st

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)


def validate_headers_and_numbers(content: str) -> str:
    """
    Validate headers and document numbers in the content.
    Ensure they're correct or leave them blank.

    Args:
        content: The article content.

    Returns:
        The validated article content.
    """
    if "Header" not in content:
        content = "Header: \n" + content
    if "Document Number" not in content:
        content = "Document Number: \n" + content
    return content


def create_perspective_sections(content: str, perspectives: list) -> str:
    """
    Create sections for different perspectives within the content.

    Args:
        content: The article content.
        perspectives: A list of perspectives to create sections for.

    Returns:
        The article content with perspective sections.
    """
    sections = []
    for perspective in perspectives:
        sections.append(f"### {perspective} Section\n\n{content}\n")
    return "\n".join(sections)


def create_base_prompt(title: str, content: str, template_content: str = None, options: dict = None) -> str:
    """
    Create the base prompt for the OpenAI API.

    Args:
        title: The title of the article.
        content: The content of the article.
        template_content: The content of the template, if provided.
        options: The selected options for the article.

    Returns:
        The base prompt as a string.
    """
    if template_content:
        return f"\n- Construct a KB article from the following user information using the provided template: Title\n\n{title}\n\nContent\n\n{content}\n\nTemplate\n\n{template_content}\n\n"
    else:
        return f"\n- Construct a KB article from the following user information: Title\n\n{title}\n\nContent\n\n{content}\n\n"


def modify_prompt_with_options(prompt: str, options: dict) -> str:
    """
    Modify the prompt based on the selected options.

    Args:
        prompt: The base prompt.
        options: The selected options for the article.

    Returns:
        The modified prompt as a string.
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


async def translate_content(content: str, language: str, selected_model: str, options: dict) -> str:
    """
    Translate the given content to the specified language while preserving markdown formatting.

    Args:
        content: The content to translate.
        language: The target language for translation.
        selected_model: The OpenAI model to use for translation.
        options: Additional options for the API call.

    Returns:
        The translated content with preserved markdown formatting.
    """
    prompt = f"""Translate the following markdown-formatted text to {language}. 
    Maintain all markdown formatting, including headers, bold text, italics, lists, and code blocks.
    Ensure that the structure and formatting of the original text is preserved in the translation.
    Here's the text to translate:

    {content}
    """

    try:
        completion = await client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a professional translator skilled in preserving markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=options.get('Temperature', 0.1),
            max_tokens=options.get('Max Tokens', 4000)
        )
        translated_content = completion.choices[0].message.content.strip()
        return translated_content
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return content  # Return original content if translation fails

