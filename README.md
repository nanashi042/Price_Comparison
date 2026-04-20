# 🛒 Price Comparison Tool

A Flask-based web application that helps users compare product prices across multiple e-commerce platforms (Amazon, Flipkart, eBay) and identify the best deal quickly.

## 📌 Features

- **Multi-Platform Search**: Compare prices from Amazon, Flipkart, and eBay
- **Price Tracking**: Store price history for trend analysis
- **Search History**: Keep track of all searches performed
- **RESTful API**: Clean API endpoints for integration
- **SQLite Database**: Lightweight database for local storage
- **Error Handling**: Robust error handling for scraping failures

## 🏗️ Project Structure

```
price_comparison_tool/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Database models
│   │   ├── product.py        # Product model
│   │   ├── price_record.py  # Price history model
│   │   └── search_history.py # Search history model
│   ├── scrapers/             # Web scrapers
│   │   ├── base_scraper.py   # Base scraper class
│   │   ├── amazon_scraper.py
│   │   ├── flipkart_scraper.py
│   │   └── ebay_scraper.py
│   ├── routes/               # API endpoints
│   │   ├── search_routes.py  # Search endpoints
│   │   └── history_routes.py # History endpoints
│   └── utils/                # Utility functions
│       ├── scraper_utils.py  # Helper functions
│       └── error_handler.py  # Error handling
├── config/
│   └── config.py             # Configuration settings
├── templates/                # HTML templates (future)
├── static/                   # Static files (future)
├── run.py                    # Entry point
├── requirements.txt          # Dependencies
├── .env                      # Environment variables
└── README.md
```

## 🛠️ Installation

### 1. Clone/Setup the project

Navigate to the project directory:
```bash
cd price_comparison_tool
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python run.py
```

The application will start at `http://localhost:5000`

## 🔌 API Endpoints

### Search for a Product
```
GET /api/search/product?q=laptop
```

**Response:**
```json
{
  "product": {
    "id": 1,
    "name": "laptop",
    "amazon": {
      "price": 45000,
      "url": "https://amazon.in/..."
    },
    "flipkart": {
      "price": 42000,
      "url": "https://flipkart.com/..."
    },
    "ebay": {
      "price": null,
      "url": null
    },
    "cheapest": {
      "site": "flipkart",
      "price": 42000
    }
  }
}
```

### Get Product Results
```
GET /api/search/results/1
```

### Get Search History
```
GET /api/history/searches?limit=50
```

### Get Price History
```
GET /api/history/prices/1?limit=100
```

### Get Trending Searches
```
GET /api/history/trending?limit=10
```

## ⚙️ Configuration

Edit `config/config.py` to customize:
- Database URI
- Cache timeout
- Scraper timeout
- Max retries
- User agents

## 🔒 Known Limitations

- **Anti-Scraping Measures**: E-commerce sites have anti-scraping mechanisms
  - Consider using API keys when available
  - Implement rate limiting and delays between requests
  - Rotate user agents and proxies

- **Dynamic Content**: Some sites render content with JavaScript
  - Use Selenium for JavaScript-heavy sites
  - Consider using headless browsers

- **Structure Changes**: Website HTML structure changes frequently
  - Monitor and update CSS selectors regularly
  - Implement automated monitoring for scraper failures

## 🚀 Future Enhancements

- [ ] Web UI with React/Vue
- [ ] Email notifications for price drops
- [ ] Machine learning for price prediction
- [ ] Browser extension
- [ ] Mobile app
- [ ] Headless browser support (Selenium/Playwright)
- [ ] Proxy rotation
- [ ] Rate limiting per IP
- [ ] Database migrations with Alembic
- [ ] Caching with Redis

## 📝 License

MIT License

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📧 Contact

For questions, please reach out or create an issue.
