# Gmail Search & Summarization

This project provides a Gmail Search & Summarization application built with FastMCP, LangChain, and Streamlit. It allows users to authenticate with Gmail, fetch emails based on search queries, and generate summaries using OpenAI agents.

## Features

* **MCP Server**: Exposes a tool (`get_top_mails_for_query`) to query Gmail via OAuth2.
* **Streamlit App**: Web UI for authentication, querying, and displaying summaries.
* **Agent Orchestration**: Uses `autogen_agentchat` for multi-agent coordination (retriever + critic).
* **Configurable**: Easy setup via environment variables and Poetry.

## Prerequisites

* Python 3.12+
* [Poetry](https://python-poetry.org/) for dependency management
* Google Cloud credentials:

  * `GOOGLE_CLIENT_ID`
  * `GOOGLE_CLIENT_SECRET`
  * Optional: `GOOGLE_REDIRECT_URI` (defaults to `http://localhost:8501`)
* OpenAI API key: `OPENAI_API_KEY`
* MCP server URL: `MCP_SERVER_URL`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/NIKHILKUMARREDDY28/Gmail-Insighter.git
   cd Gmail-Insighter
   ```
   
2. Creating the virtual environment:

   ```bash
   conda create -n gmail-insighter python=3.12
   ```
3. Activate the virtual environment:

   ```bash
    conda activate gmail-insighter
   ```


4. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

## Configuration

provide required environment variable values in a `.env` file or export them directly in your shell:

```bash
GOOGLE_CLIENT_ID="your-client-id"
GOOGLE_CLIENT_SECRET="your-client-secret"
OPENAI_API_KEY="your-openai-key"
MCP_SERVER_URL="https://your-mcp-server-url"
# Optional override
GOOGLE_REDIRECT_URI="http://localhost:8501"
```

## Running the Application

1. **Start the MCP server**:

   ```bash
   python mcp_server.py
   ```

2. **Run the Streamlit app**:

   ```bash
   streamlit run main.py
   ```

3. Open your browser to the URL shown by Streamlit (usually `http://localhost:8501`) and authenticate with Gmail.

## Project Structure

```text
.
├── mcp_server.py        # Defines MCP tool for fetching Gmail messages
├── main.py              # Streamlit application for UI and session management
├── agent.py             # Orchestrates retriever & critic agents for summarization
├── config.py            # OAuth setup, prompts, and utility functions
├── pyproject.toml       # Poetry configuration and dependencies
└── README.md            # Project documentation
```

### mcp\_server.py

* Registers a FastMCP tool `get_top_mails_for_query`
* Builds Gmail API client with `googleapiclient`
* Uses `langchain_community.tools.gmail.search.GmailSearch`

### main.py

* Streamlit UI for:

  * OAuth flow via `requests_oauthlib`
  * Query input and chat-like display
  * Fetching & caching summaries with `st.cache_data`

### agent.py

* Defines `get_emails_using_mcp`:

  * Sets up two agents (`email_retriever` & `critic_agent`)
  * Uses `RoundRobinGroupChat` for multi-agent conversation
  * Terminates on `'TERMINATE'` or after function call

### config.py

* Holds constants for OAuth endpoints and scopes
* Defines system prompts for both agents
* Implements `GoogleOAuth` helper class

## Usage Example

1. Click **Connect to Gmail** and complete the OAuth consent screen.
2. Enter a search query in the chat box (e.g., `Get my conversation with amit`).
3. The app retrieves the top matching emails and displays AI-generated summaries.

## Troubleshooting

* **Invalid credentials**: Ensure environment variables are set and valid.
* **Network issues**: Confirm internet connectivity and correct `MCP_SERVER_URL`.
* **Streamlit caching**: Clear the session if stale data persists using the **Clear Conversation** button.

---

