#!/usr/bin/env python3
"""
Enhanced Production Agent with LangChain + MCP + Weave Integration
Ultimate agentic AI system combining all frameworks
"""

import weave
import sys
import os
from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import framework components
from langchain_integration.agents.langchain_agent import LangChainWeaveAgent
from langchain_integration.tools.langchain_tools import LangChainToolRegistry
from mcp_integration.protocols.weave_protocol import WeaveProtocol, MCPContextManager
from evaluation import ResponseQualityEvaluator, ToolUsageEvaluator
from monitoring import MonitoringDashboard

@weave.op()
class EnhancedProductionAgent:
    """
    Ultimate production agent combining:
    - LangChain for advanced agentic capabilities
    - MCP for context management
    - Weave for observability
    - Original evaluation and monitoring systems
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        # Core agent with LangChain
        self.langchain_agent = LangChainWeaveAgent(model=model)
        
        # Tool system
        self.tool_registry = LangChainToolRegistry()
        self.langchain_agent.add_tools(self.tool_registry.get_tools())
        
        # MCP protocol for context management
        self.mcp_protocol = WeaveProtocol(agent_id="enhanced-production-agent")
        self.context_manager = MCPContextManager(self.mcp_protocol)
        
        # Evaluation and monitoring (existing systems)
        self.quality_evaluator = ResponseQualityEvaluator()
        self.tool_evaluator = ToolUsageEvaluator()
        self.dashboard = MonitoringDashboard()
        
        # Enhanced capabilities
        self.conversation_contexts = {}
        self.session_id = f"session-{int(time.time())}"
        
        # Initialize context templates
        self._setup_context_templates()
    
    @weave.op()
    def _setup_context_templates(self):
        """Setup MCP context templates"""
        # Conversation context template
        self.context_manager.create_context_template(
            "conversation",
            {
                "session_id": "string",
                "user_query": "string", 
                "agent_response": "string",
                "tools_used": "array",
                "quality_metrics": "object",
                "timestamp": "number"
            }
        )
        
        # Task context template
        self.context_manager.create_context_template(
            "task",
            {
                "task_type": "string",
                "complexity": "string",
                "required_tools": "array",
                "expected_output": "string",
                "success_criteria": "object"
            }
        )
        
        # Performance context template
        self.context_manager.create_context_template(
            "performance",
            {
                "response_time": "number",
                "quality_score": "number",
                "tool_efficiency": "number",
                "error_count": "number",
                "success_rate": "number"
            }
        )
    
    @weave.op()
    def process_enhanced(self, query: str, context_keys: List[str] = None) -> Dict[str, Any]:
        """
        Enhanced processing with full framework integration
        """
        start_time = time.time()
        
        # 1. MCP: Create request and gather context
        mcp_request = self.mcp_protocol.process_agent_request(query, context_keys)
        
        # 2. Analyze task and create task context
        task_context_key = self._analyze_and_store_task(query)
        
        # 3. LangChain: Process with enhanced agent
        langchain_result = self.langchain_agent.process(query)
        
        # 4. Evaluation: Comprehensive assessment
        quality_metrics = self.quality_evaluator.evaluate(query, langchain_result.get("response", ""))
        tool_metrics = self.tool_evaluator.evaluate(
            query,
            langchain_result.get("tools_used", []),
            langchain_result.get("tool_results", {}),
            self.tool_registry.get_tool_names()
        )
        
        # 5. MCP: Store conversation context
        conversation_context_key = self._store_conversation_context(
            query, langchain_result, quality_metrics, tool_metrics
        )
        
        # 6. Monitoring: Record interaction
        self.dashboard.record_agent_interaction(langchain_result, quality_metrics)
        
        # 7. MCP: Link contexts
        self.context_manager.link_contexts(task_context_key, conversation_context_key, "contains")
        
        processing_time = time.time() - start_time
        
        # 8. Create enhanced result
        enhanced_result = {
            # Core response
            "query": query,
            "response": langchain_result.get("response", ""),
            "processing_time": processing_time,
            
            # Framework results
            "langchain_result": langchain_result,
            "mcp_request": {
                "id": mcp_request.id,
                "method": mcp_request.method,
                "timestamp": mcp_request.timestamp
            },
            
            # Evaluation results
            "quality_metrics": quality_metrics,
            "tool_metrics": tool_metrics,
            "overall_quality": sum(quality_metrics.values()) / len(quality_metrics) if quality_metrics else 0,
            
            # Context management
            "context_keys": {
                "task": task_context_key,
                "conversation": conversation_context_key
            },
            "session_id": self.session_id,
            
            # Framework info
            "frameworks_used": ["langchain", "mcp", "weave"],
            "agent_type": "enhanced_production"
        }
        
        return enhanced_result
    
    @weave.op()
    def _analyze_and_store_task(self, query: str) -> str:
        """Analyze task and store context"""
        # Simple task analysis (can be enhanced with ML)
        task_type = "general"
        complexity = "medium"
        required_tools = []
        
        # Determine task type
        if any(op in query.lower() for op in ["calculate", "math", "+", "-", "*", "/"]):
            task_type = "mathematical"
            required_tools.append("calculator")
        elif "search" in query.lower() or "find" in query.lower():
            task_type = "information_retrieval"
            required_tools.append("web_search")
        elif "weather" in query.lower():
            task_type = "weather_query"
            required_tools.append("weather")
        elif "time" in query.lower():
            task_type = "time_query"
            required_tools.append("time")
        
        # Determine complexity
        if len(query.split()) > 20:
            complexity = "high"
        elif len(query.split()) < 5:
            complexity = "low"
        
        # Store task context
        task_data = {
            "task_type": task_type,
            "complexity": complexity,
            "required_tools": required_tools,
            "expected_output": f"Response to {task_type} query",
            "success_criteria": {
                "min_quality": 0.7,
                "max_response_time": 10.0,
                "required_tools_used": len(required_tools) > 0
            }
        }
        
        return self.context_manager.create_context_from_template("task", task_data)
    
    @weave.op()
    def _store_conversation_context(self, query: str, result: Dict, quality_metrics: Dict, tool_metrics: Dict) -> str:
        """Store conversation context"""
        conversation_data = {
            "session_id": self.session_id,
            "user_query": query,
            "agent_response": result.get("response", ""),
            "tools_used": result.get("tools_used", []),
            "quality_metrics": quality_metrics,
            "tool_metrics": tool_metrics,
            "timestamp": time.time()
        }
        
        return self.context_manager.create_context_from_template("conversation", conversation_data)
    
    @weave.op()
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            # Agent info
            "agent_info": self.langchain_agent.get_agent_info(),
            "session_id": self.session_id,
            
            # Framework status
            "langchain_memory": self.langchain_agent.get_memory_summary(),
            "mcp_protocol": self.mcp_protocol.get_protocol_stats(),
            "context_manager": self.context_manager.get_context_manager_stats(),
            
            # Tool system
            "tools": self.tool_registry.get_tool_info(),
            
            # Monitoring
            "dashboard": self.dashboard.get_dashboard_summary(),
            
            # System metrics
            "frameworks": {
                "langchain": "active",
                "mcp": "active", 
                "weave": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @weave.op()
    def get_context_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get context and message history"""
        return {
            "mcp_messages": self.mcp_protocol.get_message_history(limit),
            "stored_contexts": self.mcp_protocol.list_contexts(),
            "context_relationships": len(self.context_manager.context_relationships),
            "session_contexts": [
                key for key in self.mcp_protocol.list_contexts() 
                if self.session_id in str(self.mcp_protocol.get_context(key))
            ]
        }
    
    @weave.op()
    def clear_session(self):
        """Clear current session data"""
        # Clear LangChain memory
        self.langchain_agent.clear_memory()
        
        # Start new session
        self.session_id = f"session-{int(time.time())}"
        
        return {"status": "session_cleared", "new_session_id": self.session_id}