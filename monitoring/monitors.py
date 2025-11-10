import weave
from typing import Dict, List, Any, Optional
import time
import statistics
from collections import deque, defaultdict

@weave.op()
class QualityMonitor:
    """Monitor response quality metrics"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.quality_scores = deque(maxlen=window_size)
        self.relevance_scores = deque(maxlen=window_size)
        self.coherence_scores = deque(maxlen=window_size)
        
    @weave.op()
    def record_quality(self, quality_metrics: Dict[str, float]):
        """Record quality metrics"""
        if "relevance" in quality_metrics:
            self.relevance_scores.append(quality_metrics["relevance"])
        if "coherence" in quality_metrics:
            self.coherence_scores.append(quality_metrics["coherence"])
        
        # Calculate overall quality score
        overall_score = sum(quality_metrics.values()) / len(quality_metrics)
        self.quality_scores.append(overall_score)
    
    @weave.op()
    def get_quality_stats(self) -> Dict[str, Any]:
        """Get quality statistics"""
        if not self.quality_scores:
            return {"status": "no_data"}
        
        return {
            "avg_quality": statistics.mean(self.quality_scores),
            "min_quality": min(self.quality_scores),
            "max_quality": max(self.quality_scores),
            "quality_trend": self._calculate_trend(list(self.quality_scores)),
            "sample_count": len(self.quality_scores),
            "avg_relevance": statistics.mean(self.relevance_scores) if self.relevance_scores else 0,
            "avg_coherence": statistics.mean(self.coherence_scores) if self.coherence_scores else 0
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction"""
        if len(scores) < 2:
            return "stable"
        
        recent = scores[-10:]  # Last 10 scores
        older = scores[-20:-10] if len(scores) >= 20 else scores[:-10]
        
        if not older:
            return "stable"
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        if recent_avg > older_avg * 1.05:
            return "improving"
        elif recent_avg < older_avg * 0.95:
            return "declining"
        else:
            return "stable"

@weave.op()
class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.token_usage = deque(maxlen=window_size)
        self.tool_usage_counts = defaultdict(int)
        
    @weave.op()
    def record_performance(self, processing_time: float, tokens_used: int = 0, tools_used: List[str] = None):
        """Record performance metrics"""
        self.response_times.append(processing_time)
        if tokens_used > 0:
            self.token_usage.append(tokens_used)
        
        if tools_used:
            for tool in tools_used:
                self.tool_usage_counts[tool] += 1
    
    @weave.op()
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.response_times:
            return {"status": "no_data"}
        
        return {
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": self._percentile(list(self.response_times), 95),
            "avg_tokens": statistics.mean(self.token_usage) if self.token_usage else 0,
            "total_requests": len(self.response_times),
            "tool_usage": dict(self.tool_usage_counts),
            "performance_trend": self._calculate_performance_trend()
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend"""
        if len(self.response_times) < 10:
            return "stable"
        
        recent = list(self.response_times)[-10:]
        older = list(self.response_times)[-20:-10] if len(self.response_times) >= 20 else list(self.response_times)[:-10]
        
        if not older:
            return "stable"
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        if recent_avg < older_avg * 0.95:
            return "improving"
        elif recent_avg > older_avg * 1.05:
            return "declining"
        else:
            return "stable"

@weave.op()
class ErrorMonitor:
    """Monitor error rates and types"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.error_log = deque(maxlen=window_size)
        self.error_types = defaultdict(int)
        self.success_count = 0
        self.total_count = 0
        
    @weave.op()
    def record_interaction(self, success: bool, error_type: Optional[str] = None, error_message: Optional[str] = None):
        """Record interaction outcome"""
        self.total_count += 1
        
        if success:
            self.success_count += 1
        else:
            error_entry = {
                "timestamp": time.time(),
                "error_type": error_type or "unknown",
                "error_message": error_message or "No message",
                "success": False
            }
            self.error_log.append(error_entry)
            self.error_types[error_type or "unknown"] += 1
    
    @weave.op()
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        error_rate = (self.total_count - self.success_count) / max(self.total_count, 1)
        
        return {
            "error_rate": error_rate,
            "success_rate": 1 - error_rate,
            "total_interactions": self.total_count,
            "error_count": len(self.error_log),
            "error_types": dict(self.error_types),
            "recent_errors": list(self.error_log)[-5:],  # Last 5 errors
            "error_trend": self._calculate_error_trend()
        }
    
    def _calculate_error_trend(self) -> str:
        """Calculate error trend"""
        if len(self.error_log) < 5:
            return "stable"
        
        recent_errors = [e for e in self.error_log if time.time() - e["timestamp"] < 3600]  # Last hour
        older_errors = [e for e in self.error_log if 3600 <= time.time() - e["timestamp"] < 7200]  # Previous hour
        
        recent_rate = len(recent_errors) / max(self.total_count * 0.1, 1)  # Approximate recent rate
        older_rate = len(older_errors) / max(self.total_count * 0.1, 1)  # Approximate older rate
        
        if recent_rate > older_rate * 1.2:
            return "increasing"
        elif recent_rate < older_rate * 0.8:
            return "decreasing"
        else:
            return "stable"

@weave.op()
class MonitoringDashboard:
    """Centralized monitoring dashboard"""
    
    def __init__(self):
        self.quality_monitor = QualityMonitor()
        self.performance_monitor = PerformanceMonitor()
        self.error_monitor = ErrorMonitor()
    
    @weave.op()
    def record_agent_interaction(self, agent_result: Dict[str, Any], quality_metrics: Dict[str, float] = None):
        """Record a complete agent interaction"""
        # Record performance
        processing_time = agent_result.get("processing_time", 0)
        tokens_used = agent_result.get("reasoning", {}).get("tokens_used", 0)
        tools_used = agent_result.get("selected_tools", [])
        
        self.performance_monitor.record_performance(processing_time, tokens_used, tools_used)
        
        # Record quality
        if quality_metrics:
            self.quality_monitor.record_quality(quality_metrics)
        
        # Record errors
        has_errors = any("error" in str(result) for result in agent_result.get("tool_results", {}).values())
        self.error_monitor.record_interaction(not has_errors)
    
    @weave.op()
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        return {
            "quality": self.quality_monitor.get_quality_stats(),
            "performance": self.performance_monitor.get_performance_stats(),
            "errors": self.error_monitor.get_error_stats(),
            "timestamp": time.time()
        }