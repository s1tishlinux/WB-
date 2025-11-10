import weave
from typing import Dict, List, Any
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

@weave.op()
class ResponseQualityEvaluator:
    """Evaluate response quality using multiple metrics"""
    
    def __init__(self):
        self.client = openai.OpenAI()
        self.vectorizer = TfidfVectorizer()
    
    @weave.op()
    def evaluate_relevance(self, query: str, response: str) -> float:
        """Evaluate response relevance to query"""
        try:
            texts = [query, response]
            vectors = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @weave.op()
    def evaluate_coherence(self, response: str) -> float:
        """Evaluate response coherence using LLM"""
        messages = [
            {"role": "system", "content": "Rate the coherence of this response on a scale of 0-1. Return only the number."},
            {"role": "user", "content": response}
        ]
        
        try:
            result = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=10
            )
            score = float(result.choices[0].message.content.strip())
            return min(max(score, 0.0), 1.0)
        except:
            return 0.5
    
    @weave.op()
    def evaluate_completeness(self, query: str, response: str) -> float:
        """Evaluate if response completely addresses the query"""
        messages = [
            {"role": "system", "content": "Rate how completely this response addresses the query (0-1). Return only the number."},
            {"role": "user", "content": f"Query: {query}\nResponse: {response}"}
        ]
        
        try:
            result = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=10
            )
            score = float(result.choices[0].message.content.strip())
            return min(max(score, 0.0), 1.0)
        except:
            return 0.5
    
    @weave.op()
    def evaluate(self, query: str, response: str) -> Dict[str, float]:
        """Comprehensive response evaluation"""
        return {
            "relevance": self.evaluate_relevance(query, response),
            "coherence": self.evaluate_coherence(response),
            "completeness": self.evaluate_completeness(query, response),
            "length_score": min(len(response) / 500, 1.0)  # Normalize by expected length
        }

@weave.op()
class ToolUsageEvaluator:
    """Evaluate tool usage effectiveness"""
    
    @weave.op()
    def evaluate_tool_selection(self, query: str, selected_tools: List[str], available_tools: List[str]) -> float:
        """Evaluate if appropriate tools were selected"""
        if not selected_tools:
            return 0.0
        
        # Simple heuristic: check if tools are relevant to query keywords
        query_lower = query.lower()
        relevant_tools = []
        
        for tool in available_tools:
            if any(keyword in query_lower for keyword in self._get_tool_keywords(tool)):
                relevant_tools.append(tool)
        
        if not relevant_tools:
            return 0.5  # Neutral if no clear relevance
        
        # Calculate overlap
        selected_set = set(selected_tools)
        relevant_set = set(relevant_tools)
        
        if not selected_set:
            return 0.0
        
        precision = len(selected_set & relevant_set) / len(selected_set)
        recall = len(selected_set & relevant_set) / len(relevant_set) if relevant_set else 0
        
        return (precision + recall) / 2
    
    def _get_tool_keywords(self, tool_name: str) -> List[str]:
        """Get keywords associated with each tool"""
        keywords = {
            "web_search": ["search", "find", "look", "information", "web"],
            "calculator": ["calculate", "math", "compute", "number", "equation"],
            "weather": ["weather", "temperature", "climate", "forecast"],
            "time": ["time", "date", "when", "clock"]
        }
        return keywords.get(tool_name, [])
    
    @weave.op()
    def evaluate_tool_execution(self, tool_results: Dict[str, Any]) -> float:
        """Evaluate tool execution success rate"""
        if not tool_results:
            return 0.0
        
        successful_tools = sum(1 for result in tool_results.values() if "error" not in result)
        return successful_tools / len(tool_results)
    
    @weave.op()
    def evaluate(self, query: str, selected_tools: List[str], tool_results: Dict[str, Any], available_tools: List[str]) -> Dict[str, float]:
        """Comprehensive tool usage evaluation"""
        return {
            "tool_selection_score": self.evaluate_tool_selection(query, selected_tools, available_tools),
            "tool_execution_score": self.evaluate_tool_execution(tool_results),
            "tool_usage_efficiency": len(selected_tools) / max(len(available_tools), 1)
        }