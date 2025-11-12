# OpenPipe Integration Guide

## Overview

OpenPipe is now integrated into the W&B Weave Agent project for reinforcement learning and model fine-tuning. The integration allows you to:

1. **Collect training data** from agent interactions
2. **Log data to OpenPipe** for fine-tuning (when API key is provided)
3. **Export training data** locally as JSON
4. **Use in Streamlit** with a simple toggle

## Setup

### 1. Install OpenPipe

```bash
pip install openpipe-ai
```

### 2. Add API Key

Add your OpenPipe API key to `.env`:

```bash
OPENPIPE_API_KEY=your_openpipe_api_key_here
```

Get your API key from: https://app.openpipe.ai

## Usage

### Option 1: Streamlit UI (Recommended)

1. **Start Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Enable OpenPipe** in the sidebar:
   - Check "Enable Training Data Collection"
   - If API key is configured, you'll see " OpenPipe connected"

3. **Use the agent normally**:
   - All interactions are automatically collected as training data
   - Data is logged to OpenPipe in real-time (if API key is set)

4. **Export training data**:
   - Click "Export Training Data" in the sidebar
   - Download as JSON file

### Option 2: Standalone Demo

Run the RL training demo:

```bash
python rl_training_demo.py
```

This will:
- Process sample training scenarios
- Collect training data
- Log to OpenPipe (if API key is set)
- Export data to `training_data.json`

### Option 3: Programmatic Usage

```python
from rl_training import RLAgent
import weave

# Initialize Weave
weave.init("my-project")

# Create RL agent with OpenPipe enabled
agent = RLAgent(use_openpipe=True, use_mock=False)

# Process queries and collect training data
result = agent.process_with_feedback(
    query="What's the weather in New York?",
    expected_response="I'll check the weather for you."
)

# Export training data
training_data = agent.export_training_data()
```

## Features

### Training Data Collection

Each interaction captures:
- **Messages**: User query and agent response
- **Expected response**: Optional ground truth
- **Metadata**:
  - Processing time
  - Tools used
  - Reasoning quality score

### OpenPipe Logging

When enabled, data is automatically logged to OpenPipe with tags:
- `prompt_id`: "weave-agent-training"
- `tools_used`: Comma-separated list of tools
- `processing_time`: Execution time

### Data Export

Training data is exported in OpenPipe-compatible format:

```json
[
  {
    "messages": [
      {"role": "user", "content": "query"},
      {"role": "assistant", "content": "response"}
    ],
    "expected_response": "ground truth",
    "metadata": {
      "processing_time": 1.23,
      "tools_used": ["weather", "calculator"],
      "reasoning_quality": 0.85
    }
  }
]
```

## Fine-Tuning Workflow

1. **Collect Data**: Use Streamlit or demo to collect training interactions
2. **Export Data**: Download training data JSON
3. **Create Dataset**: Upload to OpenPipe dashboard (https://app.openpipe.ai)
4. **Fine-Tune**: Create fine-tuning job in OpenPipe
5. **Deploy**: Use fine-tuned model in your agent

## Configuration

### Mock Mode vs Real Mode

- **Mock Mode** (`use_mock=True`): Uses simulated responses, no OpenAI API calls
- **Real Mode** (`use_mock=False`): Uses actual OpenAI API, requires API key

### Streamlit Configuration

The Streamlit app automatically:
- Detects OpenPipe API key
- Shows connection status
- Switches between `WeaveAgent` and `RLAgent` based on toggle
- Collects training data when enabled

## Troubleshooting

### "OpenPipe logging failed"

This is normal if:
- OpenAI API quota is exceeded
- No OpenAI API key is set
- Network issues

Training data is still collected locally and can be exported.

### "No training data collected yet"

Make sure:
- OpenPipe toggle is enabled in Streamlit
- You've had at least one interaction with the agent

### Import Error

If you see `ModuleNotFoundError: No module named 'openpipe'`:

```bash
pip install openpipe-ai
```

## Files Modified

- `rl_training/openpipe_integration.py` - Core OpenPipe integration
- `rl_training/__init__.py` - Exports RLAgent
- `rl_training_demo.py` - Standalone demo
- `streamlit_app.py` - Streamlit UI with OpenPipe toggle
- `requirements.txt` - Added openpipe-ai dependency

## Next Steps

1. Collect 100+ high-quality training examples
2. Upload to OpenPipe dashboard
3. Create fine-tuning job
4. Evaluate fine-tuned model performance
5. Deploy improved model

## Resources

- OpenPipe Documentation: https://docs.openpipe.ai
- OpenPipe Dashboard: https://app.openpipe.ai
- W&B Weave: https://wandb.ai/site/weave
