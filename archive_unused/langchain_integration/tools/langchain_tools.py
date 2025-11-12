#!/usr/bin/env python3
"""
LangChain Tools with Weave Integration
Enhanced tool system using LangChain framework
"""

import weave
from typing import Dict, Any, Optional, Type
from langchain_core.tools import BaseTool
from langchain.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field
import requests
import json
import time
import math
import random

class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression to evaluate")

@weave.op()
class WeaveCalculatorTool(BaseTool):
    """Enhanced calculator tool with Weave tracing"""
    name = "calculator"
    description = "Perform mathematical calculations. Input should be a valid mathematical expression."
    args_schema: Type[BaseModel] = CalculatorInput
    
    @weave.op()
    def _run(self, expression: str) -> str:
        """Execute calculation with tracing"""
        try:
            # Safe evaluation (in production, use a proper math parser)
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"The result of {expression} is {result}"
            else:
                return f"Error: Invalid characters in expression '{expression}'"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"

class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query to find information on the web")

@weave.op()
class WeaveWebSearchTool(BaseTool):
    """Enhanced web search tool with Weave tracing"""
    name = "web_search"
    description = "Search the web for current information. Use this for recent events, news, or general information lookup."
    args_schema: Type[BaseModel] = WebSearchInput
    
    def __init__(self):
        super().__init__()
        self.serper_api_key = None
        try:
            import os
            self.serper_api_key = os.getenv("SERPER_API_KEY")
        except:
            pass
    
    @weave.op()
    def _run(self, query: str) -> str:
        """Execute web search with tracing"""
        if self.serper_api_key:
            return self._serper_search(query)
        else:
            return self._fallback_search(query)
    
    @weave.op()
    def _serper_search(self, query: str) -> str:
        """Real web search using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = json.dumps({"q": query})
            
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            results = []
            for item in data.get("organic", [])[:3]:  # Top 3 results
                results.append(f"• {item.get('title', '')}: {item.get('snippet', '')}")
            
            if results:
                return f"Search results for '{query}':\n" + "\n".join(results)
            else:
                return f"No results found for '{query}'"
                
        except Exception as e:
            return f"Search error for '{query}': {str(e)}"
    
    @weave.op()
    def _fallback_search(self, query: str) -> str:
        """Fallback search with simulated results"""
        return f"Simulated search results for '{query}':\n• Result 1: Information about {query}\n• Result 2: Related content for {query}\n• Result 3: Additional details on {query}\n\nNote: Add SERPER_API_KEY for real web search"

class WeatherInput(BaseModel):
    """Input for weather tool"""
    location: str = Field(description="Location to get weather information for")

@weave.op()
class WeaveWeatherTool(BaseTool):
    """Enhanced weather tool with Weave tracing"""
    name = "weather"
    description = "Get current weather information for a specific location."
    args_schema: Type[BaseModel] = WeatherInput
    
    @weave.op()
    def _run(self, location: str) -> str:
        """Get weather information with tracing"""
        # Simulated weather data (in production, use real weather API)
        conditions = ["sunny", "cloudy", "rainy", "snowy", "partly cloudy"]
        temperature = random.randint(-10, 35)
        condition = random.choice(conditions)
        humidity = random.randint(30, 90)
        
        return f"Weather in {location}: {temperature}°C, {condition}, humidity {humidity}%"

class TimeInput(BaseModel):
    """Input for time tool"""
    timezone: Optional[str] = Field(default="UTC", description="Timezone for time query")

@weave.op()
class WeaveTimeTool(BaseTool):
    """Enhanced time tool with Weave tracing"""
    name = "time"
    description = "Get current time and date information."
    args_schema: Type[BaseModel] = TimeInput
    
    @weave.op()
    def _run(self, timezone: str = "UTC") -> str:
        """Get current time with tracing"""
        current_time = time.time()
        formatted_time = time.ctime(current_time)
        return f"Current time ({timezone}): {formatted_time}"

@weave.op()
class LangChainToolRegistry:
    """Registry for LangChain tools with Weave integration"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    @weave.op()
    def _register_default_tools(self):
        """Register default LangChain tools"""
        # Core tools
        self.tools["calculator"] = WeaveCalculatorTool()
        self.tools["web_search"] = WeaveWebSearchTool()
        self.tools["weather"] = WeaveWeatherTool()
        self.tools["time"] = WeaveTimeTool()
        
        # Try to add DuckDuckGo search as backup
        try:
            self.tools["duckduckgo_search"] = DuckDuckGoSearchRun()
        except:
            pass  # Skip if not available
    
    @weave.op()
    def get_tools(self) -> list:
        """Get list of all tools"""
        return list(self.tools.values())
    
    @weave.op()
    def get_tool_names(self) -> list:
        """Get list of tool names"""
        return list(self.tools.keys())
    
    @weave.op()
    def add_tool(self, name: str, tool: BaseTool):
        """Add a custom tool"""
        self.tools[name] = tool
    
    @weave.op()
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about all tools"""
        return {
            name: {
                "description": tool.description,
                "name": tool.name,
                "type": type(tool).__name__
            }
            for name, tool in self.tools.items()
        }