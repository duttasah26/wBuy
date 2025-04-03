<div align="center">
  <!-- REMOVE THIS IF YOU DON'T HAVE A LOGO -->
    <img src="/public/WBuyLogo.png" alt="Logo" width="80" height="80">

<h3 align="center">W Buy</h3>

  <p align="center">
    AI-powered companion for finding the best products, food, and locations.
    <br />
     <a href="https://github.com/evanbabic/wbuy">github.com/evanbabic/wbuy</a>
  </p>
</div>

<!-- REMOVE THIS IF YOU DON'T HAVE A DEMO -->
<!-- TIP: You can alternatively directly upload a video up to 100MB by dropping it in while editing the README on GitHub. This displays a video player directly on GitHub instead of making it so that you have to click an image/link -->
<div align="center">
  <a href="https://github.com/evanbabic/wbuy">
    <img src="/public/WBuy.jpg" alt="Project Demo">
    <a href="https://www.youtube.com/watch?v=zR-UxlD1k4Q"> WATCH THE DEMO VIDEO HERE ! </a>
  </a>
</div>

## Table of Contents

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

wBuy is a Next.js application that helps users find the best recommendations for products, food, and locations using AI-powered analysis of Reddit and Google Places data. It includes a browser extension for easy access to product reviews on Amazon.

### Key Features

- **AI-Powered Recommendations:** Leverages Perplexity AI to analyze user reviews and provide relevant recommendations.
- **Location-Based Search:** Finds the best food and locations near the user.
- **Product Search:** Identifies top-rated products based on user input.
- **Browser Extension:** Integrates with Amazon to provide quick access to Reddit comments for product analysis.
- **Dynamic UI:** Uses Framer Motion for smooth animations and transitions.

## Architecture

The project is structured as follows:

- **Frontend (Next.js):**
    - `app/`: Contains the Next.js application, including pages, layouts, and components.
    - `app/page.js`: Main landing page with search functionality.
    - `app/results/page.js`: Displays search results.
    - `app/components/`: Reusable React components like `Location.js`, `Result.js`, and `LoadingAnimation.js`.
    - `public/`: Static assets such as images.
- **Backend (Flask):**
    - `backend/`: Contains the Flask API for scraping and analyzing data.
    - `backend/server.py`: Main Flask application with API endpoints.
    - `backend/scraper.py`: Implements Reddit and Google Places scraping.
    - `backend/perplexity.py`: Handles communication with the Perplexity AI API.
- **Browser Extension:**
    - `extension/`: Contains the files for the Chrome extension.
    - `extension/popup.html`: Popup UI for the extension.
    - `extension/content.js`: Content script to extract data from Amazon product pages.
    - `extension/background.js`: Background script for the extension.

The application uses the following technologies:

- **Frontend:** Next.js, React, Framer Motion, Tailwind CSS
- **Backend:** Flask, Pymongo
- **Scraping:** PRAW (Reddit API), Google Places API
- **AI:** Perplexity AI API

## Getting Started

### Prerequisites

- Node.js and npm installed
  ```sh
  node -v
  npm -v
  ```
- Python 3.6+ installed
  ```sh
  python3 --version
  ```
- MongoDB installed and running
- Perplexity AI API key
- Reddit API credentials (client ID, client secret, user agent)
- Google Places API key

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/evanbabic/wbuy.git
   cd wbuy
   ```

2. Install frontend dependencies:
   ```sh
   cd wbuy
   npm install
   ```

3. Configure environment variables:
   - Create a `.env` file in the `backend/` directory.
   - Add the following variables:
     ```
     PERPLEXITY_API_KEY=YOUR_PERPLEXITY_API_KEY
     REDDIT_CLIENT_ID=YOUR_REDDIT_CLIENT_ID
     REDDIT_CLIENT_SECRET=YOUR_REDDIT_CLIENT_SECRET
     REDDIT_USER_AGENT=ProductResearchScraper v1.0
     GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
     ```

4. Install backend dependencies:
   ```sh
   cd backend
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```sh
   python server.py
   ```

6. Run the Next.js development server:
   ```sh
   cd wbuy
   npm run dev
   ```

7. Load the browser extension:
   - Open Chrome and go to `chrome://extensions/`.
   - Enable "Developer mode".
   - Click "Load unpacked" and select the `extension/` directory.

## Acknowledgments

- This README was created using [gitreadme.dev](https://gitreadme.dev) — an AI tool that looks at your entire codebase to instantly generate high-quality README files.
