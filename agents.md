# Documentação dos Agentes - Sistema de Detecção de Fake News

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
```yaml
content_extractor:
  role: "Especialista em Extração de Conteúdo"
  goal: "Extrair e limpar conteúdo de URLs ou processar texto fornecido"
  backstory: "Especialista em processamento de conteúdo web..."
  max_iter: 3
  allow_delegation: false
  memory: true
```

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
```yaml
fact_checker:
  role: "Verificador de Fatos Especializado"
  goal: "Verificar a veracidade das informações apresentadas"
  backstory: "Jornalista investigativo experiente..."
  max_iter: 5
  allow_delegation: true
  memory: true
```

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
```yaml
source_credibility:
  role: "Analista de Credibilidade de Fontes"
  goal: "Avaliar a credibilidade, reputação e viés de fontes"
  backstory: "Especialista em análise de mídia com PhD..."
  max_iter: 4
  allow_delegation: false
  memory: true
```

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
```yaml
final_decision:
  role: "Analista Senior de Decisão"
  goal: "Sintetizar todas as análises e tomar decisão final"
  backstory: "Analista senior com mais de 20 anos de experiência..."
  max_iter: 3
  allow_delegation: false
  memory: true
```

---

## Fluxo de Trabalho

### Processo Sequential

1. **Extração** → Content Extractor processa entrada
2. **Verificação** → Fact Checker analisa claims (usa contexto da extração)
3. **Credibilidade** → Source Credibility avalia fonte (usa contexto da extração)  
4. **Decisão** → Final Decision sintetiza resultados (usa contexto de todos)

### Configuração de Tarefas

```yaml
# Tarefa de Extração
extract_content:
  description: "Extrair e processar o conteúdo fornecido..."
  expected_output: "Relatório estruturado com título, conteúdo, metadados..."
  agent: content_extractor

# Tarefa de Verificação de Fatos
verify_facts:
  description: "Verificar a veracidade dos fatos apresentados..."
  expected_output: "Relatório de verificação com claims e evidências..."
  agent: fact_checker
  context: [extract_content]

# Tarefa de Avaliação de Credibilidade
assess_source:
  description: "Avaliar a credibilidade da fonte de informação..."
  expected_output: "Análise de credibilidade com score e fatores..."
  agent: source_credibility
  context: [extract_content]

# Tarefa de Decisão Final
make_decision:
  description: "Sintetizar todas as análises..."
  expected_output: "Decisão final estruturada com classificação..."
  agent: final_decision
  context: [extract_content, verify_facts, assess_source]
```

---

## Boas Práticas de Desenvolvimento

### 1. Configuração de Agentes

#### Elementos Essenciais:
- **Role**: Papel específico e claro
- **Goal**: Objetivo mensurável e acionável
- **Backstory**: Contexto que define expertise
- **Verbose**: true para debugging
- **Memory**: true para contexto entre execuções

#### Configurações Avançadas:
```yaml
agent_name:
  role: "Papel específico e claro"
  goal: "Objetivo mensurável"
  backstory: "Contexto e expertise detalhado"
  verbose: true
  memory: true
  max_iter: 3-5          # Limite de iterações
  max_execution_time: 300 # Timeout em segundos
  allow_delegation: true/false
  system_template: "Template personalizado se necessário"
```

### 2. Design de Tasks

#### Estrutura Recomendada:
```yaml
task_name:
  description: |
    Instruções detalhadas e específicas
    1. Passo específico
    2. Outro passo
    3. Critérios de qualidade
  expected_output: |
    Formato estruturado esperado:
    - Seção 1: Conteúdo X
    - Seção 2: Conteúdo Y
    - Métricas esperadas
  agent: agent_responsavel
  context: [dependencias]  # Tarefas das quais depende
```

### 3. Gerenciamento de Ferramentas

#### Implementação de Ferramentas Personalizadas:
```python
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class CustomToolInput(BaseModel):
    parameter: str = Field(description="Descrição do parâmetro")

class CustomTool(BaseTool):
    name: str = "tool_name"
    description: str = "Descrição clara da ferramenta"
    args_schema: Type[BaseModel] = CustomToolInput

    def _run(self, parameter: str) -> str:
        # Lógica da ferramenta
        return result
```

### 4. Tratamento de Erros e Resiliência

#### Estratégias Recomendadas:
- **Retry Logic**: Para chamadas de API
- **Timeout Management**: Evitar bloqueios
- **Graceful Degradation**: Fallbacks quando ferramentas falham
- **Input Validation**: Sanitizar entradas do usuário

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```

### 5. Monitoramento e Observabilidade

#### Métricas Importantes:
- **Latência por agente**: Tempo de execução
- **Taxa de sucesso**: % de execuções bem-sucedidas
- **Custos de API**: Tracking de gastos por chamada
- **Qualidade de output**: Métricas de satisfação

#### Logging Estruturado:
```python
import logging
import json
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_agent_execution(agent_name, task, result, duration):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "task": task,
        "duration_seconds": duration,
        "success": bool(result),
        "result_length": len(str(result)) if result else 0
    }
    logging.info(f"AGENT_EXECUTION: {json.dumps(log_data)}")
