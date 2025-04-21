# Email Assistant

An AI-powered email assistant built with LangGraph, LangChain, and Azure OpenAI that helps users manage their emails through automated triage, response generation, and memory-based learning.

## Project Structure

```
emailAssistance/
├── docs/                   # Documentation
│   ├── technical_blog_english.md           
│   └── technical_blog_japanese.md        
├── logs/                   # Log files
│   └── email_logs/         # Email specific logs
├── scripts/                # Scripts for running the application
│   └── run.sh              # Main run script
├── src/                    # Source code
│   ├── app/                # Web interface
│   │   ├── __init__.py
│   │   └── interface.py    # Gradio interface
│   ├── core/               # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration
│   │   ├── models.py       # Data models
│   │   └── prompts.py      # System prompts
│   ├── memory/             # Memory management
│   │   ├── __init__.py
│   │   └── manager.py      # Memory operations
│   ├── tools/              # Agent tools
│   │   ├── __init__.py
│   │   ├── actions.py      # Email and calendar tools
│   │   └── memory.py       # Memory tools
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   └── logger.py       # Logging functionality
│   ├── workflow/           # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── graph.py        # Workflow definition
│   │   ├── response.py     # Response agent
│   │   └── triage.py       # Triage functionality
│   ├── __init__.py         # Package marker
│   └── main.py             # Entry point
├── .env                    # Environment variables (create this)
└── requirements.txt        # Dependencies
```

## Features

- **Email Triage**: Automatically classify incoming emails as 'ignore', 'notify', or 'respond'
- **Response Generation**: Create contextually appropriate replies for emails
- **Calendar Management**: Check availability and schedule meetings
- **Memory System**: Learn from interactions and improve over time:
  - **Semantic Memory**: Store facts and user preferences
  - **Episodic Memory**: Learn from past examples
  - **Procedural Memory**: Update behavior based on feedback

## Installation

Python 3.11 or higher is required. Follow these steps to set up the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/givery-technology/ai-lab-email-assistant.git
   cd ai-lab-email-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_model
   ```

## Usage

Run the application using the provided script:

```bash
./scripts/run.sh
```

Or directly with Python:

```bash
python -m src.main
```

This will start the Gradio web interface, which you can access in your browser at http://localhost:7860.

## Development

The project is organized into modules:

- `app`: Web interface with Gradio
- `core`: Essential components like configuration and data models
- `memory`: Memory management functionality
- `tools`: Agent tools for email, calendar, and memory operations
- `utils`: Utility functions and logging
- `workflow`: LangGraph workflow definition




