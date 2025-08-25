#!/usr/bin/env python3
"""
Flask Web Interface para o Sistema de Detecção de Fake News
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

class NewsAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
    
    def extract_content_from_url(self, url):
        """Extrai conteúdo básico de uma URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts, styles, etc.
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Extrair título
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Título não encontrado"
            
            # Tentar encontrar o conteúdo principal
            content_selectors = [
                'article', '[role="main"]', '.content', '.post-content', 
                '.entry-content', '.article-body', '.story-body'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            # Extrair e limpar texto
            text = main_content.get_text() if main_content else ""
            text = re.sub(r'\\s+', ' ', text)
            text = text.strip()
            
            # Limitar tamanho
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            return {
                'title': title_text,
                'content': text,
                'url': url,
                'domain': urlparse(url).netloc,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': f"Erro ao extrair conteúdo: {str(e)}",
                'url': url,
                'status': 'error'
            }
    
    def query_perplexity(self, query):
        """Consulta a API Perplexity para verificação"""
        if not self.api_key:
            return {
                'content': "API Perplexity não configurada. Configure PERPLEXITY_API_KEY no arquivo .env",
                'status': 'warning'
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Você é um especialista em verificação de fatos e análise de credibilidade de fontes. "
                            "Forneça análises objetivas, cite fontes quando possível, e indique seu nível de confiança. "
                            "Seja conciso mas preciso em suas avaliações."
                        )
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # Adicionar citações se disponíveis
                if "citations" in result and result["citations"]:
                    content += "\n\n**Fontes:**\n"
                    for i, citation in enumerate(result["citations"][:3], 1):
                        content += f"{i}. {citation}\n"
                
                return {'content': content, 'status': 'success'}
            else:
                return {'content': "Não foi possível obter resposta da API Perplexity", 'status': 'warning'}
                
        except Exception as e:
            return {'content': f"Erro na consulta à API: {str(e)}", 'status': 'error'}
    
    def analyze_url(self, url):
        """Analisa uma URL completa"""
        # Extrair conteúdo
        content_data = self.extract_content_from_url(url)
        
        if content_data['status'] == 'error':
            return content_data
        
        # Preparar query para verificação
        verification_query = f"""
        Analise esta notícia e forneça uma avaliação estruturada:
        
        Domínio: {content_data['domain']}
        Título: {content_data['title']}
        Conteúdo: {content_data['content'][:1000]}...
        
        Por favor, avalie:
        1. Credibilidade da fonte (0-10)
        2. Veracidade das principais afirmações
        3. Sinais de desinformação ou fake news
        4. Recomendação final
        5. Nível de confiança na análise (%)
        
        Seja conciso e direto.
        """
        
        # Consultar Perplexity
        analysis = self.query_perplexity(verification_query)
        
        return {
            'content_data': content_data,
            'analysis': analysis,
            'status': 'success'
        }
    
    def analyze_text(self, text):
        """Analisa um texto diretamente"""
        # Preparar query para verificação
        verification_query = f"""
        Analise este texto de notícia:
        
        Texto: {text[:1500]}...
        
        Por favor, avalie:
        1. Veracidade das principais afirmações
        2. Qualidade e coerência das informações
        3. Sinais de desinformação ou fake news
        4. Recomendação final
        5. Nível de confiança na análise (%)
        
        Seja conciso e direto.
        """
        
        # Consultar Perplexity
        analysis = self.query_perplexity(verification_query)
        
        return {
            'text_data': {
                'content': text[:500] + "..." if len(text) > 500 else text,
                'length': len(text)
            },
            'analysis': analysis,
            'status': 'success'
        }

# Instanciar o analisador
analyzer = NewsAnalyzer()

@app.route('/')
def index():
    """Página principal"""
    api_status = "🟢 Configurada" if analyzer.api_key else "🔴 Não configurada"
    return render_template('index.html', api_status=api_status)

@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    """Endpoint para análise de URL"""
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Por favor, forneça uma URL válida', 'error')
        return redirect(url_for('index'))
    
    # Validar URL básica
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = analyzer.analyze_url(url)
        return render_template('result.html', result=result, analysis_type='url')
    except Exception as e:
        flash(f'Erro na análise: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    """Endpoint para análise de texto"""
    text = request.form.get('text', '').strip()
    
    if not text or len(text) < 50:
        flash('Por favor, forneça um texto com pelo menos 50 caracteres', 'error')
        return redirect(url_for('index'))
    
    try:
        result = analyzer.analyze_text(text)
        return render_template('result.html', result=result, analysis_type='text')
    except Exception as e:
        flash(f'Erro na análise: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint para análise programática"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados JSON necessários'}), 400
    
    analysis_type = data.get('type')
    
    if analysis_type == 'url':
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL necessária'}), 400
        result = analyzer.analyze_url(url)
    elif analysis_type == 'text':
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Texto necessário'}), 400
        result = analyzer.analyze_text(text)
    else:
        return jsonify({'error': 'Tipo de análise inválido (url ou text)'}), 400
    
    return jsonify(result)

@app.route('/status')
def status():
    """Endpoint de status do sistema"""
    return jsonify({
        'status': 'online',
        'perplexity_api': 'configured' if analyzer.api_key else 'not_configured',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Criar diretório de templates se não existir
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    print("🌐 Iniciando servidor Flask...")
    print("📱 Acesse: http://localhost:5000")
    print("🔑 Status da API Perplexity:", "🟢 Configurada" if analyzer.api_key else "🔴 Não configurada")
    
    app.run(debug=True, host='0.0.0.0', port=5000)