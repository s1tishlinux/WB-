"""
Production Monitoring System with Weave + WandB Integration
Comprehensive monitoring for multi-agent workflows
"""

import weave
import wandb
from typing import Dict, List, Any, Optional, Callable
import time
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Alert:
    """Alert structure"""
    level: str  # INFO, WARNING, ERROR, CRITICAL
    message: str
    timestamp: float
    metric: str
    value: Any
    threshold: Any

@weave.op()
class ProductionPerformanceMonitor:
    """Production performance monitor with Weave + WandB integration"""
    
    def __init__(self, window_size: int = 100, project_name: str = "agent-monitoring"):
        self.window_size = window_size
        self.project_name = project_name
        self.metrics = defaultdict(lambda: deque(maxlen=window_size))
        self.alerts = []
        self.thresholds = {
            "response_time": {"warning": 5.0, "error": 10.0},
            "error_rate": {"warning": 0.1, "error": 0.2},
            "tool_failure_rate": {"warning": 0.05, "error": 0.15},
            "quality_score": {"warning": 0.6, "error": 0.4}
        }
    
    @weave.op()
    def record_metric(self, metric_name: str, value: Any, timestamp: float = None):
        """Record a metric value with comprehensive tracking"""
        if timestamp is None:
            timestamp = time.time()
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp
        })
        
        # Log to WandB
        wandb.log({
            f"monitor/{metric_name}": value,
            f"monitor/{metric_name}_timestamp": timestamp
        })
        
        # Check thresholds
        self._check_thresholds(metric_name, value)
    
    def _check_thresholds(self, metric_name: str, value: Any):
        """Check if metric exceeds thresholds"""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        
        if isinstance(value, (int, float)):
            if value >= thresholds.get("error", float('inf')):
                self._create_alert("ERROR", f"{metric_name} exceeded error threshold", metric_name, value, thresholds["error"])
            elif value >= thresholds.get("warning", float('inf')):
                self._create_alert("WARNING", f"{metric_name} exceeded warning threshold", metric_name, value, thresholds["warning"])
    
    def _create_alert(self, level: str, message: str, metric: str, value: Any, threshold: Any):
        """Create an alert with full tracking"""
        alert = Alert(
            level=level,
            message=message,
            timestamp=time.time(),
            metric=metric,
            value=value,
            threshold=threshold
        )
        self.alerts.append(alert)
        
        # Log alert to WandB
        wandb.log({
            f"alerts/{level.lower()}_count": 1,
            f"alerts/latest_{level.lower()}": message,
            f"alerts/{metric}_threshold_breach": value
        })
    
    @weave.op()
    def get_metric_stats(self, metric_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {"error": "No data available"}
        
        values = [entry["value"] for entry in self.metrics[metric_name] if isinstance(entry["value"], (int, float))]
        
        if not values:
            return {"error": "No numeric data available"}
        
        stats = {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1] if values else None,
            "std_dev": self._calculate_std_dev(values)
        }
        
        # Log stats to WandB
        wandb.log({
            f"stats/{metric_name}_mean": stats["mean"],
            f"stats/{metric_name}_min": stats["min"],
            f"stats/{metric_name}_max": stats["max"],
            f"stats/{metric_name}_std_dev": stats["std_dev"]
        })
        
        return stats
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @weave.op()
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""
        cutoff = time.time() - (hours * 3600)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]
    
    @weave.op()
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for monitoring dashboard"""
        dashboard_data = {
            "metrics": {name: self.get_metric_stats(name) for name in self.metrics.keys()},
            "recent_alerts": self.get_recent_alerts(),
            "alert_counts": {
                "total": len(self.alerts),
                "recent_24h": len(self.get_recent_alerts(24)),
                "by_level": self._count_alerts_by_level()
            },
            "system_health": self._calculate_system_health()
        }
        
        # Log dashboard summary to WandB
        wandb.log({
            "dashboard/total_alerts": dashboard_data["alert_counts"]["total"],
            "dashboard/recent_alerts_24h": dashboard_data["alert_counts"]["recent_24h"],
            "dashboard/system_health": dashboard_data["system_health"]
        })
        
        return dashboard_data
    
    def _count_alerts_by_level(self) -> Dict[str, int]:
        """Count alerts by level"""
        counts = defaultdict(int)
        for alert in self.get_recent_alerts():
            counts[alert.level] += 1
        return dict(counts)
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score (0-1)"""
        recent_alerts = self.get_recent_alerts(1)  # Last hour
        error_alerts = sum(1 for alert in recent_alerts if alert.level == "ERROR")
        warning_alerts = sum(1 for alert in recent_alerts if alert.level == "WARNING")
        
        # Simple health calculation
        health_score = 1.0 - (error_alerts * 0.2 + warning_alerts * 0.1)
        return max(0.0, min(1.0, health_score))

