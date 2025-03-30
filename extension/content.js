// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'extractProductData') {
      try {
        const productData = extractProductData();
        sendResponse(productData);
      } catch (error) {
        sendResponse({ error: error.message });
      }
    }
    return true;
  });

  document.addEventListener('click', (e) => {
    if (e.target.tagName === 'A' && e.target.href) {
      e.preventDefault();
      chrome.tabs.create({ url: e.target.href });
    }
  });
  
  function extractProductData() {
    // Check if we're on a product page
    if (!window.location.pathname.includes('/dp/') && 
        !window.location.pathname.includes('/gp/product/')) {
      throw new Error('Not a product detail page');
    }
    
    // Extract product title
    const titleElement = document.getElementById('productTitle') || 
                        document.querySelector('.product-title-word-break');
    const title = titleElement ? titleElement.textContent.trim() : '';
    
    if (!title) {
      throw new Error('Could not extract product title');
    }
    
    return {
      title: title,
      url: window.location.href
    };
  }
  