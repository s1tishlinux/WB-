"""
Production Multi-Agent System with Weave + WandB Integration
LangGraph + MCP + Comprehensive Monitoring
"""

import weave
import wandb
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import json
import time
import operator
import os
from datetime import datetime
from mcp_integration.mcp_server import mcp_server, call_mcp_tool
import asyncio

# State definition for LangGraph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_agent: str
    task_analysis: Dict[str, Any]
    specialist_results: Dict[str, Any]
    tools_used: List[str]
    processing_time: float
    wandb_run_id: str

@weave.op()
class ProductionMultiAgent:
    """Production multi-agent system with Weave + WandB tracking"""
    
    def __init__(self, use_mock: bool = False, project_name: str = "multi-agent-system"):
        self.use_mock = use_mock
        self.project_name = project_name
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) if not use_mock else None
        
        # Initialize WandB
        self.wandb_run = wandb.init(
            project=project_name,
            config={
                "model": "gpt-4o-mini",
                "use_mock": use_mock,
                "framework": "langgraph",
                "mcp_enabled": True
            }
        )
        
        # Initialize Weave
        weave.init(f"{project_name}-weave")
        
        self.graph = self._build_graph()
        self.session_stats = {
            "total_queries": 0,
            "total_processing_time": 0.0,
            "agents_used": {},
            "tools_used": {},
            "errors": 0
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("coordinator", self.coordinator_node)
        workflow.add_node("research_agent", self.research_agent_node)
        workflow.add_node("analysis_agent", self.analysis_agent_node)
        workflow.add_node("writing_agent", self.writing_agent_node)
        workflow.add_node("mcp_executor", self.mcp_executor_node)
        workflow.add_node("synthesizer", self.synthesizer_node)
        
        # Add edges
        workflow.set_entry_point("coordinator")
        workflow.add_conditional_edges(
            "coordinator",
            self.route_to_agents,
            {
                "research": "research_agent",
                "analysis": "analysis_agent", 
                "writing": "writing_agent",
                "mcp_tools": "mcp_executor",
                "synthesize": "synthesizer"
            }
        )
        
        # Agent to synthesizer edges
        workflow.add_edge("research_agent", "synthesizer")
        workflow.add_edge("analysis_agent", "synthesizer")
        workflow.add_edge("writing_agent", "synthesizer")
        workflow.add_edge("mcp_executor", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    @weave.op()
    def coordinator_node(self, state: AgentState) -> AgentState:
        """Coordinate and route tasks to appropriate agents"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Log to WandB
        wandb.log({
            "coordinator/query_length": len(last_message),
            "coordinator/timestamp": time.time()
        })
        
        # Analyze task requirements
        query_lower = last_message.lower()
        
        # Determine routing with enhanced logic
        if any(op in query_lower for op in ["calculate", "+", "-", "*", "/", "math"]):
            route = "mcp_tools"
            agents_needed = ["mcp_executor"]
            tool_type = "calculator"
        elif "weather" in query_lower:
            route = "mcp_tools"
            agents_needed = ["mcp_executor"]
            tool_type = "weather"
        elif "time" in query_lower:
            route = "mcp_tools"
            agents_needed = ["mcp_executor"]
            tool_type = "time"
        elif any(word in query_lower for word in ["research", "find", "information", "search"]):
            route = "research"
            agents_needed = ["research_agent"]
            tool_type = "research"
        elif any(word in query_lower for word in ["analyze", "analysis", "insights", "examine"]):
            route = "analysis"
            agents_needed = ["analysis_agent"]
            tool_type = "analysis"
        elif any(word in query_lower for word in ["write", "document", "report", "create"]):
            route = "writing"
            agents_needed = ["writing_agent"]
            tool_type = "writing"
        else:
            route = "research"
            agents_needed = ["research_agent"]
            tool_type = "general"
        
        task_analysis = {
            "route": route,
            "agents_needed": agents_needed,
            "tool_type": tool_type,
            "reasoning": f"Routing to {route} based on query analysis",
            "query_classification": self._classify_query_complexity(last_message)
        }
        
        # Log routing decision to WandB
        wandb.log({
            "coordinator/route": route,
            "coordinator/tool_type": tool_type,
            "coordinator/query_complexity": task_analysis["query_classification"]["complexity"]
        })
        
        return {
            **state,
            "current_agent": "coordinator",
            "task_analysis": task_analysis
        }
    
    def _classify_query_complexity(self, query: str) -> Dict[str, Any]:
        """Classify query complexity for better routing"""
        word_count = len(query.split())
        has_multiple_tasks = len([w for w in ["and", "also", "then", "after"] if w in query.lower()]) > 0
        
        if word_count < 5:
            complexity = "simple"
        elif word_count < 15 and not has_multiple_tasks:
            complexity = "medium"
        else:
            complexity = "complex"
        
        return {
            "complexity": complexity,
            "word_count": word_count,
            "has_multiple_tasks": has_multiple_tasks
        }
    
    def route_to_agents(self, state: AgentState) -> str:
        """Route to appropriate agent based on task analysis"""
        return state["task_analysis"]["route"]
    
    @weave.op()
    def research_agent_node(self, state: AgentState) -> AgentState:
        """Research specialist agent with WandB tracking"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        start_time = time.time()
        
        if self.use_mock:
            response = f"Research Agent: Comprehensive research on '{query[:50]}...' completed with detailed findings."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research specialist. Provide comprehensive, accurate research with sources and insights."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        processing_time = time.time() - start_time
        
        # Log to WandB
        wandb.log({
            "research_agent/processing_time": processing_time,
            "research_agent/response_length": len(response),
            "research_agent/timestamp": time.time()
        })
        
        result = {
            "agent": "research",
            "response": response,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        
        specialist_results = state.get("specialist_results", {})
        specialist_results["research"] = result
        
        return {
            **state,
            "current_agent": "research_agent",
            "specialist_results": specialist_results,
            "messages": state["messages"] + [AIMessage(content=response)]
        }
    
    @weave.op()
    def analysis_agent_node(self, state: AgentState) -> AgentState:
        """Analysis specialist agent with WandB tracking"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        start_time = time.time()
        
        if self.use_mock:
            response = f"Analysis Agent: Deep analysis of '{query[:50]}...' with statistical insights and recommendations."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an analysis specialist. Provide detailed analysis, insights, and data-driven recommendations."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        processing_time = time.time() - start_time
        
        # Log to WandB
        wandb.log({
            "analysis_agent/processing_time": processing_time,
            "analysis_agent/response_length": len(response),
            "analysis_agent/timestamp": time.time()
        })
        
        result = {
            "agent": "analysis",
            "response": response,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        
        specialist_results = state.get("specialist_results", {})
        specialist_results["analysis"] = result
        
        return {
            **state,
            "current_agent": "analysis_agent",
            "specialist_results": specialist_results,
            "messages": state["messages"] + [AIMessage(content=response)]
        }
    
    @weave.op()
    def writing_agent_node(self, state: AgentState) -> AgentState:
        """Writing specialist agent with WandB tracking"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        start_time = time.time()
        
        if self.use_mock:
            response = f"Writing Agent: Well-structured document created for '{query[:50]}...' with clear formatting and flow."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a writing specialist. Create clear, well-structured, engaging content with proper formatting."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        processing_time = time.time() - start_time
        
        # Log to WandB
        wandb.log({
            "writing_agent/processing_time": processing_time,
            "writing_agent/response_length": len(response),
            "writing_agent/timestamp": time.time()
        })
        
        result = {
            "agent": "writing",
            "response": response,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        
        specialist_results = state.get("specialist_results", {})
        specialist_results["writing"] = result
        
        return {
            **state,
            "current_agent": "writing_agent",
            "specialist_results": specialist_results,
            "messages": state["messages"] + [AIMessage(content=response)]
        }
    
    @weave.op()
    async def mcp_executor_node(self, state: AgentState) -> AgentState:
        """Execute MCP tools with comprehensive tracking"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        start_time = time.time()
        query_lower = query.lower()
        tool_results = {}
        tools_used = []
        
        # Determine and execute appropriate MCP tools
        if any(op in query_lower for op in ["calculate", "+", "-", "*", "/", "math"]):
            import re
            match = re.search(r'[\d+\-*/().\s]+', query)
            expression = match.group(0).strip() if match else query
            result = await call_mcp_tool("calculator", expression=expression)
            tool_results["calculator"] = result
            tools_used.append("calculator")
            
        elif "weather" in query_lower:
            # Extract location or use default
            location = self._extract_location(query) or "New York"
            result = await call_mcp_tool("weather", location=location)
            tool_results["weather"] = result
            tools_used.append("weather")
            
        elif "time" in query_lower:
            result = await call_mcp_tool("time")
            tool_results["time"] = result
            tools_used.append("time")
            
        else:
            result = await call_mcp_tool("research", query=query, depth="detailed")
            tool_results["research"] = result
            tools_used.append("research")
        
        processing_time = time.time() - start_time
        
        # Log to WandB
        wandb.log({
            "mcp_executor/processing_time": processing_time,
            "mcp_executor/tools_used": len(tools_used),
            "mcp_executor/tools_list": tools_used,
            "mcp_executor/timestamp": time.time()
        })
        
        # Update session stats
        for tool in tools_used:
            self.session_stats["tools_used"][tool] = self.session_stats["tools_used"].get(tool, 0) + 1
        
        specialist_results = state.get("specialist_results", {})
        specialist_results["mcp_tools"] = {
            "agent": "mcp_executor",
            "response": json.dumps(tool_results, indent=2),
            "tool_results": tool_results,
            "tools_used": tools_used,
            "processing_time": processing_time,
            "timestamp": time.time()
        }
        
        return {
            **state,
            "current_agent": "mcp_executor",
            "specialist_results": specialist_results,
            "tools_used": tools_used,
            "messages": state["messages"] + [AIMessage(content=json.dumps(tool_results, indent=2))]
        }
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query (simplified)"""
        # Simple location extraction - in production, use NER
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["in", "for", "at"] and i + 1 < len(words):
                return words[i + 1].strip(".,!?")
        return None
    
    @weave.op()
    def synthesizer_node(self, state: AgentState) -> AgentState:
        """Synthesize results with comprehensive tracking"""
        specialist_results = state.get("specialist_results", {})
        
        start_time = time.time()
        
        if len(specialist_results) == 1 and "mcp_tools" in specialist_results:
            # Simple tool response
            tool_result = specialist_results["mcp_tools"]["tool_results"]
            final_response = f"Results:\n{json.dumps(tool_result, indent=2)}"
        else:
            # Multi-agent synthesis
            agents_used = list(specialist_results.keys())
            responses = [result["response"] for result in specialist_results.values()]
            
            if self.use_mock:
                final_response = f"Synthesized insights from {', '.join(agents_used)} agents: Combined analysis and recommendations based on multi-agent collaboration."
            else:
                synthesis_prompt = "Synthesize these agent responses into a coherent, comprehensive answer:\n\n"
                for agent, result in specialist_results.items():
                    synthesis_prompt += f"**{agent.upper()}**: {result['response']}\n\n"
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Synthesize the agent responses into a coherent, comprehensive answer. Maintain the insights from each agent while creating a unified response."),
                    ("human", "{synthesis_prompt}")
                ])
                chain = prompt | self.llm
                final_response = chain.invoke({"synthesis_prompt": synthesis_prompt}).content
        
        processing_time = time.time() - start_time
        
        # Log synthesis to WandB
        wandb.log({
            "synthesizer/processing_time": processing_time,
            "synthesizer/agents_involved": len(specialist_results),
            "synthesizer/final_response_length": len(final_response),
            "synthesizer/timestamp": time.time()
        })
        
        return {
            **state,
            "current_agent": "synthesizer",
            "messages": state["messages"] + [AIMessage(content=final_response)]
        }
    
    @weave.op()
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through multi-agent workflow with comprehensive tracking"""
        start_time = time.time()
        
        # Update session stats
        self.session_stats["total_queries"] += 1
        
        try:
            # Initialize state
            initial_state = AgentState(
                messages=[HumanMessage(content=query)],
                current_agent="",
                task_analysis={},
                specialist_results={},
                tools_used=[],
                processing_time=0.0,
                wandb_run_id=self.wandb_run.id
            )
            
            # Execute workflow
            final_state = self.graph.invoke(initial_state)
            
            processing_time = time.time() - start_time
            self.session_stats["total_processing_time"] += processing_time
            
            # Update agent usage stats
            for agent in final_state.get("specialist_results", {}).keys():
                self.session_stats["agents_used"][agent] = self.session_stats["agents_used"].get(agent, 0) + 1
            
            result = {
                "query": query,
                "task_analysis": final_state.get("task_analysis", {}),
                "specialist_results": final_state.get("specialist_results", {}),
                "tools_used": final_state.get("tools_used", []),
                "final_response": final_state["messages"][-1].content,
                "processing_time": processing_time,
                "agents_used": list(final_state.get("specialist_results", {}).keys()),
                "message_history": [msg.content for msg in final_state["messages"]],
                "wandb_run_id": self.wandb_run.id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log comprehensive metrics to WandB
            wandb.log({
                "query/processing_time": processing_time,
                "query/agents_count": len(result["agents_used"]),
                "query/tools_count": len(result["tools_used"]),
                "query/response_length": len(result["final_response"]),
                "query/success": True,
                "session/total_queries": self.session_stats["total_queries"],
                "session/avg_processing_time": self.session_stats["total_processing_time"] / self.session_stats["total_queries"]
            })
            
            return result
            
        except Exception as e:
            self.session_stats["errors"] += 1
            processing_time = time.time() - start_time
            
            # Log error to WandB
            wandb.log({
                "query/processing_time": processing_time,
                "query/success": False,
                "query/error": str(e),
                "session/errors": self.session_stats["errors"]
            })
            
            return {
                "query": query,
                "error": str(e),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        return {
            **self.session_stats,
            "wandb_run_id": self.wandb_run.id,
            "mcp_stats": mcp_server.get_usage_stats()
        }
    
    def close(self):
        """Clean up resources"""
        # Log final session stats
        wandb.log({
            "session/final_total_queries": self.session_stats["total_queries"],
            "session/final_total_time": self.session_stats["total_processing_time"],
            "session/final_errors": self.session_stats["errors"]
        })
        
        wandb.finish()

# Factory function
@weave.op()
def create_production_multi_agent(use_mock: bool = True, project_name: str = "multi-agent-system") -> ProductionMultiAgent:
    """Create a production multi-agent system with full tracking"""
    return ProductionMultiAgent(use_mock=use_mock, project_name=project_name)