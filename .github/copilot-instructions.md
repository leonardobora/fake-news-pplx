# Fake News Detector with CrewAI and Perplexity API

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

This repository contains a fake news detection system that uses multi-agent AI architecture with CrewAI, Streamlit web interface, and Perplexity API for fact verification. The project is currently in a **generator/scaffolding phase** - the main files are scripts that create the actual project structure rather than the final implementation.

## Working Effectively

### Repository Structure (Current State)
The repository contains:
- `setup-guide.md` - Comprehensive setup and development guide
- `agents.md` - Detailed agent configuration documentation
- `script.py`, `script_1.py`, `script_2.py` - Project generation scripts
- `chart_script.py` - Chart generation utilities
- `system_architecture.png` - System architecture diagram

### Project Generation and Setup
Run these commands to create the actual project:
- `python script.py` -- KNOWN ISSUE: Contains syntax errors on line 668. Do not use without fixing first.
- Alternative: Use the setup instructions from `setup-guide.md` to manually create project structure
- Create virtual environment: `python -m venv venv`
- Activate environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- **CRITICAL**: Dependencies installation may fail due to version conflicts between `crewai==0.63.6` and `langchain==0.1.0`. Use compatible versions: `langchain>=0.2.16,<0.3.0`
- **NETWORK ISSUES**: `pip install` commands frequently timeout. Allow 10-15 minutes and retry if needed. NEVER CANCEL during installation.

### Core Dependencies (When Generated Project Exists)
```bash
# Essential packages - install these first
pip install streamlit python-dotenv requests beautifulsoup4

# Full stack (if network allows)
pip install streamlit crewai crewai-tools requests beautifulsoup4 python-dotenv newspaper3k langchain openai pydantic PyYAML
```

### Running the Application
- Copy environment template: `cp .env.example .env`
- Configure API keys in `.env` file:
  - `PERPLEXITY_API_KEY=pplx-your-key-here`
  - `OPENAI_API_KEY=sk-your-key-here`
- Start application: `streamlit run main.py`
- **TIMING**: Initial startup takes 30-60 seconds. NEVER CANCEL.
- Application opens at: `http://localhost:8501`

### Testing
- Run basic tests: `python -m unittest tests.test_basic -v` -- takes 0.1 seconds
- Run full tests: `python -m pytest tests/` -- takes 2-3 minutes. NEVER CANCEL. Set timeout to 300+ seconds.
- Test with coverage: `python -m pytest tests/ --cov=src` -- takes 3-5 minutes. NEVER CANCEL. Set timeout to 400+ seconds.
- Specific test: `python -m pytest tests/test_agents.py::TestCrewConfiguration::test_crew_initialization`

### Code Quality and Formatting
- Format code: `black src/ tests/` -- takes 10-30 seconds
- Check style: `flake8 src/ tests/` -- takes 15-45 seconds
- Type checking: `mypy src/` -- takes 30-90 seconds
- Basic syntax check: `python -m py_compile filename.py` -- takes <1 second
- **ALWAYS** run `black src/ tests/` and `flake8 src/ tests/` before committing

## Validation

### Manual Testing Requirements
After making any changes to the application:
1. **ALWAYS** test the complete user workflow:
   - Start the application with `streamlit run main.py`
   - Test URL input: Enter a news URL and verify extraction works
   - Test text input: Paste news text and verify analysis runs
   - Verify results display correctly with confidence scores
   - Check error handling with invalid inputs
2. **REQUIRED**: Take screenshots of the UI to verify visual changes work correctly
3. Test both successful and error scenarios

### API Connectivity Testing
```bash
# Test Perplexity API connectivity
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     "https://api.perplexity.ai/chat/completions"

# Verify environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Perplexity:', os.getenv('PERPLEXITY_API_KEY')[:10] + '...')
print('OpenAI:', os.getenv('OPENAI_API_KEY')[:10] + '...')
"
```

### Known Issues and Workarounds
- **Dependency conflicts**: CrewAI requires `langchain>=0.2.16` but some guides show `langchain==0.1.0`
- **Network timeouts**: pip installations frequently timeout. Retry 2-3 times with different timeout values
- **Script syntax errors**: `script.py` has confirmed syntax error on line 668 - missing comma in string literal before `"url_extractor.py"`
- **Memory issues**: Large dependency installations may require 2+ GB RAM
- **Virtual environment**: Always exclude `venv/` directories from git commits using `.gitignore`

## Common Tasks

### Project Structure (Generated)
```
fake-news-detector/
├── main.py                     # Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── config/                    # Configuration files
│   ├── agents.yaml           # Agent definitions
│   └── tasks.yaml            # Task configurations
├── src/                      # Source code
│   ├── agents/               # Agent implementations
│   │   └── crew.py          # Main crew definition
│   ├── tools/               # Custom tools
│   │   ├── perplexity_tool.py
│   │   └── url_extractor.py
│   └── utils/               # Utility functions
│       └── helpers.py
└── tests/                   # Test suite
    └── test_agents.py
```

### Key Files to Monitor
- Always check `main.py` after making changes to ensure Streamlit integration works
- Verify `config/agents.yaml` when modifying agent behavior
- Update `requirements.txt` when adding new dependencies
- Check `.env.example` when adding new environment variables

### Performance Monitoring
- **Streamlit cache**: Clear with `streamlit cache clear` if experiencing issues
- **Log locations**:
  - `~/.streamlit/logs/streamlit.log` - Streamlit application logs
  - `crew_execution.log` - Agent execution logs (when implemented)
  - `api_calls.log` - API call history (when implemented)

### Debugging Commands
```bash
# Run with debug output
export DEBUG=True
streamlit run main.py

# Monitor logs in real-time
tail -f ~/.streamlit/logs/streamlit.log

# Profile performance (if needed)
pip install py-spy
py-spy record -o profile.svg -- streamlit run main.py
```

## Agent System Architecture

### Multi-Agent Workflow
1. **Content Extractor Agent**: Extracts and cleans content from URLs or text
2. **Fact Checker Agent**: Verifies claims using Perplexity API
3. **Source Credibility Agent**: Evaluates source reliability
4. **Final Decision Agent**: Combines all analyses for final verdict

### Agent Configuration
- Max iterations: 3-5 per agent
- Execution timeout: 300 seconds (5 minutes) per agent
- Memory enabled for context retention
- Verbose mode for debugging

### Key Performance Metrics
- **Latency per agent**: 30-120 seconds typical
- **Total analysis time**: 2-5 minutes for complete workflow
- **API costs**: Track Perplexity and OpenAI usage
- **Accuracy rate**: Monitor false positive/negative rates

## Troubleshooting

### Installation Issues
```bash
# Dependency conflicts
pip install --upgrade pip setuptools wheel
pip install --force-reinstall -r requirements.txt

# newspaper3k issues (Windows)
pip install --upgrade certifi
```

### Runtime Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Reset virtual environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Development Environment
- **Recommended Python**: 3.11+ (tested with 3.12)
- **Memory requirement**: 2+ GB for full dependency installation
- **Network**: Stable connection required for API calls and pip installations

## Important Notes

- **NEVER CANCEL** long-running operations (installations, tests, builds)
- **ALWAYS** test manual workflows after code changes
- **REQUIRED**: Take UI screenshots for any interface changes
- **TIMING**: Allow 10+ minutes for complete setup from scratch
- **FALLBACK**: If pip fails repeatedly, use system Python packages where available

Fixes #3.