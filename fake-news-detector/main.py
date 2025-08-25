from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    # Check API keys
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    api_keys_configured = bool(perplexity_key and openai_key)
    
    return render_template('index.html', api_keys_configured=api_keys_configured)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    input_type = data.get('input_type')
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Por favor, insira uma URL ou texto para análise.'}), 400
    
    # Here would be the actual analysis logic
    # For now, return a demo response
    return jsonify({
        'status': 'success',
        'message': 'Análise em progresso... (Este é um demo)',
        'input_type': input_type,
        'content': content[:100] + '...' if len(content) > 100 else content
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)