# Google ADK Project

This project provides tools and utilities for working with Google's AI Development Kit (ADK).

## Project Structure

```
.
├── GEMINI.md            # Documentation for Gemini integration
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── multi_tool_agent/    # Main package directory
    ├── __init__.py      # Package initialization
    ├── .env             # Environment variables
    ├── agent.py         # Main agent implementation
    └── README.md        # Agent-specific documentation
```

## Requirements

### Python Version
- Python 3.9 or higher

### Python Libraries
- `google-generativeai` (for `google.adk.agents.Agent`)
- `datetime` (standard library)
- `zoneinfo` (standard library, available in Python 3.9+)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-repo/google-adk.git
cd google-adk
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Import and use the agent:
```python
from multi_tool_agent.agent import Agent

agent = Agent()
# Use agent methods...
```

## Documentation

- See [GEMINI.md](GEMINI.md) for Gemini-specific documentation
- See [multi_tool_agent/README.md](multi_tool_agent/README.md) for agent implementation details
