import weave
import os
from typing import Dict, List, Any, Optional
from agent.core import WeaveAgent
import json

try:
    import openpipe
    from openpipe import OpenAI
    OPENPIPE_AVAILABLE = True
except ImportError:
    OPENPIPE_AVAILABLE = False
    OpenAI = None

@weave.op()
class RLAgent(WeaveAgent):
    """Agent with OpenPipe training data collection"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", use_openpipe: bool = False, use_mock: bool = True):
        super().__init__(model, use_mock=use_mock)
        self.use_openpipe = use_openpipe and OPENPIPE_AVAILABLE
        self.training_data = []
        
        if self.use_openpipe:
            api_key = os.getenv("OPENPIPE_API_KEY")
            if api_key:
                openpipe.api_key = api_key
                self.openpipe_client = OpenAI()
            else:
                self.openpipe_client = None
        else:
            self.openpipe_client = None
        
    @weave.op()
    def process_with_feedback(self, query: str, expected_response: Optional[str] = None) -> Dict[str, Any]:
        """Process query and collect training data"""
        result = self.process(query)
        
        # Collect training data
        training_entry = {
            "messages": [
                {"role": "user", "content": query},
                {"role": "assistant", "content": result["response"]}
            ],
            "expected_response": expected_response,
            "metadata": {
                "processing_time": result["processing_time"],
                "tools_used": result["selected_tools"],
                "reasoning_quality": self._assess_reasoning_quality(result["reasoning"])
            }
        }
        
        self.training_data.append(training_entry)
        
        # Log to OpenPipe if enabled
        if self.use_openpipe and self.openpipe_client:
            try:
                self.openpipe_client.chat.completions.create(
                    model=self.model,
                    messages=training_entry["messages"],
                    openpipe={
                        "tags": {
                            "prompt_id": "weave-agent-training",
                            "tools_used": ",".join(result["selected_tools"]),
                            "processing_time": str(result["processing_time"])
                        }
                    }
                )
            except Exception as e:
                print(f"OpenPipe logging failed: {e}")
        
        return result
    
    def _assess_reasoning_quality(self, reasoning: Dict[str, Any]) -> float:
        """Simple reasoning quality assessment"""
        reasoning_text = reasoning.get("reasoning", "")
        return min(len(reasoning_text) / 500, 1.0)
    
    def export_training_data(self) -> List[Dict[str, Any]]:
        """Export collected training data"""
        return self.training_data