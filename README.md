# q2JSON - AI Response to Educational JSON Converter

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)

A Streamlit web application that transforms messy AI/LLM responses into clean, validated JSON questions ready for educational deployment. Built to bridge the gap between AI-generated content and educational platform requirements.

## 🎯 Overview

q2JSON provides a robust 3-stage workflow for converting AI responses into educational assessment materials:

1. **🎯 Prompt Builder** - Generate LLM-optimized prompts for educational question creation
2. **🤖 AI Processing** - Clean and parse AI responses into structured JSON data  
3. **✅ JSON Validation** - Comprehensive validation and export for educational platforms

## 🚀 Key Features

### 🎨 **Intelligent Prompt Generation**
- **LLM-Specific Templates**: Optimized prompts for different AI providers
- **Educational Context Options**: Example, template, or custom input methods
- **Advanced Configuration**: Question types, difficulty levels, explanations
- **LaTeX Support**: Automatic mathematical notation formatting

### 🧹 **Smart Response Processing**
- **Automatic JSON Extraction**: Finds JSON in messy AI responses
- **Format Cleaning**: Removes markdown blocks, fixes quotes, handles Unicode
- **Error Recovery**: Manual editing tools for problematic responses
- **Real-time Validation**: Immediate feedback on JSON structure

### ✅ **Comprehensive Validation**
- **Educational Standards**: Validates question structure and requirements
- **Unicode to LaTeX**: Automatic conversion of mathematical symbols
- **Quality Metrics**: Detailed analysis and success reporting
- **Multiple Export Formats**: Valid questions only, all questions, or detailed reports

## 🤖 LLM Compatibility

Tested and optimized for major AI providers:

| LLM Provider | Compatibility | Template Type | Notes |
|--------------|---------------|---------------|-------|
| **Microsoft Copilot** | ✅ Excellent | Simple | Campus-friendly, minimal prompts |
| **Google Gemini** | ✅ Excellent | Flexible | Works with both simple and detailed |
| **Claude (Anthropic)** | ✅ Good | Detailed | Requires context boundaries |
| **ChatGPT (OpenAI)** | 🔄 Testing | TBD | Evaluation in progress |

## 🏗️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/aknoesen/q2JSON.git
cd q2JSON

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Stage 1: Prompt Builder
1. **Select AI Provider Context**: Choose your target LLM
2. **Enter Educational Context**: Describe your subject and learning objectives
3. **Configure Questions**: Set count, types, and difficulty
4. **Generate Prompt**: Download or copy the optimized prompt
5. **Use with AI**: Paste into your chosen AI provider

### Stage 2: AI Processing
1. **Upload Response**: File upload or direct paste of AI output
2. **Process Response**: Automatic cleaning and JSON extraction
3. **Review Questions**: Preview generated questions and metadata
4. **Manual Edit**: Fix any JSON issues if needed

### Stage 3: JSON Validation
1. **Run Validation**: Comprehensive quality and format checking
2. **Review Results**: Detailed analysis of each question
3. **Export Options**: Choose your preferred output format
4. **Download**: Get clean, validated JSON ready for deployment

## 🎓 Educational Integration

### LMS Compatibility
- **Canvas**: Optimized for Canvas question bank import
- **Moodle**: QTI-compliant output (testing in progress)
- **Generic**: Standard JSON format for custom integrations

### Question Types Supported
- **Multiple Choice**: 4-option questions with distractors
- **True/False**: Boolean assessment questions
- **Numerical**: Calculated answers with tolerance
- **Multiple Dropdowns**: Complex fill-in-the-blank variations

### Quality Features
- **LaTeX Mathematics**: Proper rendering of equations and symbols
- **Educational Metadata**: Topics, subtopics, difficulty levels
- **Feedback Systems**: Explanations for correct and incorrect answers
- **Standards Compliance**: Follows educational assessment best practices

## 🔧 Development

### Project Structure
```
q2JSON/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── templates/               # LLM prompt templates
│   ├── preamble_default.txt
│   └── postamble_default.txt
├── q2validate/              # Validation logic
├── utils/                   # Helper utilities
└── development/             # Development resources
```

### Development Utilities
- `kill-streamlit.bat`: Process management for Windows development
- Comprehensive error handling and logging
- Mobile-responsive design with custom CSS

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔗 Related Projects

This tool is part of the **Q2 Educational Ecosystem**:
- **Q2LMS**: Converts validated JSON to LMS-specific formats
- **Q2Desktop**: Original desktop application version
- **Q2Validate**: Standalone validation library

## 📊 Technical Specifications

### System Requirements
- **Operating System**: Windows, macOS, Linux
- **Python**: 3.8+ (3.9+ recommended)
- **Memory**: 512MB minimum, 1GB recommended
- **Browser**: Modern browser with JavaScript enabled

### Dependencies
- **Streamlit**: Web application framework
- **Pathlib**: File system operations
- **JSON**: Data processing and validation
- **RE**: Pattern matching and text processing

### Performance
- **Startup Time**: < 5 seconds
- **Processing Speed**: 100+ questions per minute
- **Memory Usage**: < 100MB typical operation
- **Browser Compatibility**: Chrome, Firefox, Safari, Edge

## 🐛 Troubleshooting

### Common Issues

**Streamlit won't stop with Ctrl+C (Windows)**
```bash
# Use the provided utility
kill-streamlit.bat

# Or manually kill processes
taskkill /F /IM python.exe
```

**Template files not loading**
- Ensure `templates/` directory exists in project root
- Verify file permissions and encoding (UTF-8)
- Check file paths match exactly: `preamble_default.txt`, `postamble_default.txt`

**AI responses not parsing**
- Try the manual JSON editor in Stage 2
- Check for extra text before/after JSON
- Verify JSON syntax with online validators

**Validation errors**
- Review question structure requirements
- Check LaTeX formatting in mathematical expressions
- Ensure all required fields are present

## 📚 Documentation

### Educational Use Cases
- **Course Development**: Generate assessment questions for any subject
- **Quality Assurance**: Validate AI-generated educational content
- **LMS Integration**: Prepare content for institutional platforms
- **Research**: Compare AI provider capabilities for education

### Best Practices
- **Prompt Engineering**: Use specific, detailed educational contexts
- **Quality Control**: Always validate before deployment
- **Template Management**: Customize templates for your institution
- **Version Control**: Track changes to question sets over time

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **aknoesen** - *Initial work and development*

## 🙏 Acknowledgments

- Educational technology community for feedback and testing
- Streamlit team for the excellent web framework
- AI/LLM providers for making educational AI accessible
- Campus IT departments for deployment guidance

## 📞 Support

For questions, issues, or contributions:
- **GitHub Issues**: [Report bugs or request features](https://github.com/aknoesen/q2JSON/issues)
- **Discussions**: [Community discussion](https://github.com/aknoesen/q2JSON/discussions)
- **Documentation**: [Wiki pages](https://github.com/aknoesen/q2JSON/wiki)

---

**Built for Educators, by Educators** 🎓  
*Making AI-powered educational content creation reliable, validated, and ready for the classroom.*