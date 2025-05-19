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
        # For styling testing purposes, return a simple response
        logger.info("Using temporary response for styling testing")
        return "This is a temporary response for UI styling testing. The chat functionality will be enabled once we have a valid API key."
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"