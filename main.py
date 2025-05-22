# Install these packages:
# pip install flask-pymongo flask-login python-dotenv authlib requests

import os
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from openai import AzureOpenAI
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    load_dotenv()
    app = Flask(__name__, static_folder='static/react-build', static_url_path='')

    # Basic Flask Configuration
    CORS(app)
    app.secret_key = os.environ.get("SESSION_SECRET", "sumersault-dev-secret")

    # Session configuration for OAuth state management
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'sumersault:'

    # OAuth configuration to handle CSRF and state
    app.config['AUTHLIB_INSECURE_TRANSPORT'] = True  # Only for development
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    # MongoDB Configuration
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/sumersault")
    mongo = PyMongo(app)

    # Login Manager Setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # OAuth Setup - Microsoft Only (ONLY ONE REGISTRATION)
    oauth = OAuth(app)

    # Configure Microsoft OAuth (Azure AD) - SINGLE REGISTRATION
    microsoft = oauth.register(
        name='microsoft',
        client_id=os.getenv("MICROSOFT_CLIENT_ID"),
        client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
        access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        api_base_url='https://graph.microsoft.com/v1.0/',
        client_kwargs={
            'scope': 'openid email profile User.Read',
            'response_type': 'code'
        },
        server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration'
    )

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
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-12-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        logger.info("Azure OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
        client = None

# User class for Flask-Login
    class User(UserMixin):
        def __init__(self, user_data):
            self.id = str(user_data['_id'])
            self.email = user_data['email']
            self.name = user_data.get('name', '')
            self.company = self._extract_company_from_email(user_data['email'])
            self.job_title = user_data.get('job_title', '')
            self.department = user_data.get('department', '')
            self.role = user_data.get('role', 'user')
            self.microsoft_id = user_data.get('microsoft_id', '')
    
        def get_id(self):
            return self.id
    
        def _extract_company_from_email(self, email):
            """Extract company name from email domain"""
            if not email or '@' not in email:
                return ''
    
            domain = email.split('@')[1]
            # Remove common email providers that don't represent companies
            common_providers = ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'aol.com', 'icloud.com']
            if domain in common_providers:
                return ''
    
            # Otherwise, use the domain as company name
            company_name = domain.split('.')[0].capitalize()
            return company_name
    
@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return User(user_data)

# Authentication routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/microsoft-login')
def microsoft_login():
    redirect_uri = url_for('microsoft_auth', _external=True)
    return microsoft.authorize_redirect(redirect_uri)

@app.route('/microsoft-auth')
def microsoft_auth():
    try:
        token = microsoft.authorize_access_token()

        # Get user information from Microsoft Graph API
        graph_data = microsoft.get('me').json()

        email = graph_data.get('mail', graph_data.get('userPrincipalName'))
        if not email:
            logger.error("Could not retrieve email from Microsoft account")
            return "Could not retrieve email from Microsoft account", 400

        # Optional: Restrict to specific company domains
        # allowed_domains = ['yourcompany.com', 'subsidiary.com']
        # domain = email.split('@')[1]
        # if domain not in allowed_domains:
        #     return "Access denied: Only company email addresses are allowed", 403

        # Check if user exists
        user_data = mongo.db.users.find_one({"email": email})

        if not user_data:
            # Create new user with Microsoft Graph data
            new_user = {
                "email": email,
                "name": graph_data.get('displayName', ''),
                "microsoft_id": graph_data.get('id', ''),
                "job_title": graph_data.get('jobTitle', ''),
                "department": graph_data.get('department', ''),
                "auth_provider": "microsoft",
                "role": "user",
                "created_at": datetime.now(),
                "last_login": datetime.now()
            }

            user_id = mongo.db.users.insert_one(new_user).inserted_id
            user_data = new_user
            user_data['_id'] = user_id

            logger.info(f"Created new user: {email}")
        else:
            # Update existing user info with latest Microsoft data
            mongo.db.users.update_one(
                {"_id": user_data['_id']},
                {"$set": {
                    "name": graph_data.get('displayName', user_data.get('name', '')),
                    "microsoft_id": graph_data.get('id', user_data.get('microsoft_id', '')),
                    "job_title": graph_data.get('jobTitle', user_data.get('job_title', '')),
                    "department": graph_data.get('department', user_data.get('department', '')),
                    "auth_provider": "microsoft",
                    "last_login": datetime.now()
                }}
            )

            logger.info(f"Updated existing user: {email}")

        # Login the user
        user = User(user_data)
        login_user(user)

        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Error during Microsoft authentication: {str(e)}")
        return f"Authentication failed: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# API routes for the React frontend
