#!/usr/bin/env python3
"""
Flask Web Interface para o Sistema de Detecção de Fake News
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, abort
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import logging
from functools import wraps
import time
from datetime import datetime, timezone

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Configurações de segurança
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Rate limiting simples (em produção usar Redis/Memcached)
request_counts = {}
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hora

def rate_limit(f):
    """Decorator para rate limiting básico"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        current_time = time.time()
        
        # Limpar contadores antigos
        for ip, data in list(request_counts.items()):
            if current_time - data['timestamp'] > RATE_LIMIT_WINDOW:
                del request_counts[ip]
        
        # Verificar rate limit
        if client_ip in request_counts:
            if request_counts[client_ip]['count'] >= RATE_LIMIT_REQUESTS:
                abort(429)  # Too Many Requests
            request_counts[client_ip]['count'] += 1
        else:
            request_counts[client_ip] = {'count': 1, 'timestamp': current_time}
        
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(text, max_length=50000):
    """Sanitiza entrada do usuário"""
    if not text:
        return ""
    
    # Limitar tamanho
    text = text[:max_length]
    
    # Remover caracteres perigosos (XSS prevention)
    text = re.sub(r'[<>"\']', '', text)
    
    # Remover caracteres de controle
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

class NewsAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
        
        if self.api_key:
            logger.info("Perplexity API configurada")
        else:
            logger.warning("Perplexity API não configurada")
    
    def extract_content_from_url(self, url):
        """Extrai conteúdo básico de uma URL com tratamento de erro melhorado"""
        try:
            # Validar URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'error': "URL inválida. Verifique o formato (deve começar com http:// ou https://)",
                    'url': url,
                    'status': 'error'
                }
            
            # Verificar se é um domínio suspeito (lista básica)
            suspicious_domains = ['bit.ly', 'tinyurl.com', 'shortened.com']
            if any(domain in parsed_url.netloc.lower() for domain in suspicious_domains):
                logger.warning(f"URL suspeita detectada: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            logger.info(f"Extraindo conteúdo de: {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Verificar tamanho do conteúdo
            if len(response.content) > 10 * 1024 * 1024:  # 10MB
                return {
                    'error': "Conteúdo muito grande para processar",
                    'url': url,
                    'status': 'error'
                }
            
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
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Verificar se há conteúdo suficiente
            if len(text) < 100:
                return {
                    'error': "Conteúdo insuficiente extraído da URL. Verifique se a página contém texto.",
                    'url': url,
                    'status': 'error'
                }
            
            # Limitar tamanho
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            logger.info(f"Conteúdo extraído com sucesso: {len(text)} caracteres")
            
            return {
                'title': sanitize_input(title_text),
                'content': sanitize_input(text),
                'url': url,
                'domain': parsed_url.netloc,
                'status': 'success'
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao acessar URL: {url}")
            return {
                'error': f"Timeout ao acessar a URL (limite: {self.timeout}s). Tente novamente.",
                'url': url,
                'status': 'error'
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão para URL: {url}")
            return {
                'error': "Erro de conexão. Verifique se a URL está acessível.",
                'url': url,
                'status': 'error'
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP para URL {url}: {e}")
            return {
                'error': f"Erro HTTP: {e.response.status_code}. A página pode não existir ou estar indisponível.",
                'url': url,
                'status': 'error'
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao extrair conteúdo de {url}: {str(e)}")
            return {
                'error': f"Erro inesperado ao extrair conteúdo: {str(e)}",
                'url': url,
                'status': 'error'
            }
    
    def query_perplexity(self, query):
        """Consulta a API Perplexity para verificação com retry e cache básico"""
        if not self.api_key:
            logger.warning("Tentativa de usar API Perplexity sem chave configurada")
            return {
                'content': "API Perplexity não configurada. Configure PERPLEXITY_API_KEY no arquivo .env",
                'status': 'warning'
            }
        
        # Sanitizar query
        query = sanitize_input(query, max_length=2000)
        
        if len(query) < 10:
            return {
                'content': "Query muito curta para análise",
                'status': 'warning'
            }
        
        retries = 0
        while retries < self.max_retries:
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
                                "Seja conciso mas preciso em suas avaliações. "
                                "IMPORTANTE: Se não conseguir verificar algo, seja claro sobre isso."
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
                
                logger.info(f"Consultando Perplexity API (tentativa {retries + 1}/{self.max_retries})")
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
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
                    
                    logger.info("Resposta da Perplexity API recebida com sucesso")
                    return {'content': sanitize_input(content), 'status': 'success'}
                else:
                    logger.warning("Resposta vazia da Perplexity API")
                    return {'content': "Não foi possível obter resposta da API Perplexity", 'status': 'warning'}
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na API Perplexity (tentativa {retries + 1})")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(2 ** retries)  # Backoff exponencial
                    continue
                return {'content': f"Timeout na API após {self.max_retries} tentativas", 'status': 'error'}
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limit atingido na API Perplexity (tentativa {retries + 1})")
                    retries += 1
                    if retries < self.max_retries:
                        time.sleep(5 * (retries + 1))  # Esperar mais tempo para rate limit
                        continue
                    return {'content': "Rate limit atingido. Tente novamente mais tarde.", 'status': 'error'}
                else:
                    logger.error(f"Erro HTTP na API Perplexity: {e}")
                    return {'content': f"Erro na API: {e.response.status_code}", 'status': 'error'}
                    
            except Exception as e:
                logger.error(f"Erro inesperado na API Perplexity: {str(e)}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(2 ** retries)
                    continue
                return {'content': f"Erro na API após {self.max_retries} tentativas", 'status': 'error'}
        
        return {'content': "Falha em todas as tentativas de consulta à API", 'status': 'error'}
    
    def analyze_url(self, url):
        """Analisa uma URL completa com tratamento de erro robusto"""
        try:
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
            
            Seja conciso e direto. Se não conseguir verificar algo, mencione explicitamente.
            """
            
            # Consultar Perplexity
            analysis = self.query_perplexity(verification_query)
            
            # Análise adicional de URL
            domain_analysis = self._analyze_domain(content_data['domain'])
            
            return {
                'content_data': content_data,
                'analysis': analysis,
                'domain_analysis': domain_analysis,
                'status': 'success',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro inesperado na análise de URL: {str(e)}")
            return {
                'error': f"Erro inesperado na análise: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def analyze_text(self, text):
        """Analisa um texto diretamente com validação melhorada"""
        try:
            # Validar tamanho do texto
            if len(text) < 50:
                return {
                    'error': "Texto muito curto para análise (mínimo 50 caracteres)",
                    'status': 'error'
                }
            
            if len(text) > 20000:
                return {
                    'error': "Texto muito longo para análise (máximo 20.000 caracteres)",
                    'status': 'error'
                }
            
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
            
            Seja conciso e direto. Se não conseguir verificar algo, mencione explicitamente.
            """
            
            # Consultar Perplexity
            analysis = self.query_perplexity(verification_query)
            
            # Análise básica do texto
            text_analysis = self._analyze_text_quality(text)
            
            return {
                'text_data': {
                    'content': text[:500] + "..." if len(text) > 500 else text,
                    'length': len(text),
                    'word_count': len(text.split()),
                    'quality_score': text_analysis['quality_score']
                },
                'analysis': analysis,
                'text_analysis': text_analysis,
                'status': 'success',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro inesperado na análise de texto: {str(e)}")
            return {
                'error': f"Erro inesperado na análise: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def _analyze_domain(self, domain):
        """Análise básica do domínio"""
        try:
            domain = domain.lower()
            
            # Lista básica de domínios conhecidos por credibilidade
            reputable_domains = [
                'bbc.com', 'reuters.com', 'ap.org', 'cnn.com', 'g1.globo.com',
                'folha.uol.com.br', 'estadao.com.br', 'valor.com.br'
            ]
            
            suspicious_indicators = [
                '.tk', '.ml', '.ga', '.cf',  # TLDs gratuitos
                'news24', 'breaking', 'urgent',  # Palavras suspeitas
                '24h', 'real', 'truth'
            ]
            
            credibility_score = 5  # Score neutro
            
            if any(rep_domain in domain for rep_domain in reputable_domains):
                credibility_score = 8
            
            if any(sus in domain for sus in suspicious_indicators):
                credibility_score = 3
            
            return {
                'domain': domain,
                'credibility_score': credibility_score,
                'is_reputable': credibility_score >= 7,
                'has_suspicious_indicators': credibility_score <= 3
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de domínio: {str(e)}")
            return {
                'domain': domain,
                'credibility_score': 5,
                'error': str(e)
            }
    
    def _analyze_text_quality(self, text):
        """Análise básica da qualidade do texto"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            # Métricas básicas
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
            
            # Indicadores de qualidade
            quality_score = 5  # Score neutro
            
            # Textos muito curtos ou com palavras muito curtas podem ser suspeitos
            if avg_word_length < 3:
                quality_score -= 1
            elif avg_word_length > 6:
                quality_score += 1
            
            # Sentenças muito curtas ou muito longas podem indicar problemas
            if avg_sentence_length < 5:
                quality_score -= 1
            elif 10 <= avg_sentence_length <= 20:
                quality_score += 1
            
            # Detectar excesso de maiúsculas (pode indicar spam/fake news)
            uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            if uppercase_ratio > 0.1:
                quality_score -= 2
            
            # Garantir que o score fique entre 1 e 10
            quality_score = max(1, min(10, quality_score))
            
            return {
                'quality_score': quality_score,
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'uppercase_ratio': round(uppercase_ratio * 100, 2),
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()])
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de qualidade do texto: {str(e)}")
            return {
                'quality_score': 5,
                'error': str(e)
            }

# Instanciar o analisador
analyzer = NewsAnalyzer()

# Adicionar headers de segurança
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Handler para erros
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Página não encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {str(error)}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Erro interno do servidor"), 500

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({'error': 'Rate limit excedido. Tente novamente mais tarde.'}), 429

# Health check endpoint
@app.route('/health')
def health_check():
    """Endpoint de verificação de saúde do sistema"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0',
        'perplexity_api': 'configured' if analyzer.api_key else 'not_configured'
    })

@app.route('/')
def index():
    """Página principal"""
    api_status = "🟢 Configurada" if analyzer.api_key else "🔴 Não configurada"
    return render_template('index.html', api_status=api_status)

@app.route('/analyze_url', methods=['POST'])
@rate_limit
def analyze_url():
    """Endpoint para análise de URL com validação melhorada"""
    try:
        url = request.form.get('url', '').strip()
        
        if not url:
            flash('Por favor, forneça uma URL válida', 'error')
            return redirect(url_for('index'))
        
        # Sanitizar URL
        url = sanitize_input(url, max_length=2000)
        
        # Validar URL básica
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validação adicional de URL
        parsed = urlparse(url)
        if not parsed.netloc or len(parsed.netloc) < 4:
            flash('URL inválida. Verifique o formato.', 'error')
            return redirect(url_for('index'))
        
        logger.info(f"Iniciando análise de URL: {parsed.netloc}")
        
        result = analyzer.analyze_url(url)
        
        if result['status'] == 'error':
            flash(f'Erro na análise: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('index'))
        
        logger.info(f"Análise de URL concluída com sucesso: {parsed.netloc}")
        return render_template('result.html', result=result, analysis_type='url')
        
    except Exception as e:
        logger.error(f'Erro inesperado na análise de URL: {str(e)}')
        flash('Erro inesperado na análise. Tente novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/analyze_text', methods=['POST'])
@rate_limit
def analyze_text():
    """Endpoint para análise de texto com validação melhorada"""
    try:
        text = request.form.get('text', '').strip()
        
        if not text:
            flash('Por favor, forneça um texto válido', 'error')
            return redirect(url_for('index'))
        
        # Sanitizar texto
        text = sanitize_input(text, max_length=50000)
        
        if len(text) < 50:
            flash('Por favor, forneça um texto com pelo menos 50 caracteres', 'error')
            return redirect(url_for('index'))
        
        if len(text) > 20000:
            flash('Texto muito longo. Limite máximo: 20.000 caracteres', 'error')
            return redirect(url_for('index'))
        
        logger.info(f"Iniciando análise de texto: {len(text)} caracteres")
        
        result = analyzer.analyze_text(text)
        
        if result['status'] == 'error':
            flash(f'Erro na análise: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('index'))
        
        logger.info("Análise de texto concluída com sucesso")
        return render_template('result.html', result=result, analysis_type='text')
        
    except Exception as e:
        logger.error(f'Erro inesperado na análise de texto: {str(e)}')
        flash('Erro inesperado na análise. Tente novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
@rate_limit
def api_analyze():
    """API endpoint para análise programática com validação completa"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados JSON necessários', 'status': 'error'}), 400
        
        analysis_type = data.get('type')
        
        if analysis_type not in ['url', 'text']:
            return jsonify({'error': 'Tipo de análise inválido (url ou text)', 'status': 'error'}), 400
        
        if analysis_type == 'url':
            url = data.get('url')
            if not url:
                return jsonify({'error': 'URL necessária', 'status': 'error'}), 400
            
            # Sanitizar e validar URL
            url = sanitize_input(url, max_length=2000)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            if not parsed.netloc:
                return jsonify({'error': 'URL inválida', 'status': 'error'}), 400
            
            logger.info(f"API: Iniciando análise de URL: {parsed.netloc}")
            result = analyzer.analyze_url(url)
            
        elif analysis_type == 'text':
            text = data.get('text')
            if not text:
                return jsonify({'error': 'Texto necessário', 'status': 'error'}), 400
            
            # Sanitizar e validar texto
            text = sanitize_input(text, max_length=50000)
            if len(text) < 50:
                return jsonify({'error': 'Texto muito curto (mínimo 50 caracteres)', 'status': 'error'}), 400
            
            if len(text) > 20000:
                return jsonify({'error': 'Texto muito longo (máximo 20.000 caracteres)', 'status': 'error'}), 400
            
            logger.info(f"API: Iniciando análise de texto: {len(text)} caracteres")
            result = analyzer.analyze_text(text)
        
        # Adicionar timestamp ao resultado
        result['timestamp'] = datetime.now(timezone.utc).isoformat()
        result['request_type'] = 'api'
        
        logger.info(f"API: Análise concluída - status: {result.get('status', 'unknown')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'Erro inesperado na API: {str(e)}')
        return jsonify({'error': 'Erro interno do servidor', 'status': 'error'}), 500

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