# Azure AI Avatar - Python/Streamlit Version

A Python implementation of the Azure AI Avatar application using Streamlit for the frontend, Azure Speech Services for TTS/Avatar, and Azure OpenAI for intelligent conversations with optional RAG capabilities.

## Features

- 🎭 **Azure Avatar Integration** - Interactive AI avatar using Azure Text-to-Speech
- 💬 **Azure OpenAI Chat** - Intelligent conversations powered by Azure OpenAI
- 🔍 **RAG Support** - Optional integration with Azure Cognitive Search for grounded responses
- 🎤 **Multi-language STT** - Support for multiple languages in speech-to-text
- 🎨 **Customizable Avatar** - Choose different characters and styles
- 📝 **Chat History** - Maintain conversation context
- 🌐 **Streamlit UI** - Clean, intuitive web interface

## Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Azure Speech Services
  - Azure OpenAI Service
  - Azure Cognitive Search (optional, for RAG)

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd azure-ai-avatar-python
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables** (Optional)
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

## Project Structure

```
azure-ai-avatar-python/
├── app.py                  # Main Streamlit application
├── config.py              # Configuration management
├── avatar_service.py      # Azure Speech/Avatar service
├── openai_service.py      # Azure OpenAI service
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Configuration

You can configure the application in two ways:

1. **Through the UI** - Use the sidebar to input your Azure credentials and settings
2. **Through .env file** - Set default values in the `.env` file

#### Required Settings:

**Azure Speech Service:**
- Region (e.g., westus2, eastus)
- API Key

**Azure OpenAI Service:**
- Endpoint URL
- API Key
- Deployment Name

#### Optional Settings:

**Azure Cognitive Search** (for RAG):
- Endpoint URL
- API Key
- Index Name

**Avatar Configuration:**
- Character (default: meg)
- Style (default: formal)

**TTS Configuration:**
- Voice (default: en-US-AvaMultilingualNeural)
- STT Locales (comma-separated language codes)

### Using the Application

1. **Configure Services**: Enter your Azure credentials in the sidebar
2. **Open Session**: Click "Open Avatar Session" to connect to Azure services
3. **Chat**: Type your message in the text area and click "Send Message"
4. **Listen**: The avatar will speak the AI's response
5. **Control**: Use the control buttons to manage the conversation:
   - Stop Speaking - Interrupt current speech
   - Clear Chat History - Reset the conversation
   - Close Avatar Session - End the session

## Features Explanation

### Avatar Service (`avatar_service.py`)
- Manages Azure Speech SDK for TTS
- Handles avatar synthesis with character and style
- Creates SSML for speech generation
- Manages speech queue for continuous speaking

### OpenAI Service (`openai_service.py`)
- Manages chat completions with Azure OpenAI
- Supports both streaming and non-streaming responses
- Integrates with Azure Cognitive Search for RAG
- Maintains conversation history

### Configuration (`config.py`)
- Centralized configuration management
- Validation of required settings
- Helper methods for endpoint construction

## Advanced Features

### On Your Data (RAG)

Enable "On Your Data" in the sidebar and provide Azure Cognitive Search credentials to ground AI responses in your own documents.

### Continuous Conversation

Enable this to maintain longer conversation context without manual session management.

### Custom Voices

Modify the `tts_voice` setting to use different Azure TTS voices. Available voices:
- en-US-AvaMultilingualNeural
- en-US-JennyNeural
- en-US-GuyNeural
- And many more...

## Troubleshooting

### Common Issues

1. **"Speech API key is required"**
   - Ensure you've entered your Azure Speech API key in the sidebar

2. **"Failed to start session"**
   - Verify all required credentials are correct
   - Check that your Azure resources are active
   - Ensure you have sufficient quota

3. **No audio output**
   - Check your system audio settings
   - Verify the TTS voice is available in your region

4. **Streaming issues**
   - Ensure stable internet connection
   - Check Azure service status

## Limitations

- **WebRTC Video**: Full avatar video streaming requires WebRTC implementation (not included in basic Streamlit)
- **Microphone**: Live microphone input requires additional WebRTC/browser integration
- **Browser Compatibility**: Best experienced in modern browsers (Chrome, Edge, Firefox)

## Development

### Adding New Features

1. **Custom Avatar Characters**: Modify `avatar_character` options in the config
2. **Additional Languages**: Add language codes to `stt_locales`
3. **Custom Prompts**: Modify `system_prompt` in the sidebar

### Testing

```bash
# Run basic tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

## API Versions

This implementation uses:
- Azure Speech SDK: 1.31.0+
- Azure OpenAI API: 2023-06-01-preview
- Streamlit: 1.28.0+

## Security Notes

⚠️ **Important Security Considerations:**

- Never commit API keys to version control
- Use environment variables or Azure Key Vault for production
- Implement proper authentication for production deployments
- Enable private endpoints for enhanced security

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Resources

- [Azure Speech Documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [Azure Cognitive Search Documentation](https://docs.microsoft.com/azure/search/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## Support

For issues and questions:
- Check the Azure documentation
- Review Streamlit community forums
- Open an issue in this repository

---

**Note**: This is a Python/Streamlit port of the original JavaScript implementation. Some features (like full WebRTC video streaming) require additional implementation for web browser compatibility.