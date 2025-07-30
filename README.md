# RankMyBrand GEO Calculator

Production-ready Generative Engine Optimization (GEO) metric calculation system based on Princeton research.

## Features

- **Accurate Metrics**: Calculates statistics density, quotation authority, content fluency, and more
- **AI Visibility Tracking**: Monitors brand presence across ChatGPT, Perplexity, and Google AI
- **Real-time Analysis**: Get results in under 10 seconds
- **RESTful API**: Easy integration with any platform
- **Dashboard**: Beautiful web interface for content analysis
- **Transparent Scoring**: All calculations are explainable and verifiable

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/rankmybrand/geo-calculator.git
cd geo-calculator

Create environment file:
cp backend/.env.example backend/.env
# Edit .env with your API keys (optional)

Start the services:
docker-compose up -d

Access the dashboard:
Dashboard: http://localhost:3000
API Docs: http://localhost:8000/api/v1/docs
Manual Installation
Backend setup:
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend setup:
cd frontend
# Serve with any static file server
python -m http.server 3000

API Usage
Analyze Content
curl -X POST http://localhost:8000/api/v1/geo/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content": "Your content here...",
    "brand_terms": ["brand"],
    "target_queries": ["example query"]
  }'

Response Format
{
  "geo_score": 75.5,
  "metrics": {
    "statistics": 82.3,
    "quotation": 71.5,
    "fluency": 78.9,
    "relevance": 85.2,
    "authority": 65.0,
    "ai_visibility": 70.0
  },
  "recommendations": [
    {
      "priority": "high",
      "metric": "authority",
      "action": "Build domain authority through quality backlinks",
      "impact": "Could improve GEO score by 5%"
    }
  ],
  "confidence": "high"
}

How It Works
The GEO Calculator implements metrics based on the Princeton research paper "GEO: Generative Engine Optimization" with practical adaptations:
Statistics Density: Measures the use of data and numbers in content
Quotation Authority: Analyzes expert quotes and their sources
Content Fluency: Evaluates readability for AI parsing
Relevance Score: Semantic alignment with target queries
Authority Signal: Domain trust indicators
AI Visibility: Actual presence in AI search results
Configuration
Edit backend/.env:
# Optional API Keys
PERPLEXITY_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./data/geo_metrics.db

# Rate Limiting
RATE_LIMIT_PER_HOUR=100

Development
Running Tests
cd backend
pytest tests/

Adding New Metrics
Add calculation method to backend/app/core/metrics.py
Update the composite score in backend/app/core/calculator.py
Add UI components in frontend/dashboard.js
Integration
JavaScript SDK
import { RankMyBrandGEO } from './rankmybrand-geo-sdk.js';

const geo = new RankMyBrandGEO('https://your-api-url.com');
const result = await geo.analyzeContent({...});

Python Client
import requests

response = requests.post(
    'http://localhost:8000/api/v1/geo/analyze',
    json={
        'url': 'https://example.com',
        'content': 'Your content...'
    }
)
result = response.json()

Limitations & Transparency
This tool implements what can be accurately measured:
✅ What We Measure:
Statistical density and distribution
Quote quality and attribution
Content structure and readability
Basic AI platform visibility
❌ What We Don't Measure:
Princeton's exact Position-Adjusted Word Count (requires consistent citation format)
True click-through probability (no user data access)
Cross-platform citation tracking (formats vary)
Contributing
We welcome contributions! Please see CONTRIBUTING.md for guidelines.
License
MIT License - see LICENSE.md
Support
Documentation: https://docs.rankmybrand.ai/geo
Issues: https://github.com/rankmybrand/geo-calculator/issues
Email: support@rankmybrand.ai
Acknowledgments
Based on research from:
Princeton University
Georgia Tech
Allen Institute for AI
IIT Delhi
Paper: "GEO: Generative Engine Optimization" (Aggarwal et al., 2024)

## Production Deployment

To deploy this system in production:

1. **Security**:
   - Add rate limiting middleware
   - Implement API key authentication
   - Use HTTPS everywhere
   - Sanitize all inputs

2. **Performance**:
   - Add Redis for caching
   - Use PostgreSQL for production database
   - Implement queue system for batch processing
   - Add CDN for frontend assets

3. **Monitoring**:
   - Add logging with structured output
   - Implement health checks
   - Set up alerts for failures
   - Track API usage metrics

4. **Scaling**:
   - Use Kubernetes for orchestration
   - Implement horizontal scaling
   - Add load balancer
   - Use managed database service
