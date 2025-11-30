# Dynamic Ads Content Generator

An AI-powered full-stack application that generates personalized advertising content for users based on their interests. The system uses OpenAI GPT-4o for prompt optimization and Black Forest Labs FLUX.2 for image generation, creating unique ads tailored to each user's profile.

## About

This application automates the creation of personalized marketing campaigns:
- Upload a product image
- Define campaign parameters (description, theme, style)
- Generate 15 unique ads (3 per user based on their specific interests)
- View personalized results for each user profile

The backend analyzes user interests, optimizes prompts using AI, and generates images in parallel. The frontend provides an intuitive interface to manage campaigns and view results.

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- OpenAI GPT-4o & GPT-4o-mini (prompt optimization, interest matching)
- Black Forest Labs FLUX.2 (image-to-image generation)
- httpx (async HTTP client)

**Frontend:**
- React 18 (UI framework)
- Vite (build tool)
- Axios (API communication)
- CSS with glassmorphism design

## Project Structure

```
dynamic-ads-content/
├── backend/          # FastAPI backend service
│   ├── data/        # User profiles and trends data
│   ├── prompts/     # AI integration and prompt building
│   ├── routers/     # API endpoint definitions
│   ├── services/    # Business logic layer
│   └── uploads/     # Temporary image storage
│
└── frontend/        # React frontend application
    └── src/
        ├── components/   # React components
        │   └── tabs/    # Tab view components
        └── services/    # API communication layer
```

## Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **OpenAI API Key** (for GPT-4o and GPT-4o-mini)
- **Black Forest Labs API Key** (for FLUX.2 image generation)

## Setup Instructions

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Configure environment variables:
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
BLACK_FOREST_API_KEY=your_black_forest_api_key_here
```

Start the backend server:
```bash
python main.py
```

The backend will be available at: **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

### 2. Frontend Setup

Navigate to the frontend directory (from project root):
```bash
cd frontend
```

Install Node.js dependencies:
```bash
npm install
```

Start the development server:
```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## Running the Application

1. **Start the backend** (from `backend/` directory):
   ```bash
   python main.py
   ```

2. **Start the frontend** (from `frontend/` directory):
   ```bash
   npm run dev
   ```

3. **Open your browser** and navigate to: http://localhost:5173

## Usage Workflow

1. **Upload Product Image**: Click the upload area to select your base product image
2. **Configure Campaign**: Enter product description, campaign theme, and select style preset
3. **Generate Campaign**: Click "Generate Campaign" to start the AI generation process
4. **View Results**: 
   - Campaign Tab: Overall statistics and generation status
   - User Tabs: Individual results for each user (3 personalized ads per user)
   - Preview Tab: Overview of all generated content

## API Endpoints

**Campaign Generation:**
- `POST /api/v1/campaign/generate` - Generate personalized campaign

**User Management:**
- `GET /api/v1/users` - Get all user profiles
- `GET /api/v1/users/{user_id}` - Get specific user

**Trends Analysis:**
- `GET /api/v1/trends` - Get trending topics
- `GET /api/v1/trends/refresh` - Refresh trend data

**Health Check:**
- `GET /health` - Server health status

## Key Features

- **Personalized Generation**: Creates 3 unique ads per user based on their interests
- **Parallel Processing**: Generates up to 15 images concurrently for faster results
- **AI Optimization**: Uses GPT-4o to create detailed, engaging prompts
- **Content Moderation**: Handles API content policy checks automatically
- **Responsive UI**: Modern glassmorphism design with smooth animations
- **Real-time Feedback**: Shows generation progress and status updates

## Development

### Backend Development
- Hot reload: `uvicorn main:app --reload`
- API docs: http://localhost:8000/docs
- Logging: Configured for campaign steps and API events

### Frontend Development
- Vite HMR: Automatic browser refresh on file changes
- Component structure: Modular tabs for different views
- State management: React hooks for local state

## Configuration

**CORS Settings** (`backend/main.py`):
- Allowed origins: http://localhost:3000, http://localhost:5173

## Performance

- **Image Generation**: ~30-60 seconds per image
- **Total Campaign Time**: ~60-120 seconds for parallel generaton

## Troubleshooting

**Backend won't start:**
- Verify Python 3.8+ is installed
- Check `.env` file contains valid API keys
- Ensure port 8000 is available

**Frontend won't start:**
- Verify Node.js 16+ is installed
- Delete `node_modules` and run `npm install` again
- Ensure port 5173 is available

**Images not generating:**
- Check API keys are valid and have credits
- Review backend logs for moderation or timeout issues
- Some content may be rejected by Black Forest moderation

## License

This project was created for the München Hackathon.

## Further Documentation

- Backend README: `backend/README.md`
- Frontend README: `frontend/README.md`
