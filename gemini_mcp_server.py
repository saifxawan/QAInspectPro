"""
Gemini MCP Server for Cline Integration

This module provides an MCP (Model Context Protocol) server that connects to
Google's Gemini API, allowing Cline to use Gemini models for AI assistance.

Setup Instructions:
1. Install dependencies: pip install google-genai mcp
2. Set your API key: export GEMINI_API_KEY="your-api-key-here"
   Or create a .env file with: GEMINI_API_KEY=your-api-key-here
3. Configure Cline to use this MCP server

To run the MCP server:
    python gemini_mcp_server.py

To configure Cline, add this to your Cline MCP settings:
    {
        "command": "python",
        "args": ["/path/to/gemini_mcp_server.py"],
        "env": {
            "GEMINI_API_KEY": "your-api-key-here"
        }
    }
"""

import os
import sys
import asyncio
from typing import Optional

from google import genai
from google.genai import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
)

# Initialize the MCP server
server = Server("gemini-mcp-server")

# Gemini configuration
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_THINKING_LEVEL = os.environ.get("GEMINI_THINKING_LEVEL", "HIGH")


def get_gemini_client() -> Optional[genai.Client]:
    """Create and return a Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="gemini_generate",
            description="Generate content using Google Gemini AI model with thinking capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to send to Gemini"
                    },
                    "thinking_level": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "The thinking level for the model (default: HIGH)",
                        "default": "HIGH"
                    },
                    "model": {
                        "type": "string",
                        "description": f"The Gemini model to use (default: {GEMINI_MODEL})"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="gemini_generate_stream",
            description="Stream content generation using Google Gemini AI model",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to send to Gemini"
                    },
                    "thinking_level": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "The thinking level for the model (default: HIGH)",
                        "default": "HIGH"
                    },
                    "model": {
                        "type": "string",
                        "description": f"The Gemini model to use (default: {GEMINI_MODEL})"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="gemini_chat",
            description="Start a multi-turn conversation with Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["user", "model"]
                                },
                                "content": {
                                    "type": "string"
                                }
                            },
                            "required": ["role", "content"]
                        },
                        "description": "Array of conversation messages"
                    },
                    "thinking_level": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                        "description": "The thinking level for the model (default: HIGH)",
                        "default": "HIGH"
                    }
                },
                "required": ["messages"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    client = get_gemini_client()
    if not client:
        return [TextContent(
            type="text",
            text="Error: GEMINI_API_KEY environment variable is not set. Please set your Gemini API key."
        )]

    try:
        if name == "gemini_generate":
            return await generate_content(client, arguments)
        elif name == "gemini_generate_stream":
            return await generate_content_stream(client, arguments)
        elif name == "gemini_chat":
            return await chat_with_gemini(client, arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error calling Gemini API: {str(e)}"
        )]


async def generate_content(client: genai.Client, arguments: dict) -> list[TextContent]:
    """Generate content using Gemini."""
    prompt = arguments.get("prompt", "")
    thinking_level = arguments.get("thinking_level", GEMINI_THINKING_LEVEL)
    model_name = arguments.get("model", GEMINI_MODEL)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=thinking_level,
        ),
    )

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    )

    return [TextContent(
        type="text",
        text=response.text or "No response generated."
    )]


async def generate_content_stream(client: genai.Client, arguments: dict) -> list[TextContent]:
    """Stream content generation using Gemini."""
    prompt = arguments.get("prompt", "")
    thinking_level = arguments.get("thinking_level", GEMINI_THINKING_LEVEL)
    model_name = arguments.get("model", GEMINI_MODEL)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=thinking_level,
        ),
    )

    result_text = []
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            result_text.append(text)

    return [TextContent(
        type="text",
        text="".join(result_text) if result_text else "No response generated."
    )]


async def chat_with_gemini(client: genai.Client, arguments: dict) -> list[TextContent]:
    """Multi-turn conversation with Gemini."""
    messages = arguments.get("messages", [])
    thinking_level = arguments.get("thinking_level", GEMINI_THINKING_LEVEL)

    # Convert messages to Gemini format
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=content)],
            )
        )

    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=thinking_level,
        ),
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=generate_content_config,
    )

    return [TextContent(
        type="text",
        text=response.text or "No response generated."
    )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())