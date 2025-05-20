import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__, static_folder='static/react-build', static_url_path='')
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "sumersault-dev-secret")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    client = None

# In-memory storage for conversations (in a production app, this would be a database)
conversations = {}


# API routes for the React frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    conversation_id = request.args.get('id')

    if not conversation_id or conversation_id not in conversations:
        # Create a new conversation if none exists
        if not conversation_id:
            conversation_id = datetime.now().strftime('%Y%m%d%H%M%S')

        conversations[conversation_id] = {
            'id': conversation_id,
            'messages': []
        }

    return jsonify(conversations[conversation_id])


@app.route('/api/message', methods=['POST'])
def add_message():
    data = request.json
    conversation_id = data.get('conversation_id')
    message_text = data.get('message')

    if not conversation_id or not message_text:
        return jsonify({'error': 'Missing conversation ID or message'}), 400

    if conversation_id not in conversations:
        conversations[conversation_id] = {
            'id': conversation_id,
            'messages': []
        }

    # Add user message
    user_message = {
        'id': len(conversations[conversation_id]['messages']),
        'text': message_text,
        'sender': 'user',
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id]['messages'].append(user_message)

    try:
        # Generate AI response using Azure OpenAI
        ai_response_text = generate_ai_response(
            message_text, conversations[conversation_id]['messages'])

        # Add AI response
        ai_message = {
            'id': len(conversations[conversation_id]['messages']),
            'text': ai_response_text,
            'sender': 'bot',
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id]['messages'].append(ai_message)

        return jsonify({
            'conversation': conversations[conversation_id],
            'message': ai_message
        })

    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return jsonify({'error': 'Failed to generate AI response'}), 500


@app.route('/api/conversations', methods=['GET'])
def get_all_conversations():
    # Return just the list of conversation IDs and their first message for the sidebar
    conversation_list = []
    for conv_id, conv in conversations.items():
        first_message = conv['messages'][0]['text'] if conv[
            'messages'] else "New conversation"
        conversation_list.append({
            'id':
            conv_id,
            'preview':
            first_message[:50] + ('...' if len(first_message) > 50 else '')
        })
    return jsonify(conversation_list)


@app.route('/api/conversation', methods=['DELETE'])
def delete_conversation():
    conversation_id = request.args.get('id')

    if not conversation_id:
        return jsonify({'error': 'Missing conversation ID'}), 400

    if conversation_id in conversations:
        del conversations[conversation_id]
        logger.info(f"Deleted conversation: {conversation_id}")
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Conversation not found'}), 404


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        return jsonify(error="No messages provided"), 400

    try:
        resp = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), messages=messages)
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify(error=str(e)), 500


def generate_ai_response(user_message, conversation_history):
    """
    Generate an AI response using Azure OpenAI.
    
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
            "content": "You are a professional AI assistant. Format all responses in Markdown with section headings (##), bullet points, and bold summaries where helpful. Always organize content clearly and concisely."
        })

        # Add conversation history
        for message in conversation_history:
            if message.get('sender') == 'user':
                messages.append({
                    "role": "user",
                    "content": message.get('text', '')
                })
            elif message.get('sender') == 'bot':
                messages.append({
                    "role": "assistant",
                    "content": message.get('text', '')
                })

        # Only add the latest user message if it's not already in history
        if not conversation_history or conversation_history[-1].get(
                'sender') != 'user' or conversation_history[-1].get(
                    'text') != user_message:
            messages.append({"role": "user", "content": user_message})

        logger.info(
            f"Sending request to OpenAI with {len(messages)} messages")

        # For styling testing purposes, return a simple response if client is not initialized
        if client is None:
            logger.info("Using temporary response for styling testing")
            return "This is a temporary response for UI styling testing. The chat functionality will be enabled once Azure OpenAI is properly configured."

        # Try to call OpenAI, but if there's an issue, return a formatted example
        try:
            if client and hasattr(client, 'chat'):
                response = client.chat.completions.create(
                    model="gpt-4o",  # Using the latest model
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )
                ai_response = response.choices[0].message.content
                logger.info(f"Generated AI response: {ai_response[:100]}...")
                return ai_response
        except Exception as e:
            logger.error(f"Error with OpenAI API call: {str(e)}")
            
        # If OpenAI call failed or client is not properly configured, return a formatted example
        logger.info("Returning formatted example response")
        return """## Sample Formatted Response

Here's a demonstration of formatted Markdown text:

* **Bullet point 1**: This shows how lists work
* **Bullet point 2**: With some bold text formatting
* **Bullet point 3**: And proper indentation

### Code Example

```javascript
function helloWorld() {
  console.log("Hello, world!");
  return true;
}
```

### Table Example

| Language | Purpose | Popularity |
|----------|---------|------------|
| Python   | General | High       |
| JavaScript | Web    | High      |
| SQL      | Database | Medium    |

This demonstrates how the frontend renders different Markdown elements properly."""

    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
