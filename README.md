# Sumersault Chat Application

A ChatGPT-like interactive chat application with OpenAI integration and a responsive interface. This application allows users to have conversations with an AI assistant, save chat history, and manage multiple conversations.

![Sumersault Chat](./attached_assets/fulllogo_nobuffer.jpg)

## Features

- Interactive chat interface with AI-powered responses
- Conversation history management (create, view, delete)
- Persistent sidebar for easy navigation between conversations
- Responsive design that works on desktop and mobile devices
- Custom Sumersault branding and color scheme

## Project Structure

```
project/
├── app.py                  # Entry point for running with Flask directly
├── main.py                 # Main Flask application code
├── frontend/               # React.js frontend code
│   ├── src/
│   ├── webpack.config.js
│   └── ...
├── static/                 # Static assets served by Flask
├── templates/              # HTML templates
└── run.sh                  # Helper script to run with Gunicorn
```

## Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm
- OpenAI API Key

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd sumersault-chat
```

### 2. Set up the environment variables

Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Python dependencies

```bash
pip install flask flask-cors flask-sqlalchemy gunicorn openai python-dotenv
```

### 4. Install Node.js dependencies and build the frontend

```bash
cd frontend
npm install
npx webpack
cd ..
```

## Running the Application

### Option 1: Using Gunicorn (Production-like)

```bash
# From the project root directory
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload backend.main:app
```

### Option 2: Using Flask's Development Server

```bash
# From the project root directory
python app.py
```

### Option 3: Using the helper script

```bash
# Make sure the script is executable
chmod +x run.sh
./run.sh
```

## Frontend Development

If you're working on the frontend and want to see changes immediately:

```bash
cd frontend
npx webpack --watch
```

## Accessing the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

- `GET /api/conversations` - Get all conversations
- `GET /api/conversation?id={id}` - Get a specific conversation
- `DELETE /api/conversation?id={id}` - Delete a conversation
- `POST /chat` - Send a message to the AI and get a response

## Technologies Used

- **Backend**:
  - Flask (Python web framework)
  - OpenAI API for AI chat functionality
  - Gunicorn (WSGI HTTP Server)

- **Frontend**:
  - React.js
  - Webpack
  - CSS for styling

## License

[Include license information here]

## Contact

[Include contact information here]