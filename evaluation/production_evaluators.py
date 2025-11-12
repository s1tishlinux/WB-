"""
Production Evaluators with Weave + WandB Integration
Comprehensive evaluation system for multi-agent workflows
"""

import weave
import wandb
from typing import Dict, List, Any, Optional
import json
import time
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    """Evaluation result structure"""
    score: float
    max_score: float
    details: Dict[str, Any]
    timestamp: float

@weave.op()
class ProductionAgentEvaluator:
    """Production-grade agent evaluation with Weave + WandB integration"""
    
    def __init__(self, project_name: str = "agent-evaluation"):
        self.project_name = project_name
        self.evaluation_history = []
        self.metrics = {
            "accuracy": [],
            "response_time": [],
            "tool_usage": [],
            "coherence": []
        }
    
    @weave.op()
    def evaluate_response_quality(self, query: str, response: str, expected_type: str = None) -> EvaluationResult:
        """Evaluate response quality with comprehensive metrics"""
        score = 0.0
        max_score = 100.0
        details = {}
        
        # Length appropriateness (20 points)
        response_length = len(response.split())
        if 10 <= response_length <= 200:
            length_score = 20.0
        elif response_length < 10:
            length_score = max(0, 20 - (10 - response_length) * 2)
        else:
            length_score = max(0, 20 - (response_length - 200) * 0.1)
        
        score += length_score
        details["length_score"] = length_score
        details["response_length"] = response_length
        
        # Relevance to query (30 points)
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words.intersection(response_words))
        relevance_score = min(30.0, (overlap / max(len(query_words), 1)) * 30)
        
        score += relevance_score
        details["relevance_score"] = relevance_score
        details["word_overlap"] = overlap
        
        # Structure and coherence (25 points)
        sentences = response.split('.')
        coherence_score = min(25.0, len(sentences) * 5) if len(sentences) <= 5 else 25.0
        
        score += coherence_score
        details["coherence_score"] = coherence_score
        details["sentence_count"] = len(sentences)
        
        # Completeness (25 points)
        completeness_indicators = ["result", "conclusion", "summary", "answer"]
        completeness_score = 0
        for indicator in completeness_indicators:
            if indicator in response.lower():
                completeness_score += 6.25
        
        score += completeness_score
        details["completeness_score"] = completeness_score
        
        # Log to WandB
        wandb.log({
            "evaluation/quality_score": score,
            "evaluation/length_score": length_score,
            "evaluation/relevance_score": relevance_score,
            "evaluation/coherence_score": coherence_score,
            "evaluation/completeness_score": completeness_score,
            "evaluation/response_length": response_length
        })
        
        result = EvaluationResult(
            score=score,
            max_score=max_score,
            details=details,
            timestamp=time.time()
        )
        
        self.evaluation_history.append(result)
        self.metrics["accuracy"].append(score / max_score)
        
        return result
    
    @weave.op()
    def evaluate_tool_usage(self, tools_used: List[str], query: str) -> EvaluationResult:
        """Evaluate appropriateness of tool usage"""
        score = 0.0
        max_score = 100.0
        details = {}
        
        query_lower = query.lower()
        
        # Expected tools based on query
        expected_tools = []
        if any(op in query_lower for op in ["+", "-", "*", "/", "calculate"]):
            expected_tools.append("calculator")
        if "weather" in query_lower:
            expected_tools.append("weather")
        if "time" in query_lower:
            expected_tools.append("time")
        if any(word in query_lower for word in ["research", "find", "search"]):
            expected_tools.append("research")
        
        # Tool appropriateness (60 points)
        if expected_tools:
            correct_tools = set(tools_used).intersection(set(expected_tools))
            tool_score = (len(correct_tools) / len(expected_tools)) * 60
        else:
            tool_score = 60 if not tools_used else 30  # No tools needed
        
        score += tool_score
        details["tool_appropriateness"] = tool_score
        details["expected_tools"] = expected_tools
        details["used_tools"] = tools_used
        
        # Tool efficiency (40 points)
        efficiency_score = max(0, 40 - (len(tools_used) - len(expected_tools)) * 10)
        score += efficiency_score
        details["efficiency_score"] = efficiency_score
        
        # Log to WandB
        wandb.log({
            "evaluation/tool_score": score,
            "evaluation/tool_appropriateness": tool_score,
            "evaluation/tool_efficiency": efficiency_score,
            "evaluation/tools_used_count": len(tools_used),
            "evaluation/expected_tools_count": len(expected_tools)
        })
        
        result = EvaluationResult(
            score=score,
            max_score=max_score,
            details=details,
            timestamp=time.time()
        )
        
        self.metrics["tool_usage"].append(score / max_score)
        return result
    
    @weave.op()
    def evaluate_performance(self, processing_time: float, query_complexity: str = "medium") -> EvaluationResult:
        """Evaluate performance metrics"""
        score = 0.0
        max_score = 100.0
        details = {}
        
        # Time thresholds based on complexity
        time_thresholds = {
            "simple": 2.0,
            "medium": 5.0,
            "complex": 10.0
        }
        
        threshold = time_thresholds.get(query_complexity, 5.0)
        
        # Performance score (100 points)
        if processing_time <= threshold:
            performance_score = 100.0
        elif processing_time <= threshold * 2:
            performance_score = 100 - ((processing_time - threshold) / threshold) * 50
        else:
            performance_score = max(0, 50 - (processing_time - threshold * 2) * 5)
        
        score = performance_score
        details["performance_score"] = performance_score
        details["processing_time"] = processing_time
        details["threshold"] = threshold
        details["query_complexity"] = query_complexity
        
        # Log to WandB
        wandb.log({
            "evaluation/performance_score": performance_score,
            "evaluation/processing_time": processing_time,
            "evaluation/time_threshold": threshold,
            "evaluation/query_complexity": query_complexity
        })
        
        result = EvaluationResult(
            score=score,
            max_score=max_score,
            details=details,
            timestamp=time.time()
        )
        
        self.metrics["response_time"].append(processing_time)
        return result
    
    @weave.op()
    def comprehensive_evaluation(self, query: str, response: str, tools_used: List[str], 
                               processing_time: float, query_complexity: str = "medium") -> Dict[str, Any]:
        """Perform comprehensive evaluation with full tracking"""
        
        quality_eval = self.evaluate_response_quality(query, response)
        tool_eval = self.evaluate_tool_usage(tools_used, query)
        performance_eval = self.evaluate_performance(processing_time, query_complexity)
        
        # Overall score (weighted average)
        overall_score = (
            quality_eval.score * 0.4 +  # 40% weight on quality
            tool_eval.score * 0.3 +     # 30% weight on tool usage
            performance_eval.score * 0.3  # 30% weight on performance
        )
        
        grade = self._get_grade(overall_score)
        
        # Log comprehensive metrics to WandB
        wandb.log({
            "evaluation/overall_score": overall_score,
            "evaluation/grade": grade,
            "evaluation/quality_weight": quality_eval.score * 0.4,
            "evaluation/tool_weight": tool_eval.score * 0.3,
            "evaluation/performance_weight": performance_eval.score * 0.3
        })
        
        return {
            "overall_score": overall_score,
            "max_score": 100.0,
            "quality_evaluation": quality_eval,
            "tool_evaluation": tool_eval,
            "performance_evaluation": performance_eval,
            "grade": grade,
            "timestamp": time.time()
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    @weave.op()
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get evaluation summary statistics"""
        if not self.evaluation_history:
            return {"message": "No evaluations performed yet"}
        
        scores = [eval_result.score / eval_result.max_score for eval_result in self.evaluation_history]
        
        summary = {
            "total_evaluations": len(self.evaluation_history),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "best_score": max(scores) if scores else 0,
            "worst_score": min(scores) if scores else 0,
            "metrics_summary": {
                "avg_accuracy": sum(self.metrics["accuracy"]) / len(self.metrics["accuracy"]) if self.metrics["accuracy"] else 0,
                "avg_response_time": sum(self.metrics["response_time"]) / len(self.metrics["response_time"]) if self.metrics["response_time"] else 0,
                "avg_tool_usage": sum(self.metrics["tool_usage"]) / len(self.metrics["tool_usage"]) if self.metrics["tool_usage"] else 0
            }
        }
        
        # Log summary to WandB
        wandb.log({
            "evaluation_summary/total_evaluations": summary["total_evaluations"],
            "evaluation_summary/average_score": summary["average_score"],
            "evaluation_summary/best_score": summary["best_score"],
            "evaluation_summary/worst_score": summary["worst_score"]
        })
        
        return summary