# 🔍 Fake News Detector - Setup e Execução

## Estrutura do Projeto Completa

```
fake-news-detector/
├── main.py                     # 🚀 Aplicação Streamlit principal
├── README.md                   # 📚 Documentação do projeto
├── requirements.txt            # 📦 Dependências Python
├── .env.example               # 🔑 Template de variáveis de ambiente
├── agents.md                  # 📖 Documentação completa dos agentes
│
├── config/                    # ⚙️ Configurações YAML
│   ├── agents.yaml           # 🤖 Definições dos agentes CrewAI
│   └── tasks.yaml            # 📋 Definições das tarefas
│
├── src/                      # 💻 Código fonte principal
│   ├── __init__.py
│   ├── agents/               # 🤖 Implementação dos agentes
│   │   ├── __init__.py
│   │   └── crew.py          # Definição da crew principal
│   ├── tools/               # 🛠️ Ferramentas personalizadas
│   │   ├── __init__.py
│   │   ├── perplexity_tool.py    # 🌐 Integração Perplexity API
│   │   └── url_extractor.py      # 🔗 Extração de conteúdo web
│   └── utils/               # 🔧 Utilitários e helpers
│       ├── __init__.py
│       └── helpers.py       # Funções auxiliares
│
├── docs/                    # 📚 Documentação adicional
│   └── agents.md           # Documentação detalhada dos agentes
│
└── tests/                  # 🧪 Testes automatizados
    ├── __init__.py
    └── test_agents.py      # Testes dos agentes e ferramentas
```

## 🚀 Guia de Instalação e Execução

### 1️⃣ Clonagem e Setup Inicial
```bash
# Criar diretório do projeto
mkdir fake-news-detector
cd fake-news-detector

# Inicializar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2️⃣ Instalação de Dependências
```bash
# Instalar dependências principais
pip install streamlit==1.29.0
pip install crewai==0.63.6
pip install crewai-tools==0.12.1
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install python-dotenv==1.0.0
pip install newspaper3k==0.2.8
pip install langchain==0.1.0
pip install openai==1.12.0
pip install pydantic==2.5.0
pip install PyYAML==6.0.1

# Ou usando requirements.txt
pip install -r requirements.txt
```

### 3️⃣ Configuração das Chaves de API
```bash
# Copiar template de configuração
cp .env.example .env

# Editar arquivo .env com suas chaves
nano .env  # ou use seu editor preferido
```

**Conteúdo do arquivo .env:**
```env
# Chaves de API obrigatórias
PERPLEXITY_API_KEY=pplx-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# Configurações opcionais
DEBUG=True
MAX_RETRIES=3
TIMEOUT=30
```

### 4️⃣ Execução da Aplicação
```bash
# Executar aplicação Streamlit
streamlit run main.py

# A aplicação abrirá em: http://localhost:8501
```

## 🔧 Comandos de Desenvolvimento

### Testes
```bash
# Executar testes unitários
python -m pytest tests/

# Executar com cobertura
pip install pytest-cov
python -m pytest tests/ --cov=src

# Teste específico
python -m pytest tests/test_agents.py::TestCrewConfiguration::test_crew_initialization
```

### Linting e Formatação
```bash
# Instalar ferramentas de qualidade
pip install black flake8 mypy

# Formatação de código
black src/ tests/

# Verificação de estilo
flake8 src/ tests/

# Verificação de tipos
mypy src/
```

### Debug e Monitoramento
```bash
# Executar com debug verbose
export DEBUG=True
streamlit run main.py

# Monitorar logs em tempo real
tail -f ~/.streamlit/logs/streamlit.log
```

## 🛠️ Configuração do VSCode

### Extensions Recomendadas
1. **Python** - Microsoft
2. **Pylance** - Microsoft  
3. **YAML** - Red Hat
4. **Streamlit Snippets** - arnaud-zg
5. **GitLens** - GitKraken
6. **Python Docstring Generator** - Nils Werner

### Configuração launch.json
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Streamlit Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/Scripts/streamlit",
            "args": ["run", "main.py"],
            "console": "integratedTerminal",
            "env": {
                "DEBUG": "True"
            }
        },
        {
            "name": "Test Agents",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/test_agents.py", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

### Configuração settings.json
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "yaml.validate": true,
    "yaml.hover": true,
    "yaml.completion": true
}
```

## 🐛 Troubleshooting Comum

### Problemas de Instalação
```bash
# Problema: Conflito de dependências
pip install --upgrade pip setuptools wheel
pip install --force-reinstall -r requirements.txt

# Problema: newspaper3k no Windows
pip install --upgrade certifi
```

### Problemas de API
```bash
# Verificar conectividade com Perplexity
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     "https://api.perplexity.ai/chat/completions"

# Testar chaves no Python
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Perplexity:', os.getenv('PERPLEXITY_API_KEY')[:10] + '...')
print('OpenAI:', os.getenv('OPENAI_API_KEY')[:10] + '...')
"
```

### Performance Issues
```bash
# Limpar cache do Streamlit
streamlit cache clear

# Executar com profiling
pip install py-spy
py-spy record -o profile.svg -- streamlit run main.py
```

## 📊 Monitoramento e Métricas

### Logs Importantes
- `~/.streamlit/logs/streamlit.log` - Logs do Streamlit
- `crew_execution.log` - Logs dos agentes CrewAI
- `api_calls.log` - Histórico de chamadas de API

### Métricas para Acompanhar
- **Latência por agente** - Tempo de execução
- **Taxa de sucesso** - % de análises concluídas
- **Acurácia** - % de classificações corretas  
- **Custo por análise** - Gastos com APIs

## 🚀 Deploy e Produção

### Streamlit Cloud
```bash
# 1. Fazer push para GitHub
git add .
git commit -m "Initial fake news detector setup"
git push origin main

# 2. Conectar no Streamlit Cloud
# 3. Adicionar secrets (chaves de API)
# 4. Deploy automático
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build e run
docker build -t fake-news-detector .
docker run -p 8501:8501 --env-file .env fake-news-detector
```

## 🎯 Próximos Passos

1. **✅ Setup Básico** - Configurar ambiente e dependências
2. **🔧 Implementação** - Desenvolver agentes e ferramentas  
3. **🧪 Testes** - Criar suite de testes abrangente
4. **📊 Métricas** - Implementar monitoramento e analytics
5. **🚀 Deploy** - Colocar em produção
6. **🔄 Iteração** - Melhoramento contínuo baseado em feedback

---

**💡 Dica:** Comece testando com alguns exemplos simples antes de implementar casos complexos. O sistema é modular e pode ser expandido gradualmente.
