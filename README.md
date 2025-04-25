# Jarvis AI Assistant

A modular and extensible AI assistant system with advanced capabilities in natural language processing, voice interaction, and task automation.

## Features

- **Core AI System**
  - LLM integration with OpenAI and other providers
  - Memory systems (short-term, long-term, vector store)
  - Retrieval-Augmented Generation (RAG)
  - Agentic capabilities with task planning and execution

- **Voice Interface**
  - Speech recognition with Whisper
  - Text-to-speech with ElevenLabs
  - Wake word detection
  - Audio processing utilities

- **Integrations**
  - Smart home control
  - Personal information management
  - External services (weather, news, media)

- **Utilities**
  - Comprehensive logging
  - Security utilities
  - Performance tracking

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- ElevenLabs API key (for voice features)

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Install the package:
   ```bash
   pip install -e .
   ```

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

## Usage

### Starting the Assistant

```bash
# Local installation
jarvis --config config/default_config.yaml

# Docker installation
docker-compose up -d
```

### Basic Commands

- Start voice interaction: Say "Jarvis" followed by your command
- Text interaction: Type your command in the console
- Exit: Say "Goodbye" or press Ctrl+C

### Configuration

The system can be configured through:
- `config/default_config.yaml`: Default configuration
- `config/user_config.yaml`: User-specific overrides
- Environment variables

## Development

### Project Structure

```
jarvis/
├── config/             # Configuration files
├── core/              # Core AI system
├── voice/             # Voice interface
├── integrations/      # External services
├── utils/             # Utility functions
├── data/              # Data storage
├── ui/                # User interface
└── tests/             # Test suite
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=jarvis
```

### Adding New Features

1. Create a new module in the appropriate directory
2. Implement the required interfaces
3. Add configuration options
4. Write tests
5. Update documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT models
- ElevenLabs for voice synthesis
- Whisper for speech recognition
- ChromaDB for vector storage
- All other open-source contributors

## Support

For support, please:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Join our [Discord community](https://discord.gg/jarvis)

## Roadmap

- [ ] Multi-modal capabilities
- [ ] Enhanced security features
- [ ] Mobile app integration
- [ ] Plugin system
- [ ] Cloud deployment options
- [ ] More language support 