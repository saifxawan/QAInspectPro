"""
Test script to verify Gemini MCP Server integration.

This script tests the Gemini API connection and basic functionality
before configuring Cline.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def test_gemini_api():
    """Test the Gemini API connection."""
    try:
        from google import genai
        from google.genai import types
        
        # Get API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not set in environment")
            return False
        
        print(f"✓ API Key found: {api_key[:10]}...{api_key[-5:]}")
        
        # Create client
        client = genai.Client(api_key=api_key)
        print("✓ Gemini client created successfully")
        
        # Test basic content generation
        print("\n📝 Testing content generation...")
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="Say 'Hello from Gemini!' if you can read this."),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="HIGH",
            ),
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        )
        
        if response.text:
            print(f"\n✓ Gemini response: {response.text[:100]}...")
            print("\n✅ Gemini API integration is working correctly!")
            return True
        else:
            print("❌ No response from Gemini API")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you have installed: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False


def test_mcp_imports():
    """Test if MCP library is properly installed."""
    try:
        import mcp
        from mcp.server import Server
        print("✓ MCP library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ MCP import error: {e}")
        print("   Make sure you have installed: pip install mcp")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Gemini MCP Server Integration Test")
    print("=" * 60)
    print()
    
    # Test MCP imports
    print("1. Testing MCP library...")
    mcp_ok = test_mcp_imports()
    print()
    
    # Test Gemini API
    print("2. Testing Gemini API...")
    gemini_ok = test_gemini_api()
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary:")
    print(f"  MCP Library: {'✅ PASS' if mcp_ok else '❌ FAIL'}")
    print(f"  Gemini API:  {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if mcp_ok and gemini_ok:
        print("\n🎉 All tests passed! You're ready to configure Cline.")
        print("\nNext steps:")
        print("1. Configure Cline to use the MCP server (see GEMINI_CLINE_INTEGRATION.md)")
        print("2. Restart VS Code")
        print("3. Start using Gemini through Cline!")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
    
    return mcp_ok and gemini_ok


if __name__ == "__main__":
    main()