# W&B Weave Agent Project

A production-ready AI agent system with Weave integration for tracing, evaluation, and monitoring. Features real tool calling, multi-agent coordination, and OpenPipe RL training.

## Features

- **AI Agent**: Custom agent with real tool calling (web search, calculator, weather, time)
- **Weave Tracing**: Full execution flow capture (reasoning, tool calls, outputs)
- **Real Web Search**: Serper API integration for live Google search results
- **Multi-Agent Workflow**: Coordinated specialist agents (research, analysis, writing, technical)
- **OpenPipe RL Training**: Collect training data and fine-tune models
- **Evaluations**: Custom and native Weave scorers for agent performance
- **Monitoring**: Quality, error rate, and performance tracking
- **Streamlit UI**: Interactive chat interface with real-time metrics

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   
   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   # Required
   WANDB_API_KEY=your_wandb_api_key
   OPENAI_API_KEY=your_openai_api_key
   
   # Optional - for real web search
   SERPER_API_KEY=your_serper_api_key  # Get from https://serper.dev
   
   # Optional - for RL training
   OPENPIPE_API_KEY=your_openpipe_api_key  # Get from https://openpipe.ai
   ```

3. **Run the Agent**
   ```bash
   python main.py
   ```

4. **Run Evaluations**
   ```bash
   python evaluate_agent.py
   ```

5. **Run RL Training** (Optional)
   ```bash
   python rl_training_demo.py
   ```

6. **Launch Streamlit UI** (Recommended)
   ```bash
   streamlit run streamlit_app.py
   ```
   - Toggle between Single Agent and Multi-Agent modes
   - Enable OpenPipe training data collection
   - View real-time metrics and tool usage

7. **View Results**
   - Open your W&B dashboard at https://wandb.ai
   - Navigate to the Weave workspace
   - Explore traces, evaluations, and monitors

## Project Structure

```
W&B_Project/
├── README.md
├── requirements.txt
├── main.py                 # Main agent runner
├── agent/
│   ├── __init__.py
│   ├── core.py            # Core agent implementation
│   ├── memory.py          # Memory management
│   └── tools.py           # Tool definitions
├── evaluation/
│   ├── __init__.py
│   ├── evaluators.py      # Custom evaluators
│   └── scorers.py         # Weave scorers
├── monitoring/
│   ├── __init__.py
│   └── monitors.py        # Custom monitors
├── multi_agent/
│   ├── __init__.py
│   └── workflow.py        # Multi-agent coordination
├── rl_training/
│   ├── __init__.py
│   └── openpipe_integration.py # OpenPipe RL training
├── evaluate_agent.py      # Evaluation runner
└── rl_training_demo.py    # RL training demo
```

## Technical Implementation

### Agent Architecture
- **Memory Management**: Persistent conversation history with semantic search
- **Tool Calling**: Automatic tool detection and execution
  - **Web Search**: Real Google search via Serper API
  - **Calculator**: Safe mathematical expression evaluation
  - **Weather**: Simulated weather data (demo)
  - **Time**: Current timestamp and formatted time
- **Reasoning**: Chain-of-thought with GPT-3.5/GPT-4

### Weave Integration
- **Tracing**: Automatic capture of all agent operations
- **Evaluations**: Performance metrics and quality assessments
- **Monitoring**: Real-time tracking of key signals
- **All interactions logged** to W&B for analysis

### Multi-Agent Workflow
- **Coordinator Agent**: Analyzes tasks and routes to specialists
- **Specialist Agents**: 
  - Research: Information gathering with web search
  - Analysis: Data analysis and insights
  - Writing: Content creation and documentation
  - Technical: Implementation and code solutions
- **Tool Access**: All specialists can use tools (search, calculator, etc.)
- **Communication**: Sequential processing with context passing

## Evaluation Metrics

- **Response Quality**: Semantic similarity and relevance
- **Tool Usage**: Accuracy and efficiency of tool selection
- **Error Rate**: Failure detection and recovery
- **Performance**: Response time and resource usage

## Monitoring Dashboards

Access comprehensive monitoring through W&B:
- Agent performance trends
- Error rate analysis
- Tool usage patterns
- Quality score distributions

## OpenPipe RL Integration

- **Training Data Collection**: Automatic collection of agent interactions
- **Model Fine-tuning**: OpenPipe integration for RL-based improvements
- **Performance Tracking**: Weave-integrated training metrics
- **Continuous Learning**: Iterative agent improvement pipeline
- **Export Training Data**: Download collected interactions as JSON
- **Streamlit Toggle**: Enable/disable training collection in UI

## API Keys & Setup

### Required APIs
1. **W&B (Weights & Biases)**: Free account at https://wandb.ai
2. **OpenAI**: API key from https://platform.openai.com

### Optional APIs
3. **Serper** (Web Search): 
   - Sign up at https://serper.dev
   - Free tier: 2,500 searches/month
   - Without this: Uses simulated search results

4. **OpenPipe** (RL Training):
   - Sign up at https://openpipe.ai
   - Without this: Training data collected locally only

## Tool Calling

### How It Works
1. **Query Analysis**: Agent detects keywords/patterns
2. **Tool Selection**: Automatically selects relevant tools
3. **Tool Execution**: Calls APIs and gets real data
4. **Response Generation**: GPT synthesizes tool results

### Example Queries
- "55+55" → Uses calculator → Returns 110
- "search for AI news" → Uses Serper → Returns real search results
- "what time is it" → Uses time tool → Returns current timestamp
- "weather in Tokyo" → Uses weather tool → Returns simulated data

### Multi-Agent Example
- "search for percentage of IT professionals in SF"
  - Research specialist: Uses web_search tool
  - Analysis specialist: Analyzes search results
  - Coordinator: Synthesizes final answer with real data

## Key Features Implemented

 **Real tool calling** with Serper API web search  
 **Multi-agent workflow** with 4 specialist agents  
 **OpenPipe RL integration** with training data collection  
 **Streamlit UI** with single/multi-agent modes  
 **Weave tracing** for all interactions  
 **Custom evaluations** with quality metrics  
 **Comprehensive monitoring** dashboard  
 **Auto-detection** of mock vs real mode based on API keys  
 **Tool visibility** in both single and multi-agent modes  
 **Export capabilities** for training data and statistics

## Troubleshooting

### Agent only gives reasoning, no tools
- Check that query contains tool keywords ("search", "calculate", "+", "weather", "time")
- Verify OPENAI_API_KEY is set (mock mode doesn't use tools effectively)

### Web search returns generic results
- Add SERPER_API_KEY to `.env` for real search
- Without it, uses simulated placeholder results

### Multi-agent not showing tools
- Tools are being used! Check the updated metadata
- Look for `tools_used` and `tool_results` in Details panel

### OpenPipe errors
- OpenPipe is optional - agent works without it
- Training data is collected locally even without API key

## Documentation

See additional documentation:
- `OPENPIPE_INTEGRATION.md` - OpenPipe setup and usage
- `TOOL_CALLING_FIX.md` - Tool calling implementation details
- `test_agent.py` - Test script for single agent
- `test_multiagent_tools.py` - Test script for multi-agent with tools