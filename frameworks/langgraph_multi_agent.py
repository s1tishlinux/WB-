"""
LangGraph Multi-Agent System with Weave Integration
Production-ready multi-agent workflow using LangGraph and MCP
"""

import weave
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import json
import time
import operator
import asyncio

# State definition for LangGraph
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_agent: str
    task_analysis: Dict[str, Any]
    specialist_results: Dict[str, Any]
    tools_used: List[str]
    processing_time: float

@weave.op()
class LangGraphMultiAgent:
    """Production multi-agent system using LangGraph"""
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) if not use_mock else None
        self.tools = self._setup_tools()
        self.tool_executor = ToolExecutor(self.tools)
        self.graph = self._build_graph()
        
    def _setup_tools(self) -> List:
        """Setup MCP-compatible tools"""
        
        @tool
        def calculator(expression: str) -> str:
            """Perform mathematical calculations"""
            try:
                result = eval(expression.strip())
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        @tool
        def weather_tool(location: str) -> str:
            """Get weather information for a location"""
            import random
            conditions = ["sunny", "cloudy", "rainy", "snowy"]
            temp = random.randint(-10, 35)
            condition = random.choice(conditions)
            return f"Weather in {location}: {temp}°C, {condition}"
        
        @tool
        def time_tool() -> str:
            """Get current time"""
            import datetime
            return f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        @tool
        def research_tool(query: str) -> str:
            """Research information on a topic"""
            return f"Research results for '{query}': [Simulated research data and insights]"
        
        return [calculator, weather_tool, time_tool, research_tool]
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("coordinator", self.coordinator_node)
        workflow.add_node("research_agent", self.research_agent_node)
        workflow.add_node("analysis_agent", self.analysis_agent_node)
        workflow.add_node("writing_agent", self.writing_agent_node)
        workflow.add_node("tool_executor", self.tool_executor_node)
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
                "tools": "tool_executor",
                "synthesize": "synthesizer"
            }
        )
        
        # Agent to synthesizer edges
        workflow.add_edge("research_agent", "synthesizer")
        workflow.add_edge("analysis_agent", "synthesizer")
        workflow.add_edge("writing_agent", "synthesizer")
        workflow.add_edge("tool_executor", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    @weave.op()
    def coordinator_node(self, state: AgentState) -> AgentState:
        """Coordinate and route tasks to appropriate agents"""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Analyze task requirements
        query_lower = last_message.lower()
        
        # Determine routing
        if any(op in query_lower for op in ["calculate", "+", "-", "*", "/", "math"]):
            route = "tools"
            agents_needed = ["tool_executor"]
        elif "weather" in query_lower:
            route = "tools"
            agents_needed = ["tool_executor"]
        elif "time" in query_lower:
            route = "tools"
            agents_needed = ["tool_executor"]
        elif any(word in query_lower for word in ["research", "find", "information"]):
            route = "research"
            agents_needed = ["research_agent"]
        elif any(word in query_lower for word in ["analyze", "analysis", "insights"]):
            route = "analysis"
            agents_needed = ["analysis_agent"]
        elif any(word in query_lower for word in ["write", "document", "report"]):
            route = "writing"
            agents_needed = ["writing_agent"]
        else:
            route = "research"
            agents_needed = ["research_agent"]
        
        task_analysis = {
            "route": route,
            "agents_needed": agents_needed,
            "reasoning": f"Routing to {route} based on query analysis"
        }
        
        return {
            **state,
            "current_agent": "coordinator",
            "task_analysis": task_analysis
        }
    
    def route_to_agents(self, state: AgentState) -> str:
        """Route to appropriate agent based on task analysis"""
        return state["task_analysis"]["route"]
    
    @weave.op()
    def research_agent_node(self, state: AgentState) -> AgentState:
        """Research specialist agent"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        if self.use_mock:
            response = f"Research Agent: Analyzed '{query[:50]}...' and found relevant information."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a research specialist. Provide comprehensive research on the given topic."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        result = {
            "agent": "research",
            "response": response,
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
        """Analysis specialist agent"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        if self.use_mock:
            response = f"Analysis Agent: Performed detailed analysis of '{query[:50]}...' with insights."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an analysis specialist. Provide detailed analysis and insights."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        result = {
            "agent": "analysis",
            "response": response,
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
        """Writing specialist agent"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        if self.use_mock:
            response = f"Writing Agent: Created well-structured content for '{query[:50]}...'."
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a writing specialist. Create clear, well-structured content."),
                ("human", "{query}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"query": query}).content
        
        result = {
            "agent": "writing",
            "response": response,
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
    def tool_executor_node(self, state: AgentState) -> AgentState:
        """Execute tools based on query"""
        messages = state["messages"]
        query = messages[-1].content if messages else ""
        
        # Determine which tool to use
        query_lower = query.lower()
        tool_results = {}
        
        if any(op in query_lower for op in ["calculate", "+", "-", "*", "/", "math"]):
            import re
            match = re.search(r'[\d+\-*/().\s]+', query)
            expression = match.group(0).strip() if match else query
            result = self.tools[0].invoke(expression)  # calculator
            tool_results["calculator"] = result
        elif "weather" in query_lower:
            # Extract location or use default
            location = "New York"  # Could be extracted from query
            result = self.tools[1].invoke(location)  # weather_tool
            tool_results["weather"] = result
        elif "time" in query_lower:
            result = self.tools[2].invoke()  # time_tool
            tool_results["time"] = result
        else:
            result = self.tools[3].invoke(query)  # research_tool
            tool_results["research"] = result
        
        specialist_results = state.get("specialist_results", {})
        specialist_results["tools"] = {
            "agent": "tool_executor",
            "response": json.dumps(tool_results),
            "tool_results": tool_results,
            "timestamp": time.time()
        }
        
        tools_used = list(tool_results.keys())
        
        return {
            **state,
            "current_agent": "tool_executor",
            "specialist_results": specialist_results,
            "tools_used": tools_used,
            "messages": state["messages"] + [AIMessage(content=json.dumps(tool_results))]
        }
    
    @weave.op()
    def synthesizer_node(self, state: AgentState) -> AgentState:
        """Synthesize results from all agents"""
        specialist_results = state.get("specialist_results", {})
        
        if len(specialist_results) == 1 and "tools" in specialist_results:
            # Simple tool response
            tool_result = specialist_results["tools"]["tool_results"]
            final_response = f"Tool Results: {json.dumps(tool_result, indent=2)}"
        else:
            # Multi-agent synthesis
            agents_used = list(specialist_results.keys())
            responses = [result["response"] for result in specialist_results.values()]
            
            if self.use_mock:
                final_response = f"Synthesized insights from {', '.join(agents_used)} agents: {' | '.join(responses[:100])}"
            else:
                synthesis_prompt = f"Synthesize these agent responses into a coherent answer:\n\n"
                for agent, result in specialist_results.items():
                    synthesis_prompt += f"{agent}: {result['response']}\n\n"
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Synthesize the agent responses into a coherent, comprehensive answer."),
                    ("human", "{synthesis_prompt}")
                ])
                chain = prompt | self.llm
                final_response = chain.invoke({"synthesis_prompt": synthesis_prompt}).content
        
        return {
            **state,
            "current_agent": "synthesizer",
            "messages": state["messages"] + [AIMessage(content=final_response)]
        }
    
    @weave.op()
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through LangGraph multi-agent workflow"""
        start_time = time.time()
        
        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            current_agent="",
            task_analysis={},
            specialist_results={},
            tools_used=[],
            processing_time=0.0
        )
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        return {
            "query": query,
            "task_analysis": final_state.get("task_analysis", {}),
            "specialist_results": final_state.get("specialist_results", {}),
            "tools_used": final_state.get("tools_used", []),
            "final_response": final_state["messages"][-1].content,
            "processing_time": processing_time,
            "agents_used": list(final_state.get("specialist_results", {}).keys()),
            "message_history": [msg.content for msg in final_state["messages"]]
        }

# Factory function for easy instantiation
@weave.op()
def create_langgraph_multi_agent(use_mock: bool = True) -> LangGraphMultiAgent:
    """Create a LangGraph multi-agent system"""
    return LangGraphMultiAgent(use_mock=use_mock)