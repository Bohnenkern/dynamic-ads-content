# Frontend - Dynamic Ads Content Generator

A React-based frontend application for generating personalized advertising content using AI. Built with React 18 and Vite for a modern, fast development experience.

##  Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

### Build for Production

Create an optimized production build:
```bash
npm run build
```

Preview the production build locally:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── tabs/           # Tab view components
│   │   │   ├── CampaignTab.jsx       # Campaign setup and execution
│   │   │   ├── UserTab.jsx           # Individual user results view
│   │   │   └── PreviewTab.jsx        # Preview generated images
│   │   ├── ImageUpload.jsx           # Product image upload component
│   │   └── TabNavigation.jsx         # Tab switching navigation
│   │
│   ├── services/           # API communication layer
│   │   └── api.js          # Axios-based API client
│   │
│   ├── App.jsx             # Main application component
│   ├── main.jsx            # Application entry point
│   └── *.css               # Component-specific styles
│
├── index.html              # HTML template
├── vite.config.js          # Vite configuration
└── package.json            # Project dependencies

```

##  Application Flow

### 1. **Campaign Tab** (`CampaignTab.jsx`)
- **Image Upload**: Upload a product image that will be used as the base for all generated ads
- **Campaign Configuration**: Define product description, campaign theme, and style preset
- **Campaign Execution**: Triggers the backend to generate personalized ads for all users
- **Results Overview**: Displays statistics and status of the campaign generation

### 2. **User Tabs** (`UserTab.jsx`)
- **User Profile**: Shows demographic information (age group, location, language, occupation)
- **Top Interests**: Displays the user's 3 main interests
- **Generated Ads**: Shows the 3 personalized images generated for each user (one per interest)
- **Technical Details**: Collapsible section with raw JSON data for debugging

### 3. **Preview Tab** (`PreviewTab.jsx`)
- **Trend-Based View**: Preview images generated for trending categories
- **Quick Overview**: See all generated content in one place

##  Key Technologies

- **React 18**: Modern React with hooks and concurrent features
- **Vite**: Lightning-fast build tool and dev server
- **Axios**: Promise-based HTTP client for API communication
- **CSS Modules**: Scoped styling with glassmorphism design

## API Integration

The frontend communicates with the FastAPI backend through the `api.js` service:

- **Base URL**: `http://localhost:8000`
- **Main Endpoints**:
  - `POST /api/v1/campaign/generate` - Generate campaign with personalized ads
  - `GET /api/v1/users` - Fetch all user profiles
  - `GET /api/v1/users/{userId}` - Get specific user data

## Design Features

- **Glassmorphism UI**: Modern frosted glass effect design
- **Responsive Layout**: Works on desktop and mobile devices
- **Dark Theme**: Eye-friendly dark color scheme
- **Smooth Animations**: Polished transitions and interactions

## Workflow

1. User uploads a product image
2. User fills in campaign details (description, theme, style)
3. Click "Generate Campaign" to start the AI generation process
4. View results in individual user tabs or preview all at once
5. Each user sees ads personalized to their 3 main interests

## State Management

The application uses React's built-in `useState` and `useEffect` hooks:
- `uploadedImage`: Stores the uploaded product image
- `campaignResult`: Contains the full campaign generation results
- `users`: List of all user profiles
- `isLoading`: Tracks loading state during API calls
- `error`: Stores error messages for user feedback

## Development

### File Watching
Vite automatically reloads the browser when you save changes to any file.

### Hot Module Replacement (HMR)
Component state is preserved during updates for faster development.

### Error Handling
API errors are caught and displayed in the UI with helpful messages.