@app.route('/')
@login_required
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/conversation', methods=['GET'])
@login_required
def get_conversation():
    conversation_id = request.args.get('id')

    if conversation_id:
        # Convert string ID to ObjectId
        try:
            conversation = mongo.db.conversations.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": ObjectId(current_user.id)
            })

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            # Convert ObjectId to string for JSON serialization
            conversation['id'] = str(conversation['_id'])
            del conversation['_id']
            return jsonify(conversation)
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return jsonify({"error": "Invalid conversation ID"}), 400
    else:
        # Create a new conversation
        new_conversation = {
            "user_id": ObjectId(current_user.id),
            "title": f"New Conversation",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": []
        }

        conversation_id = mongo.db.conversations.insert_one(new_conversation).inserted_id
        new_conversation['id'] = str(conversation_id)
        del new_conversation['_id']
        return jsonify(new_conversation)

@app.route('/api/message', methods=['POST'])
@login_required
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

    try:
        # Verify the conversation belongs to the current user
        conversation = mongo.db.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": ObjectId(current_user.id)
        })

        if not conversation:
            return jsonify({'error': 'Conversation not found or access denied'}), 404

        # Add user message to the conversation
        user_message = {
            'id': str(uuid.uuid4()),
            'text': message_text,
            'sender': 'user',
            'timestamp': datetime.now().isoformat(),
            'file': file_info
        }

        # Generate AI response
        message_with_file_info = message_text
        if file_info:
            message_with_file_info = f"{message_text}\n[File attached: {file_info['name']}]"

        ai_response_text = generate_ai_response(message_with_file_info, conversation.get('messages', []))

        # Add AI response to the conversation
        ai_message = {
            'id': str(uuid.uuid4()),
            'text': ai_response_text,
            'sender': 'bot',
            'timestamp': datetime.now().isoformat()
        }

        # Update the conversation with both messages
        mongo.db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": {"$each": [user_message, ai_message]}},
                "$set": {"updated_at": datetime.now()}
            }
        )

        # Retrieve the updated conversation
        updated_conversation = mongo.db.conversations.find_one({"_id": ObjectId(conversation_id)})
        updated_conversation['id'] = str(updated_conversation['_id'])
        del updated_conversation['_id']

        return jsonify({'conversation': updated_conversation, 'message': ai_message})

    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        return jsonify({'error': f'Failed to add message: {str(e)}'}), 500

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_all_conversations():
    # Return just the list of conversation IDs and their first message for the sidebar
    conversation_list = []
    user_conversations = mongo.db.conversations.find(
        {"user_id": ObjectId(current_user.id)},
        sort=[("updated_at", -1)]  # Sort by most recently updated
    )

    for conv in user_conversations:
        first_message = ''
        if conv.get('messages') and len(conv.get('messages')) > 0:
            first_message = conv.get('messages')[0].get('text', 'New conversation')
        else:
            first_message = "New conversation"

        conversation_list.append({
            'id': str(conv['_id']),
            'preview': first_message[:50] + ('...' if len(first_message) > 50 else '')
        })

    return jsonify(conversation_list)

