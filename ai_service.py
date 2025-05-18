import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
GPT_MODEL = "gpt-4o"

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
logging.debug(f"OpenAI API Key present: {bool(OPENAI_API_KEY)}")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_response(user_message: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Generate an AI response using the OpenAI API.
    
    Args:
        user_message (str): The latest message from the user
        conversation_history (list): List of previous messages in the conversation
        
    Returns:
        str: The AI-generated response
    """
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
    
    # Format the conversation history for the API
    formatted_messages = []
    
    # System message
    formatted_messages.append({
        "role": "system", 
        "content": "You are Sumersault Assistant, a helpful AI assistant. Provide informative, concise, and friendly responses to user queries."
    })
    
    # Add conversation history (up to the last 10 messages to avoid token limits)
    for msg in conversation_history[-10:]:
        if msg['sender'] == 'user':
            formatted_messages.append({"role": "user", "content": msg['text']})
        else:
            formatted_messages.append({"role": "assistant", "content": msg['text']})
    
    # Add the latest user message if it's not already in the history
    if not conversation_history or conversation_history[-1]['sender'] != 'user':
        formatted_messages.append({"role": "user", "content": user_message})
    
    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=formatted_messages
        )
        
        # Get the response content safely
        content = response.choices[0].message.content
        if content is None:
            return "No response from AI. Please try again."
        return content
    except Exception as e:
        logging.error(f"OpenAI API Error: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"
