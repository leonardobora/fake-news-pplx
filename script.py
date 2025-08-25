# Criar estruturas de arquivos para o projeto de detecção de fake news
import os

# Estrutura do projeto
project_structure = {
    "fake-news-detector/": {
        "README.md": """# Fake News Detector com CrewAI e Perplexity API

Sistema de detecção de fake news utilizando multi-agentes com CrewAI, Streamlit e Perplexity API.

## Estrutura do Projeto

```
fake-news-detector/
├── main.py                 # Aplicação Streamlit principal
├── config/
│   ├── agents.yaml        # Configuração dos agentes CrewAI
│   └── tasks.yaml         # Configuração das tarefas
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── crew.py        # Definição da crew e agentes
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── perplexity_tool.py  # Ferramenta para Perplexity API
│   │   └── url_extractor.py    # Extração de conteúdo de URLs
│   └── utils/
│       ├── __init__.py
│       └── helpers.py     # Funções auxiliares
├── docs/
│   └── agents.md          # Documentação dos agentes
├── tests/
│   ├── __init__.py
│   └── test_agents.py     # Testes dos agentes
├── requirements.txt       # Dependências do projeto
└── .env.example          # Exemplo de variáveis de ambiente
```

## Instalação

1. Clone o repositório:
```bash
git clone <repo-url>
cd fake-news-detector
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

4. Execute a aplicação:
```bash
streamlit run main.py
```

## Uso

1. Abra a aplicação no navegador
2. Escolha o tipo de entrada (URL ou texto)
3. Insira o conteúdo para análise
4. Clique em "Analisar" para processar
5. Visualize os resultados da análise

## Agentes

O sistema utiliza 4 agentes especializados:

- **Content Extractor**: Extrai e limpa conteúdo de URLs
- **Fact Checker**: Verifica fatos contra fontes confiáveis
- **Source Credibility**: Avalia credibilidade da fonte
- **Final Decision**: Sintetiza resultados e toma decisão final

## Tecnologias

- CrewAI: Framework multi-agente
- Streamlit: Interface web
- Perplexity API: Validação externa
- Python 3.8+
""",
        
        "requirements.txt": """streamlit==1.29.0
crewai==0.63.6
crewai-tools==0.12.1
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
newspaper3k==0.2.8
langchain==0.1.0
openai==1.12.0
pydantic==2.5.0
PyYAML==6.0.1
""",
        
        ".env.example": """# Chaves de API
PERPLEXITY_API_KEY=pplx-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# Configurações do sistema
DEBUG=True
MAX_RETRIES=3
TIMEOUT=30
""",
        
        "main.py": """import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.crew import FakeNewsDetectorCrew
from src.utils.helpers import validate_url, clean_text

# Carregar variáveis de ambiente
load_dotenv()

def main():
    st.set_page_config(
        page_title="Detector de Fake News",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Detector de Fake News")
    st.subheader("Sistema multi-agente para validação de notícias")
    
    # Sidebar com configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verificar se as chaves de API estão configuradas
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not perplexity_key or not openai_key:
            st.error("⚠️ Configure as chaves de API no arquivo .env")
            st.stop()
        
        st.success("✅ Chaves de API configuradas")
        
        # Configurações de análise
        confidence_threshold = st.slider(
            "Limite de confiança", 0.0, 1.0, 0.7, 0.05
        )
        
        detailed_analysis = st.checkbox("Análise detalhada", value=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Entrada")
        
        # Seleção do tipo de entrada
        input_type = st.radio(
            "Tipo de entrada:",
            ["URL", "Texto"],
            horizontal=True
        )
        
        if input_type == "URL":
            url = st.text_input(
                "URL da notícia:",
                placeholder="https://exemplo.com/noticia",
                help="Cole aqui a URL da notícia que deseja verificar"
            )
            
            if url and st.button("🔍 Analisar URL", type="primary"):
                if validate_url(url):
                    with st.spinner("Analisando conteúdo..."):
                        result = analyze_content(url, input_type, confidence_threshold, detailed_analysis)
                        display_results(result)
                else:
                    st.error("URL inválida. Verifique o formato.")
        
        else:  # Texto
            text = st.text_area(
                "Texto da notícia:",
                height=200,
                placeholder="Cole aqui o texto da notícia que deseja verificar...",
                help="Insira o conteúdo completo da notícia"
            )
            
            if text and st.button("🔍 Analisar Texto", type="primary"):
                if len(text.strip()) > 50:
                    with st.spinner("Analisando conteúdo..."):
                        result = analyze_content(text, input_type, confidence_threshold, detailed_analysis)
                        display_results(result)
                else:
                    st.error("Texto muito curto. Insira pelo menos 50 caracteres.")
    
    with col2:
        st.header("ℹ️ Sobre")
        st.info(
            '''
            **Como funciona:**
            
            1. **Extração**: O sistema extrai o conteúdo da URL ou processa o texto
            2. **Verificação**: Múltiplos agentes analisam diferentes aspectos
            3. **Validação**: Consulta fontes externas via Perplexity API
            4. **Decisão**: Combina todas as análises para o resultado final
            
            **Agentes ativos:**
            - 🔍 Extrator de Conteúdo
            - ✅ Verificador de Fatos
            - 🏛️ Avaliador de Credibilidade
            - ⚖️ Decisor Final
            '''
        )

def analyze_content(content, input_type, confidence_threshold, detailed_analysis):
    \"\"\"Analisa o conteúdo usando a crew de agentes\"\"\"
    try:
        # Inicializar a crew
        crew = FakeNewsDetectorCrew()
        
        # Preparar inputs
        inputs = {
            'content': content,
            'input_type': input_type,
            'confidence_threshold': confidence_threshold,
            'detailed_analysis': detailed_analysis
        }
        
        # Executar análise
        result = crew.crew().kickoff(inputs=inputs)
        return result
        
    except Exception as e:
        st.error(f"Erro na análise: {str(e)}")
        return None

def display_results(result):
    \"\"\"Exibe os resultados da análise\"\"\"
    if not result:
        return
    
    st.header("📊 Resultados da Análise")
    
    # Resultado principal
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if result.get('is_fake', False):
            st.error("🚨 FAKE NEWS DETECTADA")
        else:
            st.success("✅ NOTÍCIA VERIFICADA")
    
    with col2:
        confidence = result.get('confidence', 0)
        st.metric("Confiança", f"{confidence:.1%}")
    
    with col3:
        risk_level = result.get('risk_level', 'Baixo')
        color = {"Alto": "🔴", "Médio": "🟡", "Baixo": "🟢"}
        st.metric("Nível de Risco", f"{color.get(risk_level, '⚪')} {risk_level}")
    
    # Detalhes da análise
    if st.expander("📋 Detalhes da Análise", expanded=True):
        
        # Análise por agente
        agents_results = result.get('agents_analysis', {})
        
        for agent_name, analysis in agents_results.items():
            with st.container():
                st.subheader(f"🤖 {agent_name}")
                st.write(analysis.get('summary', 'Nenhuma análise disponível'))
                
                if analysis.get('evidence'):
                    st.write("**Evidências:**")
                    for evidence in analysis['evidence']:
                        st.write(f"- {evidence}")
    
    # Recomendações
    if result.get('recommendations'):
        st.subheader("💡 Recomendações")
        for rec in result['recommendations']:
            st.write(f"• {rec}")

if __name__ == "__main__":
    main()
""",
    },
    
    "config/": {
        "agents.yaml": """content_extractor:
  role: "Especialista em Extração de Conteúdo"
  goal: "Extrair e limpar conteúdo de URLs ou processar texto fornecido, preparando-o para análise"
  backstory: |
    Você é um especialista em processamento de conteúdo web com vasta experiência em extração 
    de texto de diferentes formatos e fontes. Sua missão é garantir que o conteúdo seja 
    limpo, estruturado e pronto para análise pelos outros agentes.
  verbose: true
  memory: true
  max_iter: 3
  allow_delegation: false

fact_checker:
  role: "Verificador de Fatos Especializado"
  goal: "Verificar a veracidade das informações apresentadas usando fontes confiáveis e cross-referencing"
  backstory: |
    Você é um jornalista investigativo experiente com mais de 15 anos verificando fatos. 
    Você tem acesso a múltiplas fontes de informação e é especialista em identificar 
    discrepâncias, contradições e informações falsas. Você sempre busca evidências 
    concretas antes de fazer qualquer julgamento.
  verbose: true
  memory: true
  max_iter: 5
  allow_delegation: true

source_credibility:
  role: "Analista de Credibilidade de Fontes"
  goal: "Avaliar a credibilidade, reputação e viés de fontes de informação"
  backstory: |
    Você é um especialista em análise de mídia com PhD em Comunicação Social. 
    Sua especialidade é avaliar a credibilidade de fontes, identificar vieses 
    políticos ou comerciais, e determinar a confiabilidade histórica de 
    veículos de comunicação.
  verbose: true
  memory: true
  max_iter: 4
  allow_delegation: false

final_decision:
  role: "Analista Senior de Decisão"
  goal: "Sintetizar todas as análises e tomar decisão final sobre autenticidade do conteúdo"
  backstory: |
    Você é um analista senior com mais de 20 anos de experiência em análise de 
    informações e tomada de decisões críticas. Você é responsável por combinar 
    múltiplas perspectivas, pesar evidências e chegar a conclusões fundamentadas 
    sobre a veracidade de informações.
  verbose: true
  memory: true
  max_iter: 3
  allow_delegation: false
""",
        
        "tasks.yaml": """extract_content:
  description: |
    Extrair e processar o conteúdo fornecido:
    
    Se for URL:
    1. Acessar a URL e extrair o conteúdo principal
    2. Remover elementos desnecessários (ads, menus, etc.)
    3. Identificar título, autor, data de publicação
    4. Extrair o texto principal do artigo
    
    Se for texto:
    1. Limpar e estruturar o texto fornecido
    2. Identificar elementos-chave (título, pontos principais)
    3. Verificar se há metadados disponíveis
    
    Conteúdo: {content}
    Tipo: {input_type}
  expected_output: |
    Um relatório estruturado contendo:
    - Título da notícia
    - Conteúdo principal limpo e estruturado  
    - Metadados disponíveis (autor, data, fonte)
    - Resumo executivo do conteúdo
    - Pontos principais identificados
  agent: content_extractor

verify_facts:
  description: |
    Verificar a veracidade dos fatos apresentados no conteúdo extraído:
    
    1. Identificar claims específicos e verificáveis
    2. Usar a ferramenta Perplexity para buscar informações de fontes confiáveis
    3. Cross-referenciar informações com múltiplas fontes
    4. Identificar inconsistências ou contradições
    5. Verificar estatísticas, datas e eventos mencionados
    6. Avaliar se as informações estão atualizadas
    
    Use análise detalhada: {detailed_analysis}
    Conteúdo para verificação será fornecido pelo agente anterior.
  expected_output: |
    Relatório de verificação de fatos contendo:
    - Lista de claims identificados
    - Status de verificação para cada claim (Verdadeiro/Falso/Inconclusivo)
    - Fontes utilizadas para verificação
    - Evidências encontradas (a favor ou contra)
    - Nível de confiança para cada verificação
    - Inconsistências identificadas
  agent: fact_checker
  context: [extract_content]

assess_source:
  description: |
    Avaliar a credibilidade da fonte de informação:
    
    1. Analisar a reputação histórica da fonte
    2. Verificar registro de precisão em reportagens anteriores
    3. Identificar possíveis vieses políticos, comerciais ou ideológicos
    4. Avaliar transparência editorial e metodologia jornalística
    5. Verificar se a fonte segue padrões éticos de jornalismo
    6. Analisar financiamento e propriedade da fonte
    
    Considerar limite de confiança: {confidence_threshold}
  expected_output: |
    Análise de credibilidade contendo:
    - Score de credibilidade (0-100)
    - Histórico de precisão da fonte
    - Vieses identificados
    - Transparência editorial
    - Padrões jornalísticos seguidos
    - Recomendações sobre confiabilidade
    - Fatores de risco identificados
  agent: source_credibility
  context: [extract_content]

make_decision:
  description: |
    Sintetizar todas as análises e tomar decisão final sobre a autenticidade:
    
    1. Revisar análise de extração de conteúdo
    2. Considerar resultados da verificação de fatos
    3. Incorporar avaliação de credibilidade da fonte  
    4. Aplicar peso apropriado a cada análise
    5. Determstar classificação final (Fake News/Verificado/Inconclusivo)
    6. Calcular nível de confiança na decisão
    7. Fornecer recomendações para o usuário
    
    Limite de confiança configurado: {confidence_threshold}
  expected_output: |
    Decisão final estruturada contendo:
    - Classificação: FAKE NEWS / VERIFICADO / INCONCLUSIVO
    - Nível de confiança (0-100%)
    - Nível de risco (Alto/Médio/Baixo)
    - Resumo executivo da análise
    - Principais evidências que suportam a decisão
    - Recomendações para o usuário
    - Próximos passos sugeridos
    - Limitações da análise
  agent: final_decision
  context: [extract_content, verify_facts, assess_source]
"""
    },
    
    "src/": {
        "__init__.py": "",
        "agents/": {
            "__init__.py": "",
            "crew.py": """from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import yaml
import os
from ..tools.perplexity_tool import PerplexityTool
from ..tools.url_extractor import URLExtractorTool

@CrewBase
class FakeNewsDetectorCrew():
    \"\"\"Crew para detecção de fake news usando múltiplos agentes especializados\"\"\"
    
    def __init__(self):
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')
    
    def _load_config(self, file_path):
        \"\"\"Carrega configuração YAML\"\"\"
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {file_path}")
    
    @agent
    def content_extractor(self) -> Agent:
        \"\"\"Agente responsável por extrair conteúdo de URLs ou processar texto\"\"\"
        return Agent(
            config=self.agents_config['content_extractor'],
            tools=[URLExtractorTool()],
            verbose=True
        )
    
    @agent  
    def fact_checker(self) -> Agent:
        \"\"\"Agente responsável por verificar fatos usando fontes externas\"\"\"
        return Agent(
            config=self.agents_config['fact_checker'],
            tools=[PerplexityTool(), SerperDevTool()],
            verbose=True
        )
    
    @agent
    def source_credibility(self) -> Agent:
        \"\"\"Agente responsável por avaliar credibilidade da fonte\"\"\"
        return Agent(
            config=self.agents_config['source_credibility'],
            tools=[PerplexityTool()],
            verbose=True
        )
    
    @agent
    def final_decision(self) -> Agent:
        \"\"\"Agente responsável pela decisão final\"\"\"
        return Agent(
            config=self.agents_config['final_decision'],
            verbose=True
        )
    
    @task
    def extract_content_task(self) -> Task:
        \"\"\"Tarefa de extração de conteúdo\"\"\"
        return Task(
            config=self.tasks_config['extract_content'],
            agent=self.content_extractor()
        )
    
    @task
    def verify_facts_task(self) -> Task:
        \"\"\"Tarefa de verificação de fatos\"\"\"
        return Task(
            config=self.tasks_config['verify_facts'],
            agent=self.fact_checker()
        )
    
    @task
    def assess_source_task(self) -> Task:
        \"\"\"Tarefa de avaliação de credibilidade\"\"\"
        return Task(
            config=self.tasks_config['assess_source'],
            agent=self.source_credibility()
        )
    
    @task
    def make_decision_task(self) -> Task:
        \"\"\"Tarefa de decisão final\"\"\"
        return Task(
            config=self.tasks_config['make_decision'],
            agent=self.final_decision(),
            output_file='analysis_result.md'
        )
    
    @crew
    def crew(self) -> Crew:
        \"\"\"Cria a crew de detecção de fake news\"\"\"
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=None,  # Usar LLM padrão para planejamento
            memory=True
        )
"""
        },
        
        "tools/": {
            "__init__.py": "",
            "perplexity_tool.py": """from crewai_tools import BaseTool
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class PerplexityInput(BaseModel):
    \"\"\"Input para a ferramenta Perplexity\"\"\"
    query: str = Field(description="Query de pesquisa para validação de fatos")
    model: Optional[str] = Field(
        default="llama-3.1-sonar-small-128k-online", 
        description="Modelo Perplexity a ser usado"
    )

class PerplexityTool(BaseTool):
    \"\"\"Ferramenta para consultar a API do Perplexity para verificação de fatos\"\"\"
    
    name: str = "perplexity_search"
    description: str = (
        "Ferramenta para buscar informações e verificar fatos usando a API do Perplexity. "
        "Útil para cross-referencing de informações com fontes confiáveis online."
    )
    args_schema: Type[BaseModel] = PerplexityInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY não encontrada nas variáveis de ambiente")
    
    def _run(
        self, 
        query: str, 
        model: str = "llama-3.1-sonar-small-128k-online"
    ) -> str:
        \"\"\"Executa consulta na API do Perplexity\"\"\"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Você é um assistente especializado em verificação de fatos. "
                            "Forneça informações precisas, atualizadas e cite as fontes sempre que possível. "
                            "Se não tiver certeza sobre algo, indique explicitamente."
                        )
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.9,
                "return_citations": True,
                "search_domain_filter": ["reputable_sources"],
                "return_related_questions": False
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # Adicionar citações se disponíveis
                if "citations" in result:
                    citations = result.get("citations", [])
                    if citations:
                        content += "\\n\\n**Fontes:**\\n"
                        for i, citation in enumerate(citations[:5], 1):
                            content += f"{i}. {citation}\\n"
                
                return content
            else:
                return "Não foi possível obter resposta da API Perplexity"
                
        except requests.exceptions.RequestException as e:
            return f"Erro na requisição para Perplexity API: {str(e)}"
        except Exception as e:
            return f"Erro inesperado na ferramenta Perplexity: {str(e)}"
    
    async def _arun(self, query: str, model: str = "llama-3.1-sonar-small-128k-online") -> str:
        \"\"\"Versão assíncrona da execução\"\"\"
        # Para implementação assíncrona futura
        return self._run(query, model)
""",
            
            "url_extractor.py": """from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from urllib.parse import urlparse, urljoin
import time

class URLExtractorInput(BaseModel):
    \"\"\"Input para extração de conteúdo de URL\"\"\"
    url: str = Field(description="URL da notícia para extrair conteúdo")

class URLExtractorTool(BaseTool):
    \"\"\"Ferramenta para extrair conteúdo limpo de URLs de notícias\"\"\"
    
    name: str = "url_extractor"
    description: str = (
        "Extrai conteúdo principal de URLs de notícias, incluindo título, "
        "texto do artigo, autor, data de publicação e metadados relevantes."
    )
    args_schema: Type[BaseModel] = URLExtractorInput
    
    def _run(self, url: str) -> str:
        \"\"\"Extrai conteúdo da URL fornecida\"\"\"
        
        try:
            # Validar URL
            if not self._is_valid_url(url):
                return "URL inválida fornecida"
            
            # Tentar primeiro com newspaper3k
            try:
                article = Article(url)
                article.download()
                article.parse()
                
                # Extrair informações básicas
                title = article.title or "Título não encontrado"
                text = article.text or ""
                authors = article.authors or []
                publish_date = article.publish_date
                
                # Se newspaper3k não conseguir extrair texto, usar BeautifulSoup
                if not text.strip():
                    text = self._extract_with_beautifulsoup(url)
                
                # Limpar texto
                cleaned_text = self._clean_text(text)
                
                # Formatear data
                date_str = publish_date.strftime("%Y-%m-%d") if publish_date else "Data não encontrada"
                
                # Construir resultado
                result = f"""**CONTEÚDO EXTRAÍDO DA URL**

**URL:** {url}
**Título:** {title}
**Autor(es):** {', '.join(authors) if authors else 'Não informado'}
**Data de Publicação:** {date_str}

**CONTEÚDO PRINCIPAL:**
{cleaned_text}

**METADADOS:**
- Tamanho do texto: {len(cleaned_text)} caracteres
- Número de parágrafos: {len(cleaned_text.split('\\n\\n'))}
- Domínio: {urlparse(url).netloc}
"""
                
                return result
                
            except Exception as newspaper_error:
                # Fallback para BeautifulSoup se newspaper3k falhar
                return self._extract_with_beautifulsoup(url)
                
        except Exception as e:
            return f"Erro ao extrair conteúdo da URL: {str(e)}"
    
    def _is_valid_url(self, url: str) -> bool:
        \"\"\"Valida se a URL é válida\"\"\"
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_with_beautifulsoup(self, url: str) -> str:
        \"\"\"Extrai conteúdo usando BeautifulSoup como fallback\"\"\"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remover scripts, styles, etc.
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
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
            
            # Extrair título
            title_tag = soup.find('title') or soup.find('h1')
            title = title_tag.get_text().strip() if title_tag else "Título não encontrado"
            
            # Extrair texto
            text = main_content.get_text() if main_content else ""
            cleaned_text = self._clean_text(text)
            
            result = f"""**CONTEÚDO EXTRAÍDO (FALLBACK)**

**URL:** {url}
**Título:** {title}
**Método:** BeautifulSoup (fallback)

**CONTEÚDO PRINCIPAL:**
{cleaned_text}

**METADADOS:**
- Tamanho do texto: {len(cleaned_text)} caracteres
- Domínio: {urlparse(url).netloc}
"""
            
            return result
            
        except Exception as e:
            return f"Erro no fallback de extração: {str(e)}"
    
    def _clean_text(self, text: str) -> str:
        \"\"\"Limpa e formata o texto extraído\"\"\"
        if not text:
            return "Texto não encontrado"
        
        # Remover espaços extras e quebras de linha desnecessárias
        text = re.sub(r'\\s+', ' ', text)
        text = re.sub(r'\\n\\s*\\n', '\\n\\n', text)
        
        # Remover padrões comuns de menu/navegação
        patterns_to_remove = [
            r'Home\\s*>.*?\\n',
            r'Menu\\s*\\n',
            r'Compartilhar.*?\\n',
            r'Imprimir.*?\\n',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Limitar tamanho se muito grande
        if len(text) > 10000:
            text = text[:10000] + "\\n\\n[TEXTO TRUNCADO...]"
        
        return text.strip()
    
    async def _arun(self, url: str) -> str:
        \"\"\"Versão assíncrona\"\"\"
        return self._run(url)
"""
        },
        
        "utils/": {
            "__init__.py": "",
            "helpers.py": """import re
from urllib.parse import urlparse
from typing import Dict, Any, List

def validate_url(url: str) -> bool:
    \"\"\"Valida se uma URL está em formato válido\"\"\"
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def clean_text(text: str) -> str:
    \"\"\"Limpa texto removendo caracteres especiais e formatação\"\"\"
    if not text:
        return ""
    
    # Remover espaços extras
    text = re.sub(r'\\s+', ' ', text)
    
    # Remover caracteres de controle
    text = re.sub(r'[\\x00-\\x1f\\x7f-\\x9f]', '', text)
    
    return text.strip()

def extract_key_points(text: str, max_points: int = 5) -> List[str]:
    \"\"\"Extrai pontos-chave do texto\"\"\"
    if not text:
        return []
    
    # Dividir em sentenças
    sentences = re.split(r'[.!?]+', text)
    
    # Filtrar sentenças muito curtas ou muito longas
    filtered_sentences = [
        s.strip() for s in sentences 
        if 20 <= len(s.strip()) <= 200
    ]
    
    # Retornar as primeiras sentenças (simplificado)
    return filtered_sentences[:max_points]

def calculate_confidence_score(factors: Dict[str, float]) -> float:
    \"\"\"Calcula score de confiança baseado em múltiplos fatores\"\"\"
    if not factors:
        return 0.0
    
    # Pesos para diferentes fatores
    weights = {
        'source_credibility': 0.3,
        'fact_verification': 0.4,
        'content_quality': 0.2,
        'consistency': 0.1
    }
    
    weighted_score = 0.0
    total_weight = 0.0
    
    for factor, score in factors.items():
        if factor in weights:
            weighted_score += score * weights[factor]
            total_weight += weights[factor]
    
    return weighted_score / total_weight if total_weight > 0 else 0.0

def format_analysis_result(result: Dict[str, Any]) -> str:
    \"\"\"Formata resultado da análise para exibição\"\"\"
    if not result:
        return "Nenhum resultado disponível"
    
    formatted = f\"\"\"
# Análise de Fake News

## Resultado: {result.get('classification', 'Não determinado')}
**Confiança:** {result.get('confidence', 0):.1%}
**Nível de Risco:** {result.get('risk_level', 'Não avaliado')}

## Resumo
{result.get('summary', 'Resumo não disponível')}

## Evidências
{chr(10).join(f"• {evidence}" for evidence in result.get('evidence', []))}

## Recomendações
{chr(10).join(f"• {rec}" for rec in result.get('recommendations', []))}
\"\"\"
    
    return formatted.strip()

def get_risk_level(confidence: float, is_fake: bool) -> str:
    \"\"\"Determina nível de risco baseado na confiança e classificação\"\"\"
    if is_fake:
        if confidence >= 0.8:
            return "Alto"
        elif confidence >= 0.6:
            return "Médio"
        else:
            return "Baixo"
    else:
        if confidence >= 0.8:
            return "Baixo"
        elif confidence >= 0.6:
            return "Médio"
        else:
            return "Alto"  # Baixa confiança em notícia real também é risco

def sanitize_input(text: str, max_length: int = 50000) -> str:
    \"\"\"Sanitiza entrada do usuário\"\"\"
    if not text:
        return ""
    
    # Limitar tamanho
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remover caracteres perigosos
    text = re.sub(r'[<>\"\'&]', '', text)
    
    return text.strip()
"""
        }
    },
    
    "docs/": {
        "agents.md": """# Documentação dos Agentes - Sistema de Detecção de Fake News

## Visão Geral

Este sistema utiliza uma arquitetura multi-agente baseada no framework CrewAI para detectar fake news de forma colaborativa e especializada. Cada agente tem uma responsabilidade específica no pipeline de análise.

## Arquitetura do Sistema

### 1. Content Extractor Agent (Agente Extrator de Conteúdo)

**Papel:** Especialista em Extração de Conteúdo  
**Objetivo:** Extrair e limpar conteúdo de URLs ou processar texto fornecido

#### Responsabilidades:
- Acessar URLs e extrair conteúdo principal
- Remover elementos desnecessários (advertisements, menus, etc.)
- Identificar metadados (título, autor, data)
- Estruturar o conteúdo para análise
- Processar texto diretamente fornecido

#### Ferramentas Utilizadas:
- `URLExtractorTool`: Extração de conteúdo web
- `newspaper3k`: Parsing avançado de artigos
- `BeautifulSoup`: Fallback para extração HTML

#### Configurações:
- `max_iter`: 3
- `allow_delegation`: false
- `memory`: true

---

### 2. Fact Checker Agent (Agente Verificador de Fatos)

**Papel:** Verificador de Fatos Especializado  
**Objetivo:** Verificar veracidade das informações usando fontes confiáveis

#### Responsabilidades:
- Identificar claims específicos e verificáveis
- Buscar informações em fontes confiáveis
- Cross-referenciar dados com múltiplas fontes
- Identificar inconsistências temporais
- Verificar estatísticas e eventos mencionados

#### Ferramentas Utilizadas:
- `PerplexityTool`: Consulta à API Perplexity para fact-checking
- `SerperDevTool`: Busca web adicional
- Acesso a bases de dados de fact-checking

#### Configurações:
- `max_iter`: 5
- `allow_delegation`: true
- `memory`: true

---

### 3. Source Credibility Agent (Agente de Credibilidade)

**Papel:** Analista de Credibilidade de Fontes  
**Objetivo:** Avaliar credibilidade, reputação e viés das fontes

#### Responsabilidades:
- Analisar histórico de precisão da fonte
- Identificar vieses políticos/comerciais
- Verificar transparência editorial
- Avaliar metodologia jornalística
- Analisar financiamento e propriedade

#### Ferramentas Utilizadas:
- `PerplexityTool`: Pesquisa sobre reputação de fontes
- Bases de dados de credibilidade de mídia
- Análise de padrões editoriais

#### Configurações:
- `max_iter`: 4
- `allow_delegation`: false
- `memory`: true

---

### 4. Final Decision Agent (Agente de Decisão Final)

**Papel:** Analista Senior de Decisão  
**Objetivo:** Sintetizar análises e tomar decisão final sobre autenticidade

#### Responsabilidades:
- Combinar resultados de todos os agentes
- Aplicar pesos apropriados às análises
- Calcular nível de confiança
- Determinar classificação final
- Fornecer recomendações ao usuário

#### Configurações:
- `max_iter`: 3
- `allow_delegation`: false
- `memory`: true

---

## Fluxo de Trabalho

### Processo Sequential

1. **Extração** → Content Extractor processa entrada
2. **Verificação** → Fact Checker analisa claims (paralelo)
3. **Credibilidade** → Source Credibility avalia fonte (paralelo)  
4. **Decisão** → Final Decision sintetiza resultados

### Interdependências

- Fact Checker e Source Credibility dependem do Content Extractor
- Final Decision depende de todos os agentes anteriores
- Contexto é compartilhado entre agentes relevantes

---

## Configurações de Qualidade

### Limites de Confiança
- **Alto**: ≥ 80% - Decisão confiável
- **Médio**: 60-79% - Cautela recomendada  
- **Baixo**: < 60% - Análise adicional necessária

### Níveis de Risco
- **Alto**: Fake news com alta confiança
- **Médio**: Resultados inconclusivos
- **Baixo**: Conteúdo verificado como autêntico

---

## Boas Práticas de Desenvolvimento

### 1. Configuração de Agentes

```yaml
agent_name:
  role: "Papel específico e claro"
  goal: "Objetivo mensurável"
  backstory: "Contexto e expertise"
  verbose: true
  memory: true
  max_iter: 3-5
  allow_delegation: true/false
```

### 2. Design de Tasks

```yaml
task_name:
  description: "Instruções detalhadas e específicas"
  expected_output: "Formato estruturado esperado"
  agent: agent_responsavel
  context: [dependencias]
```

### 3. Gerenciamento de Memória

- Ativar memória para contexto entre execuções
- Limpar memória periodicamente para evitar poluição
- Usar contexto específico para dependências

### 4. Tratamento de Erros

- Implementar retry logic para chamadas de API
- Validar entradas antes do processamento
- Fornecer fallbacks para falhas de ferramentas

### 5. Monitoramento e Logs

- Log detalhado de cada etapa do processo
- Métricas de performance por agente
- Tracking de custos de API

---

## Extensibilidade

### Adicionando Novos Agentes

1. Definir papel e responsabilidades específicas
2. Criar configuração YAML
3. Implementar classe do agente
4. Definir ferramentas necessárias
5. Configurar dependências e contexto

### Melhorias Futuras

- **Sentiment Analysis Agent**: Análise de tom e sentimento
- **Image Verification Agent**: Verificação de imagens
- **Social Media Agent**: Análise de propagação em redes sociais
- **Legal Compliance Agent**: Verificação de aspectos legais

---

## Troubleshooting

### Problemas Comuns

1. **Timeout de API**: Aumentar timeout, implementar retry
2. **Memória insuficiente**: Limpar contexto, otimizar prompts
3. **Rate limiting**: Implementar backoff exponencial
4. **Qualidade baixa**: Ajustar prompts, aumentar max_iter

### Métricas de Qualidade

- **Precisão**: % de classificações corretas
- **Recall**: % de fake news detectadas
- **F1-Score**: Harmonic mean de precisão e recall
- **Tempo de resposta**: Latência média do pipeline
"""
    },
    
    "tests/": {
        "__init__.py": "",
        "test_agents.py": """import pytest
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.crew import FakeNewsDetectorCrew
from tools.perplexity_tool import PerplexityTool
from tools.url_extractor import URLExtractorTool
from utils.helpers import validate_url, clean_text, calculate_confidence_score

class TestCrewConfiguration:
    \"\"\"Testes para configuração da crew\"\"\"
    
    def test_crew_initialization(self):
        \"\"\"Testa inicialização da crew\"\"\"
        crew = FakeNewsDetectorCrew()
        assert crew is not None
        assert hasattr(crew, 'agents_config')
        assert hasattr(crew, 'tasks_config')
    
    def test_agents_creation(self):
        \"\"\"Testa criação dos agentes\"\"\"
        crew = FakeNewsDetectorCrew()
        
        # Verificar se todos os agentes podem ser criados
        content_extractor = crew.content_extractor()
        fact_checker = crew.fact_checker()
        source_credibility = crew.source_credibility()
        final_decision = crew.final_decision()
        
        assert content_extractor is not None
        assert fact_checker is not None
        assert source_credibility is not None
        assert final_decision is not None

class TestTools:
    \"\"\"Testes para as ferramentas\"\"\"
    
    def test_perplexity_tool_initialization(self):
        \"\"\"Testa inicialização da ferramenta Perplexity\"\"\"
        # Mock da chave de API para teste
        os.environ['PERPLEXITY_API_KEY'] = 'test_key'
        
        tool = PerplexityTool()
        assert tool.name == "perplexity_search"
        assert tool.api_key == 'test_key'
    
    def test_url_extractor_tool(self):
        \"\"\"Testa ferramenta de extração de URL\"\"\"
        tool = URLExtractorTool()
        assert tool.name == "url_extractor"
        
        # Teste com URL inválida
        result = tool._run("invalid_url")
        assert "inválida" in result.lower()

class TestHelpers:
    \"\"\"Testes para funções auxiliares\"\"\"
    
    def test_validate_url(self):
        \"\"\"Testa validação de URLs\"\"\"
        assert validate_url("https://example.com") == True
        assert validate_url("http://example.com") == True
        assert validate_url("invalid") == False
        assert validate_url("") == False
    
    def test_clean_text(self):
        \"\"\"Testa limpeza de texto\"\"\"
        dirty_text = "  Texto   com    espaços   extras  \\n\\n  "
        clean = clean_text(dirty_text)
        assert clean == "Texto com espaços extras"
        
        assert clean_text("") == ""
        assert clean_text(None) == ""
    
    def test_confidence_score_calculation(self):
        \"\"\"Testa cálculo de score de confiança\"\"\"
        factors = {
            'source_credibility': 0.8,
            'fact_verification': 0.9,
            'content_quality': 0.7,
            'consistency': 0.6
        }
        
        score = calculate_confidence_score(factors)
        assert 0.0 <= score <= 1.0
        
        # Teste com fatores vazios
        assert calculate_confidence_score({}) == 0.0

class TestIntegration:
    \"\"\"Testes de integração\"\"\"
    
    @pytest.mark.integration
    def test_crew_execution_flow(self):
        \"\"\"Testa fluxo de execução da crew (mock)\"\"\"
        # Este teste requer configuração completa
        # Implementar quando ambiente de teste estiver pronto
        pass
    
    @pytest.mark.integration 
    def test_api_connectivity(self):
        \"\"\"Testa conectividade com APIs externas\"\"\"
        # Implementar testes de conectividade quando necessário
        pass

# Fixtures para testes
@pytest.fixture
def sample_crew():
    \"\"\"Fixture para crew de exemplo\"\"\"
    return FakeNewsDetectorCrew()

@pytest.fixture
def sample_url():
    \"\"\"Fixture para URL de exemplo\"\"\"
    return "https://example.com/news-article"

@pytest.fixture
def sample_text():
    \"\"\"Fixture para texto de exemplo\"\"\"
    return '''
    Este é um exemplo de artigo de notícia para teste.
    Contém informações que podem ser verificadas pelos agentes.
    O texto tem tamanho suficiente para análise.
    '''

if __name__ == "__main__":
    pytest.main([__file__])
"""
    }
}

def create_file_structure(base_path, structure):
    """Cria estrutura de arquivos e diretórios"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # É um diretório
            os.makedirs(path, exist_ok=True)
            create_file_structure(path, content)
        else:
            # É um arquivo
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

# Criar estrutura do projeto
base_dir = "fake-news-detector"
create_file_structure(".", project_structure)

print("✅ Estrutura do projeto criada com sucesso!")
print(f"📁 Diretório principal: {base_dir}")
print("\n📋 Próximos passos:")
print("1. cd fake-news-detector")
print("2. pip install -r requirements.txt")
print("3. cp .env.example .env")
print("4. Configure suas chaves de API no arquivo .env")
print("5. streamlit run main.py")