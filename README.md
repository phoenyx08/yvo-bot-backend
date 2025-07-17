# YVO Bot Backend

Your Very Own Chatbot Backend - A secure FastAPI-based REST API that provides authentication and proxies chat requests to a local Ollama instance.

## Overview

This backend service enables secure access to a local Ollama LLM through a REST API with JWT authentication. It's designed to be a simple, single-file application that can be easily deployed and configured.

## Features

- **JWT Authentication**: Secure login system with bcrypt password hashing
- **Ollama Integration**: Seamless proxy to local Ollama LLM instances
- **FastAPI Framework**: Modern Python web framework with automatic OpenAPI documentation
- **Environment Configuration**: Easy setup through environment variables
- **Request Timeout Handling**: Configurable timeouts for Ollama requests

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   Create a `.env` file with the following variables:
   ```
   OLLAMA_URL=http://localhost:11434/api/generate
   MODEL_NAME=llama2
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   USERNAME=your-username
   PASSWORD=your-password
   ```

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API:**
   - Interactive docs: `http://localhost:8000/docs`
   - API endpoints: `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /login` - Authenticate user and receive JWT token
  - Request: `{"username": "string", "password": "string"}`
  - Response: `{"accessToken": "string", "tokenType": "bearer"}`

### Chat
- `POST /ask` - Send chat query (requires authentication)
  - Headers: `Authorization: Bearer <token>`
  - Request: `{"query": "string"}`
  - Response: `{"response": "string"}`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OLLAMA_URL` | URL of the Ollama instance | `http://localhost:11434/api/generate` |
| `MODEL_NAME` | Name of the Ollama model to use | `llama2` |
| `SECRET_KEY` | JWT signing secret | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `USERNAME` | Authentication username | `admin` |
| `PASSWORD` | Authentication password | `password` |

## Development

The application uses a single-file architecture with all logic contained in `main.py`. Key components include:

- **Authentication System**: JWT-based authentication with password hashing
- **Chat Proxy**: Forwards authenticated requests to Ollama
- **Error Handling**: Comprehensive error handling for various failure scenarios

## Dependencies

- **FastAPI**: Web framework
- **httpx**: HTTP client for Ollama requests
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **python-dotenv**: Environment variable management

## License

See LICENSE file for details.