@weave.op()
class ProductionQualityMonitor:
    """Production quality monitor with comprehensive tracking"""
    
    def __init__(self, project_name: str = "quality-monitoring"):
        self.project_name = project_name
        self.quality_scores = deque(maxlen=1000)
        self.quality_trends = defaultdict(list)
        self.quality_thresholds = {
            "minimum_acceptable": 0.6,
            "target_quality": 0.8,
            "excellent_quality": 0.9
        }
    
    @weave.op()
    def record_quality_score(self, score: float, category: str = "general", details: Dict[str, Any] = None):
        """Record a quality score with comprehensive tracking"""
        entry = {
            "score": score,
            "category": category,
            "timestamp": time.time(),
            "details": details or {}
        }
        
        self.quality_scores.append(entry)
        self.quality_trends[category].append(entry)
        
        # Log to WandB
        wandb.log({
            f"quality/{category}_score": score,
            f"quality/{category}_timestamp": entry["timestamp"],
            "quality/overall_score": score
        })
        
        # Check quality thresholds
        self._check_quality_thresholds(score, category)
    
    def _check_quality_thresholds(self, score: float, category: str):
        """Check quality score against thresholds"""
        if score < self.quality_thresholds["minimum_acceptable"]:
            wandb.log({f"quality_alerts/{category}_below_minimum": score})
        elif score >= self.quality_thresholds["excellent_quality"]:
            wandb.log({f"quality_alerts/{category}_excellent": score})
    
    @weave.op()
    def get_quality_trend(self, category: str = "general", hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive quality trend analysis"""
        cutoff = time.time() - (hours * 3600)
        recent_scores = [
            entry for entry in self.quality_trends[category]
            if entry["timestamp"] >= cutoff
        ]
        
        if not recent_scores:
            return {"error": "No recent data"}
        
        scores = [entry["score"] for entry in recent_scores]
        
        trend_data = {
            "count": len(scores),
            "average": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "trend": self._calculate_trend(scores),
            "quality_distribution": self._calculate_quality_distribution(scores)
        }
        
        # Log trend data to WandB
        wandb.log({
            f"quality_trends/{category}_average": trend_data["average"],
            f"quality_trends/{category}_trend": 1 if trend_data["trend"] == "improving" else -1,
            f"quality_trends/{category}_count": trend_data["count"]
        })
        
        return trend_data
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction"""
        if len(scores) < 2:
            return "stable"
        
        # Simple linear trend
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 0.05:
            return "improving"
        elif second_avg < first_avg - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _calculate_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        distribution = {
            "excellent": 0,  # >= 0.9
            "good": 0,       # 0.8-0.89
            "acceptable": 0, # 0.6-0.79
            "poor": 0        # < 0.6
        }
        
        for score in scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.8:
                distribution["good"] += 1
            elif score >= 0.6:
                distribution["acceptable"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution

# Global monitor instances
performance_monitor = ProductionPerformanceMonitor()
quality_monitor = ProductionQualityMonitor()