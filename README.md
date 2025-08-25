# 🔍 Fake News Detection System

A sophisticated web application powered by Perplexity AI for detecting and analyzing potential misinformation in news articles.

## ✨ Features

- **🌐 URL Analysis** - Analyze news articles directly from web URLs
- **📝 Text Analysis** - Paste news content for direct analysis
- **🤖 AI-Powered Verification** - Uses Perplexity AI for fact-checking
- **📊 Credibility Scoring** - Provides detailed credibility assessments
- **🔗 Source Citations** - Automatic linking to reliable verification sources
- **📱 Responsive Design** - Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Perplexity AI API key ([Get one here](https://www.perplexity.ai/settings/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/leonardobora/fake-news-pplx.git
   cd fake-news-pplx
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Perplexity API key
   # PERPLEXITY_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**
   ```bash
   python web_app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📖 Usage

### Analyzing News by URL
1. Go to the web interface at `http://localhost:5000`
2. Click on "Analisar por URL" (Analyze by URL)
3. Paste the news article URL
4. Click "Analisar URL" to get comprehensive analysis

### Analyzing News by Text
1. Click on "Analisar Texto" (Analyze Text)
2. Paste the news article text directly
3. Click "Analisar Texto" to get analysis results

### Understanding Results
The system provides:
- **Veracidade** (Truthfulness) - Fact verification of main claims
- **Qualidade** (Quality) - Information coherence and reliability
- **Sinais de Fake News** - Detection of misinformation patterns
- **Recomendação Final** - Final credibility recommendation
- **Fontes** (Sources) - Reliable sources for verification

## 🛠️ Technical Architecture

- **Backend**: Flask (Python web framework)
- **AI Engine**: Perplexity AI API for fact-checking
- **Content Extraction**: BeautifulSoup for web scraping
- **Frontend**: Responsive HTML/CSS/JavaScript
- **Environment**: Python-dotenv for configuration

## 📁 Project Structure

```
fake-news-pplx/
├── web_app.py              # Main Flask application
├── templates/              # HTML templates
│   ├── index.html         # Main page
│   └── result.html        # Results page
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PERPLEXITY_API_KEY` | Your Perplexity AI API key | Yes |
| `SECRET_KEY` | Flask secret key for sessions | No (auto-generated) |
| `FLASK_ENV` | Flask environment (development/production) | No |

### API Configuration

The application uses the Perplexity AI "sonar" model for real-time web search and fact-checking. The API provides:
- Real-time web search capabilities
- Source attribution and citations
- Multilingual support
- Content verification against reliable sources

## 🚀 Deployment

### Production Deployment

1. **Set environment to production**
   ```bash
   export FLASK_ENV=production
   ```

2. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
   ```

3. **Configure reverse proxy** (nginx, Apache, etc.)

4. **Set up SSL/HTTPS** for security

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_app.py"]
```

## 🧪 Testing

The application includes built-in error handling and validation:
- URL validation and content extraction
- API error handling and fallbacks
- Input sanitization and security
- Responsive design testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/leonardobora/fake-news-pplx/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🔮 Future Enhancements

- Multiple language support
- Batch analysis capabilities
- API endpoints for programmatic access
- Enhanced visualization of results
- Integration with social media platforms
- Historical analysis tracking

---

**⚠️ Disclaimer**: This tool is designed to assist in fact-checking and should not be the sole source for determining information credibility. Always verify important information through multiple reliable sources.