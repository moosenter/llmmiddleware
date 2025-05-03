# LLM Middleware

A PocketFlow-based middleware for generating SQL queries from natural language questions, executing them, and visualizing the results.

## Overview

LLM Middleware is a comprehensive solution that leverages Large Language Models to translate natural language questions about data into SQL queries. The application:

- Generates SQL from natural language questions
- Validates and executes queries against your database
- Provides data visualization with auto-generated charts
- Suggests follow-up questions based on query results
- Summarizes data insights in natural language

Built with the [PocketFlow](https://github.com/the-pocket/PocketFlow) framework, this project demonstrates how to build complex LLM applications using a minimalist, composable architecture.

## Project Structure

The project follows PocketFlow's recommended structure:

```
.
├── app.py                      # Streamlit web application
├── main.py                     # Main entry point
├── config/                     # Configuration files
│   ├── AppConfig.yaml          # Application configuration
│   └── ModelConfig.yaml        # LLM model configuration
├── llmmiddleware/              # Core package
│   ├── core/                   # Core framework code
│   │   └── pocketflow.py       # 100-line PocketFlow implementation
│   ├── flows/                  # Flow definitions
│   │   └── sql_flows.py        # SQL generation and execution flows
│   ├── nodes/                  # Node definitions
│   │   └── sql_nodes.py        # Nodes for SQL generation pipeline
│   ├── utils/                  # Utility functions
│   │   └── call_vanna.py       # Vanna API wrapper
│   ├── lib/                    # Additional libraries
│   │   └── vanna/              # Vanna integration for SQL generation
│   ├── docs/                   # Documentation
│   │   ├── design.md           # System design document
│   │   └── testing_report.md   # Testing documentation
│   └── tests/                  # Test cases
├── docker-compose.yaml         # Docker compose configuration
├── Dockerfile.backend          # Dockerfile for the backend
├── Dockerfile.frontend         # Dockerfile for the frontend
├── requirements.txt            # Python dependencies
└── requirements-frontend.txt   # Frontend dependencies
└── setup.py                    # Setup file
```

## Features

- **Natural Language to SQL**: Convert questions into optimized SQL queries
- **Multi-LLM Support**: Compatible with OpenAI, Anthropic, Groq, Hugging Face, and Azure models
- **Data Visualization**: Automatically generate appropriate charts based on query results
- **Follow-up Suggestions**: Get intelligent follow-up questions to explore your data further
- **Data Summarization**: Receive natural language summaries of query results
- **Modular Design**: Built on PocketFlow's composable architecture

## Installation

### Prerequisites
- Python 3.8+
- SQLite database (or other supported databases)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llmmiddleware.git
cd llmmiddleware
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment:
   - Update `config/AppConfig.yaml` with your database paths
   - Update `config/ModelConfig.yaml` with your preferred LLM providers

## Running the Application

### Direct Execution

```bash
# Run the Streamlit web interface
streamlit run app.py

# Run the backend API
python main.py
```

### Docker Deployment

```bash
docker-compose up
```

## Development

To extend the middleware:
1. Add new nodes in `llmmiddleware/nodes/`
2. Create new flows in `llmmiddleware/flows/`
3. Add utility functions in `llmmiddleware/utils/`

For detailed design documentation, see `llmmiddleware/docs/design.md`. 