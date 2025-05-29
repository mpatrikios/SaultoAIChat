# SaultoChat

A modern ChatGPT-like interactive chat application with advanced Azure OpenAI integration, robust file upload capabilities, and real-time streaming message display. Built with React.js frontend and Python/Flask backend.

![SaultoChat Interface](generated-icon.png)

## Features

### Core Functionality
- **Real-time AI Chat**: Interactive conversations with Azure OpenAI GPT-4o
- **Streaming Responses**: Word-by-word "thinking aloud" AI responses for better user experience
- **File Upload & Analysis**: Upload and analyze text files (Python, JavaScript, C, text files, etc.)
- **Conversation Management**: Save, load, and organize chat history
- **Pin Conversations**: Pin important chats to the top of the sidebar for quick access

### User Experience
- **Microsoft Authentication**: Secure login with Microsoft accounts
- **User Profiles**: Company-based user management and profiles
- **Persistent Sidebar**: Always-visible conversation history with attractive card-style design
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Sumersault Branding**: Green color scheme matching Sumersault brand identity

### Technical Features
- **MongoDB Atlas**: Secure cloud database for conversation storage
- **Role-based Access**: Admin and user role management
- **File Content Parsing**: AI can read and analyze uploaded file contents
- **Real-time Streaming**: Server-sent events for live message updates
- **Cross-platform**: Runs on any system with Python and Node.js

## Technology Stack

### Frontend
- **React.js**: Modern component-based UI framework
- **Webpack**: Module bundler and build tool
- **Axios**: HTTP client for API requests
- **Font Awesome**: Icons and visual elements
- **CSS3**: Custom styling with CSS variables

### Backend
- **Flask**: Python web framework
- **Azure OpenAI**: GPT-4o integration for AI responses
- **MongoDB Atlas**: Cloud database for data persistence
- **Flask-Login**: User session management
- **Microsoft OAuth**: Authentication integration
- **Gunicorn**: WSGI HTTP server

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Atlas account
- Azure OpenAI service
- Microsoft Azure AD application

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/saultochat.git
cd saultochat
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory and install dependencies
cd frontend
npm install

# Build the frontend
npm run build
cd ..
```

### 4. Environment Configuration
Create a `.env` file in the root directory with the following variables:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name

# Microsoft Authentication
MICROSOFT_CLIENT_ID=your_microsoft_app_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_app_client_secret
MICROSOFT_TENANT_ID=your_tenant_id

# Application Configuration
SESSION_SECRET=your_session_secret_key
UPLOAD_DIR=uploads
UPLOAD_FOLDER=uploads
```

### 5. Run the Application
```bash
# Start the Flask server
python main.py

# Or using Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

Visit `http://localhost:5000` to access the application.

## Configuration Guide

### Azure OpenAI Setup
1. Create an Azure OpenAI resource in Azure Portal
2. Deploy a GPT-4o model
3. Copy the endpoint, API key, and deployment name
4. Add these to your `.env` file

### MongoDB Atlas Setup
1. Create a MongoDB Atlas cluster
2. Create a database user with read/write permissions
3. Whitelist your IP address
4. Copy the connection string and add to `.env`

### Microsoft Authentication Setup
1. Register an application in Azure Active Directory
2. Add redirect URI: `http://localhost:5000/auth/microsoft/callback`
3. Generate a client secret
4. Copy client ID, secret, and tenant ID to `.env`

## Usage

### Basic Chat
1. Sign in with your Microsoft account
2. Click "New Chat" to start a conversation
3. Type your message and press Enter or click Send
4. Watch the AI respond in real-time with streaming text

### File Upload
1. Click the attachment button (📎) in the message input
2. Select a text file (Python, JavaScript, C, txt, etc.)
3. Add a message asking about the file
4. The AI will analyze the file contents and respond

### Pin Conversations
1. Hover over any conversation in the sidebar
2. Click the pin button (📌) to pin important chats
3. Pinned conversations appear at the top under "Pinned"
4. Click the pin again to unpin

### Managing Conversations
- **Delete**: Click the trash icon to delete conversations
- **Switch**: Click any conversation in the sidebar to switch to it
- **New Chat**: Use the "New Chat" button to start fresh

## API Endpoints

### Authentication
- `GET /login` - Microsoft login redirect
- `GET /auth/microsoft` - Microsoft OAuth callback
- `POST /logout` - Logout current user

### Chat & Conversations
- `GET /api/conversations` - Get user's conversations
- `GET /api/conversation` - Get specific conversation
- `DELETE /api/conversation` - Delete conversation
- `PATCH /api/conversation/pin` - Pin/unpin conversation
- `POST /api/chat/stream` - Stream chat responses

### File Management
- `POST /api/upload` - Upload file
- `GET /api/uploads/<filename>` - Download file

### User Management
- `GET /api/user/profile` - Get user profile
- `GET /admin/users` - Admin: List users
- `POST /admin/users/<id>/role` - Admin: Update user role

## Project Structure

```
saultochat/
├── frontend/                 # React.js frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── styles/          # CSS stylesheets
│   │   └── index.js         # Entry point
│   ├── webpack.config.js    # Webpack configuration
│   └── package.json         # Frontend dependencies
├── uploads/                 # File upload directory
├── main.py                  # Flask application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev    # Development build with watch mode
npm run build  # Production build
```

### Backend Development
```bash
# Run with auto-reload for development
python main.py

# Or with debug mode
FLASK_DEBUG=1 python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Notes

- Never commit `.env` files or API keys
- Use environment variables for all sensitive configuration
- MongoDB connection strings contain credentials
- Microsoft client secrets should be kept secure
- Upload directory should have proper permissions

## Troubleshooting

### Common Issues

**Authentication not working**
- Check Microsoft app registration redirect URIs
- Verify tenant ID and client credentials
- Ensure proper permissions in Azure AD

**AI responses not working**
- Verify Azure OpenAI endpoint and API key
- Check deployment name matches your Azure configuration
- Ensure sufficient quota in Azure OpenAI service

**Database connection issues**
- Verify MongoDB Atlas connection string
- Check IP whitelist in MongoDB Atlas
- Ensure database user has proper permissions

**File uploads failing**
- Check upload directory permissions
- Verify UPLOAD_DIR environment variable
- Ensure sufficient disk space

## License

This project is proprietary software developed for Sumersault.

## Support

For support and questions, contact the development team or create an issue in the repository.