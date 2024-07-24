# KB Dojo 🥋

KB Dojo is an advanced Knowledge Base article generation tool powered by AI. It streamlines the process of creating, reauthoring, and translating KB articles, making knowledge management effortless and efficient.

## 🌟 Features

- **AI-Powered Content Generation**: Leverage OpenAI or Azure OpenAI to create high-quality KB articles.
- **Flexible Input**: Work with single files or batch process multiple documents.
- **Multi-Language Support**: Translate your KB articles into multiple languages.
- **Template Formatting**: Format your content to match specific templates.
- **Perspective Sections**: Generate content from different viewpoints (User, Support Analyst, Administrator).
- **Consistency Control**: Ensure standardized terminology and formatting across articles.
- **File Type Support**: Process PDF, DOCX, and TXT files.
- **Export Options**: Download articles as Word documents or in bulk as a ZIP file.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Pandoc (document conversion tool)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kbdojo.git
cd kbdojo
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Install Pandoc:
   - For Ubuntu/Debian: `sudo apt-get install pandoc`
   - For macOS (using Homebrew): `brew install pandoc`
   - For Windows: Download the installer from [Pandoc's website](https://pandoc.org/installing.html)

5. Set up your environment variables:
   - Copy the `example.env` file to `.env`
   - Fill in your API keys and other configuration details:
     ```
     OPENAI_API_KEY=your_openai_api_key
     AZURE_OPENAI_API_KEY=your_azure_openai_api_key
     AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
     AZURE_OPENAI_API_VERSION=2023-05-15
     ```

6. (Optional) Prepare a reference Word document:
   - Create a Word document named `reference.docx` in the project root directory.
   - This document will be used as a template for styling the generated Word documents.
   - If not provided, Pandoc's default styling will be used.

### Running the Application

Launch the Streamlit app:
```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your web browser to use KB Dojo.

## 🛠 Configuration

KB Dojo can be configured to use either standard OpenAI or Azure OpenAI services. The application automatically detects which service to use based on the provided environment variables:

- If both `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are set, it will use Azure OpenAI.
- Otherwise, it will use the standard OpenAI service with the `OPENAI_API_KEY`.

## 📚 Usage

1. Select your workflow:
   - **Single File**: Process one document or input content directly.
   - **Multiple Files**: Batch process multiple documents.

2. Upload your source document(s) or input content:
   - Supported file types: PDF, DOCX, TXT
   - For multiple files, you can upload several documents at once.

3. (Optional) Upload a template document:
   - This can be used to format your content according to a specific structure.

4. Choose AI model and set article options:
   - Select the AI model (options depend on whether you're using OpenAI or Azure OpenAI).
   - Choose actions: Generate Content, Reauthor Content, Format to Template, Translate.
   - Select translation languages (if applicable).
   - Add perspective sections (User, Support Analyst, Administrator).
   - Set consistency options for multiple files.
   - Adjust advanced options like temperature and max tokens.

5. Click "Generate KB Article" to create your content.

6. Review the generated content:
   - The content will be displayed in expandable sections.
   - You can download individual articles as Word documents.
   - For multiple articles, you can download all as a ZIP file.

## 🔧 Troubleshooting

- If you encounter issues with Pandoc, ensure it's correctly installed and accessible from the command line.
- Make sure your `.env` file is properly configured with the necessary API keys.
- If using Azure OpenAI, verify that your deployment names match the model options in the config file.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- OpenAI and Azure for their powerful language models
- Streamlit for making it easy to create web applications with Python
- Pandoc for document conversion capabilities
- All the open-source libraries that made this project possible

---

Made with ❤️ by Christopher Collins
