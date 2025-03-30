document.addEventListener('DOMContentLoaded', async () => {
    const contentDiv = document.getElementById('content');
  
    try {
      // Get the current active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Check if we're on an Amazon product page
      if (!tab.url.includes('amazon.com')) {
        contentDiv.innerHTML = '<div class="error">This extension only works on Amazon product pages.</div>';
        return;
      }
      
      // Extract product data from the page
      chrome.tabs.sendMessage(tab.id, { action: 'extractProductData' }, async (response) => {
        if (chrome.runtime.lastError) {
          contentDiv.innerHTML = `<div class="error">Error: ${chrome.runtime.lastError.message}</div>`;
          return;
        }
        
        if (response.error) {
          contentDiv.innerHTML = `<div class="error">Error: ${response.error}</div>`;
          return;
        }
        
        // Extract first 4 words from the product title
        const first4Words = response.title.split(' ').slice(0, 5).join(' ');
        
        // Show product title
        contentDiv.innerHTML = `<div class="product-title">Analyzing: ${first4Words}</div>
                                <div class="loading">Fetching Reddit comments...</div>`;
        
        // Send first 4 words of product name to your API
        try {
          const apiResponse = await fetchRedditComments(first4Words);
          displayRedditComments(apiResponse, contentDiv);
        } catch (error) {
          contentDiv.innerHTML = `<div class="error">Error fetching comments: ${error.message}</div>`;
        }
      });
      
    } catch (error) {
      contentDiv.innerHTML = `<div class="error">An error occurred: ${error.message}</div>`;
    }
  });
  
  // Fetch Reddit comments from API
  async function fetchRedditComments(productName) {
    const apiUrl = `http://127.0.0.1:5000/api/analyze?category=thoughts&query=${encodeURIComponent(productName)}`;
    
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const rawText = await response.text();
    let jsonText = rawText;
    if (rawText.includes('```json')) {
      const match = rawText.match(/```json\s*([\s\S]*?)\s*```/);
      if (match && match[1]) {
        jsonText = match[1].trim();
      }
    }
    
    try {
      return JSON.parse(jsonText);
    } catch (error) {
      console.error("Error parsing JSON:", error);
      throw new Error("Failed to parse API response as JSON");
    }
  }
  
  // Display Reddit comments and posts
  function displayRedditComments(apiResponse, contentDiv) {
    if (!apiResponse) {
      contentDiv.innerHTML = '<div class="error">Empty API response received.</div>';
      return;
    }
  
    if (!apiResponse.recommendations || !Array.isArray(apiResponse.recommendations) || apiResponse.recommendations.length === 0) {
      contentDiv.innerHTML = '<div class="error">No Reddit content found in the response. Raw response: ' + 
      JSON.stringify(apiResponse).substring(0, 200) + '...</div>';
      return;
    }
    
    let html = '<h3>Here\'s what reddit has to say:</h3>';
    
    apiResponse.recommendations.forEach(rec => {
      html += `<div class="reddit-section">`;
      html += `<h4 class="product-name">${rec.name}</h4>`;
      
      if (rec.posts && rec.posts.length > 0) {
        rec.posts.forEach(post => {
          if (post.title) {
            const postUrl = post.url || '#';
            html += `<div class="post-title"><a href="${postUrl}" target="_blank">${post.title}</a></div>`;
          }
          
          if (post.comments && post.comments.length > 0) {
            post.comments.forEach(comment => {
              html += `<div class="comment-text">"${comment}"</div>`;
            });
          }
        });
      } else if (rec.quoted_reviews && rec.quoted_reviews.length > 0) {
        rec.quoted_reviews.forEach(quote => {
          html += `<div class="comment-text">"${quote}"</div>`;
        });
      }
      
      html += `</div>`;
    });
    
    html += '<button id="refreshBtn">Refresh Comments</button>';
    contentDiv.innerHTML = html;
  
    document.getElementById('refreshBtn').addEventListener('click', () => {
      location.reload();
    });
  }
  