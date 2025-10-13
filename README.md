# Todo App

An AI-powered agile development team simulation for managing todo tasks.

## Description

This project implements an AI-powered agile development team that can help manage and organize todo tasks. It uses LangChain with Ollama for AI capabilities and includes GitHub integration.

## Prerequisites

- Python 3.8 or higher
- Ollama installed locally (https://ollama.com/)
- Required Ollama models:
  - `mistral:7b`
  - `codellama:7b`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/daz2d/todo-app.git
   cd todo-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Ollama and required models:
   ```bash
   ollama pull mistral:7b
   ollama pull codellama:7b
   ```

## Usage

Run the demo:
```bash
python demo_agile_team.py
```

Or use the agile development team directly:
```bash
python agile_dev_team.py
```

## Files

- `agile_dev_team.py` - Main agile development team implementation
- `demo_agile_team.py` - Demo script showing the team in action
- `requirements.txt` - Python package dependencies

## License

This project is open source and available under the MIT License.