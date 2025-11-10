import weave
from typing import Dict, List, Any, Callable
import requests
import json
import time
import random

@weave.op()
class ToolRegistry:
    """Registry for agent tools with execution tracking"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "usage_count": 0,
            "success_count": 0,
            "error_count": 0
        }
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool("web_search", self._web_search, "Search the web for information")
        self.register_tool("calculator", self._calculator, "Perform mathematical calculations")
        self.register_tool("weather", self._weather, "Get weather information")
        self.register_tool("time", self._time, "Get current time information")
    
    @weave.op()
    def _web_search(self, query: str) -> Dict[str, Any]:
        """Search using Serper API"""
        import os
        
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not serper_api_key:
            # Fallback to simulated results if no API key
            return {
                "results": [
                    {"title": f"Search result for: {query}", "url": "https://example.com", "snippet": f"Information about {query}"},
                    {"title": f"Related to: {query}", "url": "https://example2.com", "snippet": f"More details on {query}"}
                ],
                "query": query,
                "note": "Using simulated results - add SERPER_API_KEY for real search"
            }
        
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            payload = json.dumps({"q": query})
            
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract organic results
            results = []
            for item in data.get("organic", [])[:5]:  # Top 5 results
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return {
                "results": results,
                "query": query,
                "total_results": len(results)
            }
            
        except Exception as e:
            return {
                "error": f"Serper API error: {str(e)}",
                "query": query
            }
    
    @weave.op()
    def _calculator(self, expression: str) -> Dict[str, Any]:
        """Safe calculator"""
        try:
            # Simple evaluation (in production, use a safer approach)
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return {"result": result, "expression": expression}
            else:
                return {"error": "Invalid characters in expression"}
        except Exception as e:
            return {"error": str(e)}
    
    @weave.op()
    def _weather(self, location: str) -> Dict[str, Any]:
        """Simulate weather API (replace with actual API)"""
        # Simulated weather data
        weather_conditions = ["sunny", "cloudy", "rainy", "snowy"]
        return {
            "location": location,
            "temperature": random.randint(-10, 35),
            "condition": random.choice(weather_conditions),
            "humidity": random.randint(30, 90)
        }
    
    @weave.op()
    def _time(self, timezone: str = "UTC") -> Dict[str, Any]:
        """Get current time"""
        current_time = time.time()
        return {
            "timestamp": current_time,
            "formatted": time.ctime(current_time),
            "timezone": timezone
        }
    
    @weave.op()
    def execute(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool with tracking"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools[tool_name]
        tool["usage_count"] += 1
        
        try:
            result = tool["function"](*args, **kwargs)
            tool["success_count"] += 1
            return result
        except Exception as e:
            tool["error_count"] += 1
            return {"error": str(e)}
    
    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())
    
    @weave.op()
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        stats = {}
        for name, tool in self.tools.items():
            stats[name] = {
                "description": tool["description"],
                "usage_count": tool["usage_count"],
                "success_count": tool["success_count"],
                "error_count": tool["error_count"],
                "success_rate": tool["success_count"] / max(tool["usage_count"], 1)
            }
        return stats