```

---

## Configurações de Qualidade e Performance

### Limites de Confiança
- **Alto**: ≥ 80% - Decisão confiável
- **Médio**: 60-79% - Cautela recomendada  
- **Baixo**: < 60% - Análise adicional necessária

### Otimização de Performance
```python
# Configurações recomendadas para produção
CREW_CONFIG = {
    "max_execution_time": 300,  # 5 minutos máximo
    "memory": True,             # Ativar memória
    "planning": True,           # Planejamento automático
    "planning_llm": "gpt-4o-mini",  # LLM mais rápido para planejamento
    "max_rpm": 20,              # Rate limiting
    "verbose": False            # Desativar em produção
}
```

### Níveis de Risco
```python
def calculate_risk_level(confidence: float, is_fake: bool) -> str:
    if is_fake:
        if confidence >= 0.8:
            return "Alto"      # Alta confiança que é fake
        elif confidence >= 0.6:
            return "Médio"     # Moderada confiança
        else:
            return "Baixo"     # Baixa confiança
    else:
        if confidence >= 0.8:
            return "Baixo"     # Alta confiança que é real
        elif confidence >= 0.6:
            return "Médio"     # Moderada confiança
        else:
            return "Alto"      # Baixa confiança em notícia "real"
```

---

## Extensibilidade e Melhorias Futuras

### Adicionando Novos Agentes

#### Processo Recomendado:
1. **Definir responsabilidade específica**
2. **Criar configuração YAML**
3. **Implementar classe do agente**
4. **Desenvolver ferramentas necessárias**
5. **Configurar dependências e contexto**
6. **Testar integração com pipeline existente**

#### Exemplo de Novo Agente:
```yaml
# config/agents.yaml
sentiment_analyzer:
  role: "Analista de Sentimento e Polarização"
  goal: "Analisar tom emocional e possível polarização do conteúdo"
  backstory: "Especialista em análise de sentimento com foco em detecção de conteúdo polarizador..."
  max_iter: 3
  allow_delegation: false
  memory: true
```

### Agentes Futuros Sugeridos:

#### 1. **Image Verification Agent**
- Verificação de imagens com reverse search
- Detecção de manipulação digital
- Análise de metadados de imagem

#### 2. **Social Media Propagation Agent**  
- Análise de padrões de compartilhamento
- Identificação de comportamento de bots
- Tracking de velocidade de propagação

#### 3. **Legal Compliance Agent**
- Verificação de aspectos legais
- Análise de compliance com regulamentações
- Identificação de conteúdo potencialmente problemático

#### 4. **Contextual Timeline Agent**
- Verificação de contexto temporal
- Análise de eventos relacionados
- Detecção de conteúdo desatualizado

---

## Troubleshooting e Resolução de Problemas

### Problemas Comuns

#### 1. **Timeout de API**
```python
# Solução: Aumentar timeout e implementar retry
import asyncio
from functools import wraps

def with_timeout(seconds):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                return f"Operação timeout após {seconds} segundos"
        return wrapper
    return decorator
```

#### 2. **Rate Limiting**
```python
# Solução: Backoff exponencial
import time
import random

def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0):
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
    time.sleep(delay)
    return delay
```

#### 3. **Qualidade de Output Baixa**
```python
# Solução: Validação de output e re-execução
def validate_agent_output(output: str, min_length: int = 100) -> bool:
    if not output or len(output) < min_length:
        return False

    # Verificar se contém informações esperadas
    required_sections = ["análise", "conclusão", "evidência"]
    return any(section.lower() in output.lower() for section in required_sections)
```

### Métricas de Qualidade

#### KPIs Recomendados:
```python
class QualityMetrics:
    def __init__(self):
        self.total_executions = 0
        self.successful_executions = 0
        self.avg_response_time = 0
        self.accuracy_scores = []

    def calculate_success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    def calculate_avg_accuracy(self) -> float:
        if not self.accuracy_scores:
            return 0.0
        return sum(self.accuracy_scores) / len(self.accuracy_scores)
```

---

## Segurança e Compliance

### Práticas de Segurança

#### 1. **Sanitização de Input**
```python
import re
from html import escape

def sanitize_user_input(text: str) -> str:
    # Remove scripts maliciosos
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Escapa HTML
    text = escape(text)

    # Limita tamanho
    if len(text) > 50000:
        text = text[:50000] + "..."

    return text
```

#### 2. **Gerenciamento de Chaves API**
```python
import os
from cryptography.fernet import Fernet

class SecureAPIKeyManager:
    def __init__(self):
        self.cipher = Fernet(os.environ.get('ENCRYPTION_KEY', Fernet.generate_key()))

    def encrypt_key(self, key: str) -> str:
        return self.cipher.encrypt(key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### Compliance com LGPD/GDPR

- **Data Minimization**: Coletar apenas dados necessários
- **Purpose Limitation**: Usar dados apenas para detecção de fake news  
- **Storage Limitation**: Não armazenar dados pessoais por tempo excessivo
- **Transparency**: Clara explicação sobre processamento de dados

---

## Conclusão

Este sistema de detecção de fake news fornece uma base sólida e extensível para análise automatizada de conteúdo. A arquitetura multi-agente permite especialização, melhoria contínua e adaptação a novos tipos de desinformação.

### Próximos Passos:
1. Implementar métricas de qualidade
2. Adicionar testes automatizados
3. Desenvolver interface de monitoramento
4. Expandir base de agentes especializados
5. Implementar feedback loop para melhoria contínua
