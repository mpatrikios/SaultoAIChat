import os
import logging
from typing import List, Dict, Any
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

def generate_ai_response(user_message: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Generate an AI response using the OpenAI API.
    
    Args:
        user_message (str): The latest message from the user
        conversation_history (list): List of previous messages in the conversation
        
    Returns:
        str: The AI-generated response
    """
    try:
        # Format the conversation history for OpenAI
        messages = []
        
        # Add system message to set up the assistant's behavior
        messages.append({
            "role": "system",
            "content": "You are a helpful Sumersault assistant, branded with green colors. You provide accurate and concise information to help the user."
        })
        
        # Add conversation history
        for message in conversation_history:
            if message.get('sender') == 'user':
                messages.append({"role": "user", "content": message.get('text', '')})
            elif message.get('sender') == 'bot':
                messages.append({"role": "assistant", "content": message.get('text', '')})
        
        # Only add the latest user message if it's not already in history
        if not conversation_history or conversation_history[-1].get('sender') != 'user' or conversation_history[-1].get('text') != user_message:
            messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Sending request to OpenAI with {len(messages)} messages")
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        
        # Extract and return the assistant's response
        ai_response = response.choices[0].message.content
        logger.info(f"Generated AI response: {ai_response[:100]}...")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"