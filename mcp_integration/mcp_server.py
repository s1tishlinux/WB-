"""
MCP (Model Context Protocol) Server Integration
Provides standardized tool interfaces for multi-agent system
"""

import weave
from typing import Dict, List, Any, Optional
import json
import asyncio
from dataclasses import dataclass
import time
import random

@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable

@weave.op()
class MCPServer:
    """MCP Server for multi-agent tool integration"""
    
    def __init__(self):
        self.tools = {}
        self.usage_stats = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools"""
        
        # Calculator tool
        self.register_tool(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            },
            handler=self._calculator_handler
        )
        
        # Weather tool
        self.register_tool(
            name="weather",
            description="Get weather information for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to get weather for"
                    }
                },
                "required": ["location"]
            },
            handler=self._weather_handler
        )
        
        # Time tool
        self.register_tool(
            name="time",
            description="Get current time information",
            parameters={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (optional)",
                        "default": "UTC"
                    }
                }
            },
            handler=self._time_handler
        )
        
        # Research tool
        self.register_tool(
            name="research",
            description="Research information on a topic",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Research query"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "default": "basic"
                    }
                },
                "required": ["query"]
            },
            handler=self._research_handler
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler: callable):
        """Register a new MCP tool"""
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )
        self.tools[name] = tool
        self.usage_stats[name] = {
            "calls": 0,
            "success": 0,
            "errors": 0,
            "total_time": 0.0
        }
    
    @weave.op()
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        stats = self.usage_stats[tool_name]
        
        start_time = time.time()
        stats["calls"] += 1
        
        try:
            # Validate parameters (simplified)
            result = await self._execute_tool(tool, parameters)
            stats["success"] += 1
            
            execution_time = time.time() - start_time
            stats["total_time"] += execution_time
            
            return {
                "tool": tool_name,
                "result": result,
                "execution_time": execution_time,
                "status": "success"
            }
            
        except Exception as e:
            stats["errors"] += 1
            execution_time = time.time() - start_time
            stats["total_time"] += execution_time
            
            return {
                "tool": tool_name,
                "error": str(e),
                "execution_time": execution_time,
                "status": "error"
            }
    
    async def _execute_tool(self, tool: MCPTool, parameters: Dict[str, Any]) -> Any:
        """Execute a tool handler"""
        if asyncio.iscoroutinefunction(tool.handler):
            return await tool.handler(**parameters)
        else:
            return tool.handler(**parameters)
    
    # Tool Handlers
    @weave.op()
    def _calculator_handler(self, expression: str) -> Dict[str, Any]:
        """Handle calculator operations"""
        try:
            # Safe evaluation (in production, use a proper math parser)
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return {
                    "expression": expression,
                    "result": result,
                    "type": "calculation"
                }
            else:
                raise ValueError("Invalid characters in expression")
        except Exception as e:
            raise Exception(f"Calculation error: {str(e)}")
    
    @weave.op()
    def _weather_handler(self, location: str) -> Dict[str, Any]:
        """Handle weather requests"""
        # Simulated weather data (replace with real API)
        conditions = ["sunny", "cloudy", "rainy", "snowy", "partly cloudy"]
        temperature = random.randint(-10, 35)
        condition = random.choice(conditions)
        humidity = random.randint(30, 90)
        
        return {
            "location": location,
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "unit": "celsius",
            "timestamp": time.time()
        }
    
    @weave.op()
    def _time_handler(self, timezone: str = "UTC") -> Dict[str, Any]:
        """Handle time requests"""
        import datetime
        
        current_time = datetime.datetime.now()
        
        return {
            "timestamp": current_time.timestamp(),
            "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": timezone,
            "iso_format": current_time.isoformat(),
            "day_of_week": current_time.strftime("%A")
        }
    
    @weave.op()
    def _research_handler(self, query: str, depth: str = "basic") -> Dict[str, Any]:
        """Handle research requests"""
        # Simulated research (replace with real research API)
        research_data = {
            "basic": f"Basic information about {query}",
            "detailed": f"Detailed analysis and insights about {query}",
            "comprehensive": f"Comprehensive research report on {query} with multiple perspectives"
        }
        
        return {
            "query": query,
            "depth": depth,
            "content": research_data.get(depth, research_data["basic"]),
            "sources": [f"source1_{query}", f"source2_{query}"],
            "confidence": random.uniform(0.7, 0.95),
            "timestamp": time.time()
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    @weave.op()
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        stats = {}
        for tool_name, tool_stats in self.usage_stats.items():
            avg_time = tool_stats["total_time"] / max(tool_stats["calls"], 1)
            success_rate = tool_stats["success"] / max(tool_stats["calls"], 1)
            
            stats[tool_name] = {
                **tool_stats,
                "average_execution_time": avg_time,
                "success_rate": success_rate
            }
        
        return stats

# Global MCP server instance
mcp_server = MCPServer()

@weave.op()
async def call_mcp_tool(tool_name: str, **parameters) -> Dict[str, Any]:
    """Convenience function to call MCP tools"""
    return await mcp_server.call_tool(tool_name, parameters)