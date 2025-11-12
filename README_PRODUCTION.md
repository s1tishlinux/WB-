# Production Multi-Agent System with Weave + WandB

A production-ready multi-agent system built with **LangGraph**, **MCP**, **Weave**, and **WandB** for comprehensive AI workflow orchestration and monitoring.

## 🚀 Features

- **Multi-Agent Orchestration**: LangGraph-based workflow with specialized agents
- **MCP Integration**: Model Context Protocol for standardized tool interfaces
- **Comprehensive Monitoring**: Weave + WandB for complete observability
- **Production Ready**: Error handling, monitoring, and evaluation systems
- **Tool Integration**: Calculator, Weather, Time, Research tools via MCP
- **Real-time Evaluation**: Quality, performance, and tool usage metrics

## 📋 Requirements

- Python 3.8+
- OpenAI API key (for production mode)
- WandB account (free)
- Optional: Serper API key for web search

## 🛠️ Installation

### 1. Clone and Setup Environment

```bash
cd /Users/satishgundu/Desktop/WB/WB
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Required for production mode
OPENAI_API_KEY=your_openai_api_key_here

# WandB Configuration
WANDB_API_KEY=your_wandb_api_key_here
WANDB_PROJECT=multi-agent-system
WANDB_ENTITY=your_wandb_entity

# Optional
SERPER_API_KEY=your_serper_api_key_here
WEAVE_PROJECT_NAME=multi-agent-weave
```

### 3. Initialize WandB

```bash
wandb login
```

## 🎯 Quick Start

### Demo Mode (Mock APIs)

```bash
python main_demo.py
```

### Production Mode (Real APIs)

```bash
python main_demo.py --production
```

### Interactive Mode

```bash
python main_demo.py --interactive
```

## 🏗️ Architecture

### Core Components

1. **LangGraph Multi-Agent System** (`frameworks/langgraph_multi_agent.py`)
   - Coordinator Agent: Routes tasks to appropriate specialists
   - Research Agent: Information gathering and analysis
   - Analysis Agent: Data analysis and insights
   - Writing Agent: Content creation and documentation
   - MCP Executor: Tool execution via Model Context Protocol

2. **MCP Server** (`mcp_integration/mcp_server.py`)
   - Standardized tool interfaces
   - Calculator, Weather, Time, Research tools
   - Usage statistics and monitoring

3. **Production System** (`production_multi_agent.py`)
   - Complete integration of all components
   - Comprehensive Weave + WandB tracking
   - Error handling and recovery

4. **Evaluation System** (`evaluation/production_evaluators.py`)
   - Response quality evaluation
   - Tool usage assessment
   - Performance metrics

5. **Monitoring System** (`monitoring/production_monitors.py`)
   - Real-time performance monitoring
   - Quality trend analysis
   - Alert system

### Workflow

```
Query → Coordinator → Route Decision → Specialist Agents → Tool Execution → Synthesis → Response
  ↓                                                                                      ↑
Weave Tracing ←→ WandB Logging ←→ Evaluation ←→ Monitoring ←→ Alerts
```

## 📊 Monitoring & Observability

### Weave Integration

- **Tracing**: Complete execution flow capture
- **Function Tracking**: All agent operations traced
- **Performance Metrics**: Processing times and resource usage

### WandB Integration

- **Experiment Tracking**: All runs logged with metadata
- **Metrics Dashboard**: Real-time performance monitoring
- **Quality Trends**: Response quality over time
- **Alert System**: Threshold-based notifications

### Key Metrics Tracked

- Response time and latency
- Tool usage patterns
- Quality scores (relevance, coherence, completeness)
- Error rates and types
- Agent coordination efficiency
- Token usage and costs

## 🧪 Evaluation System

### Automatic Evaluation

```python
from evaluation.production_evaluators import ProductionAgentEvaluator

evaluator = ProductionAgentEvaluator()
result = evaluator.comprehensive_evaluation(
    query="Calculate 25 + 17",
    response="The result is 42",
    tools_used=["calculator"],
    processing_time=1.2
)
```

### Evaluation Metrics

- **Quality Score** (0-100): Response relevance, coherence, completeness
- **Tool Usage Score** (0-100): Appropriateness and efficiency
- **Performance Score** (0-100): Speed relative to complexity
- **Overall Grade** (A-F): Weighted combination

## 🔧 Usage Examples

### Basic Query Processing

```python
from production_multi_agent import create_production_multi_agent

# Initialize system
agent_system = create_production_multi_agent(use_mock=False)

# Process query
result = agent_system.process_query("What's 25 * 17 + 100?")

print(f"Response: {result['final_response']}")
print(f"Agents Used: {result['agents_used']}")
print(f"Processing Time: {result['processing_time']:.2f}s")
```

### Custom Tool Integration

```python
from mcp_integration.mcp_server import mcp_server

# Register custom tool
def custom_tool(input_data: str) -> dict:
    return {"result": f"Processed: {input_data}"}

mcp_server.register_tool(
    name="custom_tool",
    description="Custom processing tool",
    parameters={"type": "object", "properties": {"input": {"type": "string"}}},
    handler=custom_tool
)
```

## 📈 Performance Optimization

### Monitoring Thresholds

```python
# Configure performance thresholds
performance_monitor.thresholds = {
    "response_time": {"warning": 3.0, "error": 8.0},
    "error_rate": {"warning": 0.05, "error": 0.15},
    "quality_score": {"warning": 0.7, "error": 0.5}
}
```

### Quality Targets

- **Minimum Acceptable**: 60% quality score
- **Target Quality**: 80% quality score  
- **Excellent Quality**: 90% quality score

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check environment variables
   echo $OPENAI_API_KEY
   echo $WANDB_API_KEY
   ```

2. **Import Errors**
   ```bash
   # Verify installation
   pip install -r requirements.txt
   python -c "import weave, wandb, langchain"
   ```

3. **WandB Login Issues**
   ```bash
   wandb login --relogin
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
agent_system = create_production_multi_agent(use_mock=True)
```

## 📚 Documentation

- **Weave Documentation**: [https://weave-docs.wandb.ai/](https://weave-docs.wandb.ai/)
- **WandB Documentation**: [https://docs.wandb.ai/](https://docs.wandb.ai/)
- **LangGraph Documentation**: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all evaluations pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Next Steps

- [ ] Add more specialized agents
- [ ] Implement RL training with OpenPipe
- [ ] Add custom evaluation metrics
- [ ] Create Weave Reports
- [ ] Scale to production workloads
- [ ] Add A/B testing capabilities

---

**Built for the Weights & Biases Forward Deployed Engineer Technical Interview**

This system demonstrates:
✅ Multi-agent workflow with LangGraph  
✅ Comprehensive Weave instrumentation  
✅ WandB experiment tracking  
✅ Production-ready monitoring  
✅ Evaluation systems  
✅ MCP tool integration  
✅ Reproducible setup