@app.route('/api/conversation', methods=['DELETE'])
@login_required
def delete_conversation():
    conversation_id = request.args.get('id')

    if not conversation_id:
        return jsonify({'error': 'Missing conversation ID'}), 400

    try:
        # Verify the conversation belongs to the current user before deleting
        result = mongo.db.conversations.delete_one({
            "_id": ObjectId(conversation_id),
            "user_id": ObjectId(current_user.id)
        })

        if result.deleted_count == 0:
            return jsonify({'error': 'Conversation not found or access denied'}), 404

        logger.info(f"Deleted conversation: {conversation_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({'error': f'Failed to delete conversation: {str(e)}'}), 500

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Return current user profile information"""
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'company': current_user.company,
        'job_title': current_user.job_title,
        'department': current_user.department,
        'role': current_user.role,
        'microsoft_id': current_user.microsoft_id
    })

@app.route('/api/uploads/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    """
    Serve uploaded files for download
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
        # For styling testing purposes, return a simple response if client is not initialized
        if client is None:
            logger.info("Using temporary response for styling testing")
            return f"Hello {current_user.name} from {current_user.company}! This is a temporary response for UI styling testing. The chat functionality will be enabled once Azure OpenAI is properly configured."

        # Format the conversation history for OpenAI
        messages = []

        # Add system message to set up the assistant's behavior
        system_message = f"""You are a helpful Sumersault assistant for {current_user.name}"""
        if current_user.company:
            system_message += f" at {current_user.company}"
        if current_user.job_title:
            system_message += f", who works as {current_user.job_title}"
        if current_user.department:
            system_message += f" in the {current_user.department} department"

        system_message += """. You are branded with green colors and provide accurate, professional, and concise information to help the user. When users upload files, analyze their content and provide relevant insights or assistance."""

        messages.append({
            "role": "system",
            "content": system_message
        })

        # Process conversation history
        for message in conversation_history:
            content = message.get('text', '')

            # If the message has a file attachment
            if message.get('sender') == 'user' and message.get('file'):
                try:
                    file_info = message.get('file')
                    file_path = file_info.get('path', '')
                    file_name = file_info.get('name', 'unnamed-file')
                    file_type = file_info.get('type', '')

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
                            except Exception as read_err:
                                logger.error(f"Error reading file content: {str(read_err)}")
                                content += f"\n\nFile attached: {file_name} (error reading content: {str(read_err)})"
                        # For binary/non-text files, just mention the file
                        else:
                            content += f"\n\nFile attached: {file_name} (binary/non-text file, type: {file_type})"
                    else:
                        content += f"\n\nFile attached: {file_name} (file not found on server)"
                except Exception as file_err:
                    logger.error(f"Error processing file content: {str(file_err)}")
                    content += f"\n\nFile attached (unable to process content: {str(file_err)})"

            # Add to messages based on sender
            if message.get('sender') == 'user':
                messages.append({"role": "user", "content": content})
            elif message.get('sender') == 'bot':
                messages.append({"role": "assistant", "content": content})

        # Add the latest user message if it's not already in history
        if not conversation_history or conversation_history[-1].get('sender') != 'user' or conversation_history[-1].get('text') != user_message:
            messages.append({"role": "user", "content": user_message})

        logger.info(f"Sending request to Azure OpenAI with {len(messages)} messages")

        # Call the Azure OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        # Extract and return the assistant's response
        ai_response = response.choices[0].message.content
        logger.info(f"Generated AI response: {ai_response[:100]}...")
        return ai_response

    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again later. Error: {str(e)}"

# Admin routes for user management (protected by role check)
@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    # Check if the current user has admin role
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403

    # List all users
    users = mongo.db.users.find({})
    user_list = []

    for user in users:
        user_data = {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', ''),
            'company': user.get('company', ''),
            'job_title': user.get('job_title', ''),
            'department': user.get('department', ''),
            'role': user.get('role', 'user'),
            'last_login': user.get('last_login', ''),
            'created_at': user.get('created_at', '')
        }
        user_list.append(user_data)

    return jsonify(user_list)

@app.route('/admin/user/<user_id>/role', methods=['PUT'])
@login_required
def admin_update_role(user_id):
    # Check if the current user has admin role
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403

    try:
        data = request.json
        role = data.get('role')

        if role not in ['user', 'admin']:
            return jsonify({"error": "Invalid role"}), 400

        # Update the user role
        result = mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": role}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Create first admin user on startup if none exists
def ensure_admin_exists():
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        logger.warning("No ADMIN_EMAIL set in environment variables")
        return

    existing_admin = mongo.db.users.find_one({"role": "admin"})
    if not existing_admin:
        # Check if the admin email user exists and promote them
        admin_user = mongo.db.users.find_one({"email": admin_email})
        if admin_user:
            mongo.db.users.update_one(
                {"_id": admin_user['_id']},
                {"$set": {"role": "admin"}}
            )
            logger.info(f"Promoted existing user to admin: {admin_email}")
        else:
            logger.info(f"Admin user {admin_email} not found. They will be created as admin when they first log in.")

if __name__ == "__main__":
    # Ensure admin user exists on startup
    ensure_admin_exists()
    app.run(host="0.0.0.0", port=5000, debug=True)