import weave
from typing import Dict, Any, List
import openai

class WeaveScorers:
    """Collection of Weave-native scorers"""
    
    @staticmethod
    @weave.op()
    def llm_judge_scorer(query: str, response: str) -> Dict[str, Any]:
        """LLM-based scoring using GPT as judge"""
        client = openai.OpenAI()
        
        messages = [
            {"role": "system", "content": """You are an expert evaluator. Rate the response on these criteria (0-10 scale):
            1. Accuracy: Is the information correct?
            2. Helpfulness: Does it help the user?
            3. Clarity: Is it clear and well-structured?
            4. Completeness: Does it fully address the query?
            
            Return a JSON object with scores and brief explanations."""},
            {"role": "user", "content": f"Query: {query}\n\nResponse: {response}"}
        ]
        
        try:
            result = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300
            )
            
            import json
            scores = json.loads(result.choices[0].message.content)
            return scores
        except Exception as e:
            return {
                "accuracy": 5,
                "helpfulness": 5,
                "clarity": 5,
                "completeness": 5,
                "error": str(e)
            }
    
    @staticmethod
    @weave.op()
    def semantic_similarity_scorer(query: str, response: str, expected_response: str = None) -> float:
        """Semantic similarity scoring"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            if expected_response:
                # Compare response to expected response
                texts = [response, expected_response]
            else:
                # Compare response to query
                texts = [query, response]
            
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @staticmethod
    @weave.op()
    def response_length_scorer(response: str, target_length: int = 200) -> float:
        """Score based on response length appropriateness"""
        actual_length = len(response)
        
        if actual_length == 0:
            return 0.0
        
        # Optimal range is 50% to 150% of target length
        min_length = target_length * 0.5
        max_length = target_length * 1.5
        
        if min_length <= actual_length <= max_length:
            return 1.0
        elif actual_length < min_length:
            return actual_length / min_length
        else:
            return max_length / actual_length
    
    @staticmethod
    @weave.op()
    def error_rate_scorer(agent_results: List[Dict[str, Any]]) -> float:
        """Calculate error rate across multiple agent interactions"""
        if not agent_results:
            return 0.0
        
        error_count = 0
        for result in agent_results:
            # Check for errors in tool results
            if "tool_results" in result:
                for tool_result in result["tool_results"].values():
                    if isinstance(tool_result, dict) and "error" in tool_result:
                        error_count += 1
            
            # Check for processing errors
            if "error" in result:
                error_count += 1
        
        return 1.0 - (error_count / len(agent_results))
    
    @staticmethod
    @weave.op()
    def performance_scorer(processing_times: List[float], target_time: float = 5.0) -> float:
        """Score based on processing performance"""
        if not processing_times:
            return 0.0
        
        avg_time = sum(processing_times) / len(processing_times)
        
        if avg_time <= target_time:
            return 1.0
        else:
            return target_time / avg_time
    
    @staticmethod
    @weave.op()
    def comprehensive_scorer(query: str, agent_result: Dict[str, Any]) -> Dict[str, float]:
        """Comprehensive scoring combining multiple metrics"""
        scores = {}
        
        # Response quality
        if "response" in agent_result:
            scores["llm_judge"] = WeaveScorers.llm_judge_scorer(query, agent_result["response"])
            scores["semantic_similarity"] = WeaveScorers.semantic_similarity_scorer(query, agent_result["response"])
            scores["response_length"] = WeaveScorers.response_length_scorer(agent_result["response"])
        
        # Performance
        if "processing_time" in agent_result:
            scores["performance"] = WeaveScorers.performance_scorer([agent_result["processing_time"]])
        
        # Tool usage
        if "tool_results" in agent_result:
            tool_errors = sum(1 for result in agent_result["tool_results"].values() 
                            if isinstance(result, dict) and "error" in result)
            total_tools = len(agent_result["tool_results"])
            scores["tool_success_rate"] = (total_tools - tool_errors) / max(total_tools, 1)
        
        return scores