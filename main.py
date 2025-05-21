import os
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI      # Using standard OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__, static_folder='static/react-build', static_url_path='')
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET", "sumersault-dev-secret")

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json', 'zip', 
                     'py', 'js', 'html', 'css', 'c', 'cpp', 'h', 'java', 'rb', 'php', 'xml', 'md'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize OpenAI client
try:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
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
    file_info = None
    file_path = None
    
    # Check if the post request has the file part
    if 'file' in request.files:
        file = request.files['file']
        logger.info(f"File received in request: {file.filename if file else 'None'}")
        
        if file and file.filename and allowed_file(file.filename):
            # Generate a secure filename with UUID to prevent collisions
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create file info for storing in the message
            file_info = {
                'name': filename,
                'path': file_path,
                'type': file.content_type,
                'size': os.path.getsize(file_path)
            }
            logger.info(f"File uploaded: {filename} ({file_info['size']} bytes), path: {file_path}, type: {file.content_type}")
        else:
            logger.warning(f"File upload failed validation: filename={file.filename if file else 'None'}, allowed={allowed_file(file.filename) if file and file.filename else False}")
    
    # Get conversation ID and message text from form data
    conversation_id = request.form.get('conversation_id')
    message_text = request.form.get('message', '')
    
    if not conversation_id:
        return jsonify({'error': 'Missing conversation ID'}), 400
    
    # Allow empty message text if a file is attached
    if not message_text and not file_info:
        return jsonify({'error': 'Missing message content (text or file)'}), 400
    
    if conversation_id not in conversations:
        conversations[conversation_id] = {
            'id': conversation_id,
            'messages': []
        }
    
    # Add user message with file attachment if present
    user_message = {
        'id': len(conversations[conversation_id]['messages']),
        'text': message_text,
        'sender': 'user',
        'timestamp': datetime.now().isoformat(),
        'file': file_info
    }
    conversations[conversation_id]['messages'].append(user_message)
    
    try:
        # Generate AI response using Azure OpenAI
        # Include file information in the message sent to AI if a file was uploaded
        message_with_file_info = message_text
        if file_info:
            message_with_file_info = f"{message_text}\n[File attached: {file_info['name']}]"
        
        ai_response_text = generate_ai_response(message_with_file_info, conversations[conversation_id]['messages'])
        
        # Add AI response
        ai_message = {
            'id': len(conversations[conversation_id]['messages']),
            'text': ai_response_text,
            'sender': 'bot',
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id]['messages'].append(ai_message)
        
        return jsonify({'conversation': conversations[conversation_id], 'message': ai_message})
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return jsonify({'error': 'Failed to generate AI response'}), 500

@app.route('/api/conversations', methods=['GET'])
def get_all_conversations():
    # Return just the list of conversation IDs and their first message for the sidebar
    conversation_list = []
    for conv_id, conv in conversations.items():
        first_message = conv['messages'][0]['text'] if conv['messages'] else "New conversation"
        conversation_list.append({
            'id': conv_id,
            'preview': first_message[:50] + ('...' if len(first_message) > 50 else '')
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
        
@app.route('/api/uploads/<filename>', methods=['GET'])
def download_file(filename):
    """
    Serve uploaded files for download
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        return jsonify(error="No messages provided"), 400

    try:
        resp = client.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify(error=str(e)), 500

def generate_ai_response(user_message, conversation_history):
    """
    Generate an AI response using OpenAI.
    
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
            "content": "You are a helpful Sumersault assistant, branded with green colors. You provide accurate and concise information to help the user. When users upload files, analyze their content and provide relevant insights or assistance."
        })
        
        # Process file content from conversation history and include in messages
        current_message_has_file = False
        
        for message in conversation_history:
            content = message.get('text', '')
            has_file = False
            
            # If the message has a file attachment
            if message.get('sender') == 'user' and message.get('file'):
                has_file = True
                try:
                    file_info = message.get('file')
                    file_path = file_info.get('path', '')
                    file_name = file_info.get('name', 'unnamed-file')
                    file_type = file_info.get('type', '')
                    
                    # Log full file info to help debug
                    logger.info(f"File in message: {file_info}")
                    
                    if os.path.exists(file_path):
                        # For text-based files, include their content in the message
                        if file_type and ('text/' in file_type or file_name.lower().endswith(('.txt', '.md', '.csv', '.json', '.py', '.js', '.html', '.css', '.c', '.cpp', '.h', '.xml'))):
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    file_content = f.read()
                                    file_excerpt = file_content[:10000]  # Limit to 10K chars to avoid token limits
                                    content += f"\n\nFile attached: {file_name}\nContent of the file:\n```\n{file_excerpt}"
                                    if len(file_content) > 10000:
                                        content += "\n... (content truncated due to length)"
                                    content += "\n```"
                                    logger.info(f"Successfully read file content of {file_name}")
                            except Exception as read_err:
                                logger.error(f"Error reading file content: {str(read_err)}")
                                content += f"\n\nFile attached: {file_name} (error reading content: {str(read_err)})"
                        # For binary/non-text files, just mention the file
                        else:
                            content += f"\n\nFile attached: {file_name} (binary/non-text file, type: {file_type})"
                            logger.info(f"Binary file noted: {file_name}")
                    else:
                        logger.error(f"File path does not exist: {file_path}")
                        content += f"\n\nFile attached: {file_name} (file not found on server)"
                        
                    logger.info(f"Processing file in conversation: {file_name}")
                    
                    # Check if this is the current user's message with a file
                    if message == conversation_history[-1] and message.get('sender') == 'user':
                        current_message_has_file = True
                except Exception as file_err:
                    logger.error(f"Error processing file content: {str(file_err)}")
                    content += f"\n\nFile attached: {file_name if 'file_name' in locals() else 'unknown'} (unable to process content: {str(file_err)})"
            
            # Add to messages based on sender
            if message.get('sender') == 'user':
                messages.append({"role": "user", "content": content})
                if has_file:
                    logger.info(f"Added user message with file content to conversation: {content[:100]}...")
            elif message.get('sender') == 'bot':
                messages.append({"role": "assistant", "content": content})
        
        # Only add the latest user message if it's not already in history
        if not conversation_history or conversation_history[-1].get('sender') != 'user' or conversation_history[-1].get('text') != user_message:
            messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Sending request to OpenAI with {len(messages)} messages")
        
        # For styling testing purposes, return a simple response if client is not initialized
        if client is None:
            logger.info("Using temporary response for styling testing")
            return "This is a temporary response for UI styling testing. The chat functionality will be enabled once OpenAI is properly configured."
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages
        )
        
        # Extract and return the assistant's response
        ai_response = response.choices[0].message.content
        logger.info(f"Generated AI response: {ai_response[:100]}...")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

