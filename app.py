import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

from ai_service import generate_ai_response

app = Flask(__name__, static_folder='static/react-build', static_url_path='')
app.secret_key = os.environ.get("SESSION_SECRET", "sumersault-dev-secret")

# In-memory storage for conversations (in a production app, this would be a database)
conversations = {}

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
        # Generate AI response
        ai_response_text = generate_ai_response(message_text, conversations[conversation_id]['messages'])
        
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
        logging.error(f"Error generating AI response: {str(e)}")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)