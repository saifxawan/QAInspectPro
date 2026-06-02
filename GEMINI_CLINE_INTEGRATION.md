# Gemini AI Integration with Cline

This guide explains how to integrate Google's Gemini AI with Cline using the Model Context Protocol (MCP).

## Overview

This integration allows Cline (the VS Code AI assistant) to use Google's Gemini models for code generation, analysis, and other AI-assisted tasks. The integration is built using MCP (Model Context Protocol), which provides a standardized way for AI assistants to connect to different AI models and tools.

## Prerequisites

1. **Python 3.9+** installed on your system
2. **Cline VS Code extension** installed
3. **Google Gemini API key** - Already configured in `.env` file

## Installation Steps

### Step 1: Install Dependencies

Navigate to your project directory and install the required Python packages:

```bash
pip install google-genai mcp
```

Or if you want to install all project dependencies including the Gemini integration:

```bash
pip install -r backend/requirements.txt
```

### Step 2: Configure API Key

The API key is already configured in the `.env` file. If you need to update it:

1. Edit the `.env` file in the project root
2. Update the `GEMINI_API_KEY` value with your API key

**Important:** The `.env` file is in `.gitignore` and should never be committed to version control.

### Step 3: Configure Cline to Use the MCP Server

You need to configure Cline to recognize and use the Gemini MCP server. There are two ways to do this:

#### Option A: Using Cline's MCP Settings UI

1. Open VS Code
2. Click on the Cline extension icon in the sidebar
3. Go to Cline Settings → MCP Servers
4. Click "Add New MCP Server"
5. Fill in the configuration:
   - **Name**: `Gemini AI`
   - **Command**: `python`
   - **Args**: `/full/path/to/your/project/gemini_mcp_server.py`
   - **Environment Variables**: 
     ```
     GEMINI_API_KEY=AIzaSyDTA3clPI2IXMNLKzHMuxiHlJwHn8yRqlg
     ```

#### Option B: Manual Configuration File

Create or edit the Cline MCP configuration file at `~/.vscode/extensions/saoudrizwan.cline-<version>/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "gemini": {
      "command": "python",
      "args": ["/full/path/to/your/project/gemini_mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "AIzaSyDTA3clPI2IXMNLKzHMuxiHlJwHn8yRqlg"
      }
    }
  }
}
```

**Note:** Replace `/full/path/to/your/project/` with the actual absolute path to your project directory (e.g., `s:\SAIFI\PROJECTS\SQA_Project\gemini_mcp_server.py` on Windows or `/home/user/projects/SQA_Project/gemini_mcp_server.py` on Linux/Mac).

### Step 4: Verify Installation

1. Restart VS Code to ensure Cline picks up the new MCP server configuration
2. Open Cline and ask it to use Gemini (e.g., "Use Gemini to help me write a Python function")
3. Cline should now have access to the Gemini tools

## Available Tools

Once integrated, Cline can use the following Gemini tools:

### 1. `gemini_generate`
Generate content using Gemini with thinking capabilities.

**Parameters:**
- `prompt` (required): The text prompt to send to Gemini
- `thinking_level` (optional): LOW, MEDIUM, or HIGH (default: HIGH)
- `model` (optional): Specific Gemini model to use

### 2. `gemini_generate_stream`
Stream content generation for real-time responses.

**Parameters:**
- `prompt` (required): The text prompt to send to Gemini
- `thinking_level` (optional): LOW, MEDIUM, or HIGH (default: HIGH)
- `model` (optional): Specific Gemini model to use

### 3. `gemini_chat`
Multi-turn conversation with Gemini AI.

**Parameters:**
- `messages` (required): Array of conversation messages with `role` and `content`
- `thinking_level` (optional): LOW, MEDIUM, or HIGH (default: HIGH)

## Configuration Options

You can customize the Gemini integration using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | (required) |
| `GEMINI_MODEL` | The Gemini model to use | `gemini-1.5-flash` |
| `GEMINI_THINKING_LEVEL` | Default thinking level | `HIGH` |

## Testing the Integration

### Quick Test

You can test the MCP server directly from the command line:

```bash
# The API key is already set in .env, load it
source .env  # On Windows: for /f "tokens=1,2 delims==" %a in (.env) do @if "%a"=="GEMINI_API_KEY" setx GEMINI_API_KEY "%b"

# Run the MCP server (it will wait for connections)
python gemini_mcp_server.py
```

### Test with a Simple Prompt

Once Cline is configured, you can test it by asking Cline to:
- "Use Gemini to explain what this code does"
- "Ask Gemini to help me refactor this function"
- "Use Gemini's thinking capabilities to solve this algorithm problem"

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set" error**
   - Make sure your `.env` file exists and contains a valid API key
   - Check that the environment variable is properly set in the MCP server configuration

2. **MCP server not connecting**
   - Verify the path to `gemini_mcp_server.py` is correct in Cline's configuration
   - Ensure Python can import the required packages (`google.genai`, `mcp`)
   - Check that you're using Python 3.9 or higher

3. **API errors**
   - Verify your API key is valid at [Google AI Studio](https://aistudio.google.com/)
   - Check your API usage limits
   - Ensure you have internet connectivity

4. **Cline doesn't see the tools**
   - Restart VS Code after making configuration changes
   - Check Cline's output panel for any MCP-related errors
   - Verify the MCP server configuration in Cline settings

### Debug Mode

To debug the MCP server, you can run it with Python's debug output:

```bash
python -u gemini_mcp_server.py 2>&1 | tee mcp_server.log
```

## Usage Examples

### Example 1: Code Generation

Ask Cline: "Use Gemini to create a Python function that calculates Fibonacci numbers"

### Example 2: Code Analysis

Ask Cline: "Use Gemini to analyze this code and suggest improvements"

### Example 3: Multi-turn Conversation

Ask Cline: "Start a conversation with Gemini about the best practices for API design"

## Updating the Integration

To update the Gemini integration:

1. Pull the latest changes from the repository
2. Update the Python packages:
   ```bash
   pip install --upgrade google-genai mcp
   ```
3. Restart VS Code

## Security Considerations

- **Never commit your API key** - The `.env` file is in `.gitignore`
- **Keep your API key secret** - Don't share it in code, logs, or version control
- **Monitor API usage** - Check your Google AI Studio dashboard for usage statistics
- **Use appropriate thinking levels** - Higher thinking levels use more tokens and may cost more

## Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [MCP (Model Context Protocol) Specification](https://modelcontextprotocol.io/)
- [Cline Documentation](https://github.com/cline/cline)
- [Google AI Studio](https://aistudio.google.com/)

## Support

If you encounter issues:

1. Check this documentation first
2. Review the [troubleshooting section](#troubleshooting)
3. Check the [Google Gemini API documentation](https://ai.google.dev/docs)
4. File an issue in the project repository if it's a bug in the integration

---

**Note:** This integration is for development purposes. For production use, ensure proper error handling, rate limiting, and security measures are in place.