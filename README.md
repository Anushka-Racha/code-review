# CodeRefine - AI-Powered Code Reviewer & Optimizer

CodeRefine is a lightweight, AI-powered code review assistant built with FastAPI and React. It uses Google Gemini API to analyze code, suggest improvements, detect security issues, and provide optimized versions of your code.

## Features

- **AI Code Review**: Detects inefficient loops, bad naming, redundant logic, and poor structure.
- **Optimization Suggestions**: Provides time complexity hints, cleaner alternatives, and better data structures.
- **Security Check**: Identifies hardcoded credentials, SQL injection risks, and unsafe practices.
- **Complexity Estimation**: Estimates time and space complexity of your code.
- **Google Gemini**: Uses Gemini 1.5 Flash for fast, intelligent code analysis.

## Tech Stack

- **Backend**: Python, FastAPI, Google Gemini API
- **Frontend**: React 19, Vite, Tailwind CSS, Framer Motion, Lucide React

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API key (in `.env` file)

### Installation

1. **Clone the repository**

2. **Set up the Backend**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure API Key**
   Create a `.env` file in the root directory with:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Get your key at: https://aistudio.google.com/app/apikey

### Running the Application

1. **Start the Backend**
   ```bash
   uvicorn main:app --reload
   ```

2. **Start the Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser at `http://localhost:5173`.

## Project Structure

- `main.py`: FastAPI backend handling code analysis.
- `frontend/`: React frontend application.
- `test_code.py`: Sample code for testing the application.
- `.env`: Environment variables (API key).

## Demo Mode

If the Gemini API is unavailable, the application will automatically switch to **Demo Mode** with basic code analysis so you can still test the UI.

