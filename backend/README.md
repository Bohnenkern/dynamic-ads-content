# Backend - Dynamic Ads Content API

A FastAPI-based backend service that generates personalized advertising content using AI. Integrates with OpenAI GPT-4o for prompt optimization and Black Forest Labs FLUX.2 for image generation.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Black Forest Labs API key

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the backend root directory with the following:
```env
OPENAI_API_KEY=your_openai_api_key_here
BLACK_FOREST_API_KEY=your_black_forest_api_key_here
```

### Running the Server

Start the server with:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The server runs on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs** (Swagger UI)

## Project Structure

```
backend/
├── data/                   # Static data files
│   ├── users.json         # User profiles with interests
│   ├── trends.json        # Trending topics data
│   └── trends_short.json  # Shortened trends list
│
├── prompts/               # AI prompt generation and API integration
│   ├── openai_service.py          # OpenAI GPT-4o integration
│   ├── image_generation.py        # Black Forest FLUX.2 API client
│   ├── image_prompt_builder.py    # Constructs image prompts
│   ├── interest_matcher.py        # Matches user interests with trends
│   └── trend_filter.py            # Filters relevant trends
│
├── routers/               # API endpoint definitions
│   ├── users.py          # Campaign generation endpoints
│   └── trends.py         # Trend analysis endpoints
│
├── services/              # Business logic layer
│   ├── user_data.py      # User profile management
│   ├── trend_analysis.py # Trend aggregation service
│   ├── trend_matcher.py  # User-trend matching logic
│   └── external_api.py   # External API utilities
│
├── uploads/               # Temporary storage for uploaded images
│
├── main.py               # Application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (create this)

```

## Key Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **OpenAI GPT-4o**: Text generation for prompt optimization (temperature 0.7)
- **OpenAI GPT-4o-mini**: Lightweight model for interest matching
- **Black Forest Labs FLUX.2**: Image-to-image generation (flux-2-pro endpoint)
- **httpx**: Async HTTP client for API requests
- **Pillow**: Image processing library
- **python-multipart**: File upload handling

## API Endpoints

### Users & Campaign Generation

**POST /api/v1/campaign/generate**
- Generates personalized ad campaign for all users
- Accepts: product image, product description, campaign theme, style preset
- Returns: personalized images

**GET /api/v1/users**
- Returns all user profiles with their interests

**GET /api/v1/users/{user_id}**
- Returns specific user profile

### Trends Analysis

**GET /api/v1/trends**
- Returns aggregated trending topics

**GET /api/v1/trends/refresh**
- Refreshes trend data from sources

## Campaign Generation Workflow

The campaign generation follows an 8-step pipeline:

1. **Image Upload**: Receive and save product image
2. **User Loading**: Load all user profiles 
3. **Interest Matching**: Match user interests with trending topics using GPT-4o-mini
4. **Trend Filtering**: Optional step to filter relevant trends (currently disabled)
5. **Trend Optimization**: Optimize top 5 trends using GPT-4o
6. **Prompt Building**: with GPT-4o
7. **Image Generation**: parallel generation using Black Forest FLUX.2
8. **Result Mapping**: Map generated images to users by interest

## Image Generation

### Black Forest Labs FLUX.2 Integration
- **Model**: flux-2-pro (image-to-image)
- **Polling Mechanism**: 1-second intervals with 60-second timeout
- **Status Detection**: Handles "Ready", "Request Moderated", "Error", "Failed"
- **Parallelization**: Generates concurrently using asyncio.gather()

### Prompt Optimization
- **Primary Model**: GPT-4o (temperature 0.7, max_tokens 250)
- **Purpose**: Creates detailed, stylized prompts for image generation
- **Input**: User interest + product description + campaign theme

## Configuration

### CORS Settings
Configured to allow requests from:
- http://localhost:3000
- http://localhost:5173

## Data Models

### User Profile
```json
{
  "id": 1,
  "name": "User Name",
  "age": 28,
  "location": "City, Country",
  "language": "en",
  "interests": ["Interest 1", "Interest 2", "Interest 3"],
  "demographics": {
    "occupation": "Job Title"
  }
}
```

### Campaign Result
```json
{
  "campaign_id": "uuid",
  "status": "success",
  "statistics": {
    "total_users": 5,
    "total_images_generated": 15,
    "images_per_user": 3
  },
  "user_results": [...]
}
```

## Error Handling

- **Content Moderation**: Black Forest API may reject prompts (alcohol, copyrights)
- **Timeout Handling**: 60-second polling limit per image
- **API Rate Limits**: Respects OpenAI and Black Forest rate limits
- **Validation**: Pydantic models ensure data integrity

## Logging

Structured logging configured for:
- Campaign generation steps
- Image generation status (logged at 0s and every 20s)
- API errors and moderation events
- User data loading

## Development

### Hot Reload
Use `--reload` flag for automatic server restart on code changes:
```bash
uvicorn main:app --reload
```

### API Documentation
Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```
