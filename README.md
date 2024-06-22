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

- Python 3.11+
- pip (Python package manager)

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
4. Set up your environment variables:
- Copy the `example.env` file to `.env`
- Fill in your API keys and other configuration details

### Running the Application

Launch the Streamlit app:
```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your web browser to use KB Dojo.

## 🛠 Configuration

KB Dojo can be configured to use either standard OpenAI or Azure OpenAI services. Set the appropriate environment variables in your `.env` file to switch between services.

## 📚 Usage

1. Select your workflow (Single File or Multiple Files).
2. Upload your source document(s) or input content directly.
3. Choose AI model and set article options.
4. Click "Generate KB Article" to create your content.
5. Review, download, or further process your generated articles.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- OpenAI for their powerful language models
- Streamlit for making it easy to create web applications with Python
- All the open-source libraries that made this project possible

---

Made with ❤️
