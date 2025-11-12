#!/usr/bin/env python3
"""
LangChain Enhanced Agent with Weave Integration
Production-ready agentic AI using LangChain framework
"""

import weave
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_core.tools import BaseTool
import time
import json

@weave.op()
class LangChainWeaveAgent:
    """Enhanced agent using LangChain with Weave tracing"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=True
        )
        
        # Enhanced prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced AI agent with access to various tools. 
            Use tools when appropriate and provide comprehensive, accurate responses.
            
            Available capabilities:
            - Mathematical calculations
            - Web search and information retrieval  
            - Time and date queries
            - Weather information
            - Complex reasoning and analysis
            
            Always explain your reasoning and tool usage."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Memory management
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Keep last 10 exchanges
        )
        
        # Tools will be set during initialization
        self.tools = []
        self.agent_executor = None
        
    @weave.op()
    def add_tools(self, tools: List[BaseTool]):
        """Add LangChain tools to the agent"""
        self.tools.extend(tools)
        self._initialize_agent()
    
    @weave.op()
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        if not self.tools:
            return
            
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    @weave.op()
    def process(self, query: str) -> Dict[str, Any]:
        """Process query with LangChain agent and Weave tracing"""
        start_time = time.time()
        
        if not self.agent_executor:
            return {
                "error": "Agent not initialized. Add tools first.",
                "query": query,
                "processing_time": time.time() - start_time
            }
        
        try:
            # Execute with LangChain
            result = self.agent_executor.invoke({
                "input": query
            })
            
            processing_time = time.time() - start_time
            
            # Extract information from LangChain result
            response = result.get("output", "No response generated")
            
            # Get intermediate steps for tool tracking
            intermediate_steps = result.get("intermediate_steps", [])
            tools_used = []
            tool_results = {}
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_name = getattr(action, 'tool', 'unknown')
                    tools_used.append(tool_name)
                    tool_results[tool_name] = str(observation)
            
            return {
                "query": query,
                "response": response,
                "tools_used": tools_used,
                "tool_results": tool_results,
                "processing_time": processing_time,
                "langchain_result": result,
                "memory_length": len(self.memory.chat_memory.messages),
                "framework": "langchain"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "processing_time": time.time() - start_time,
                "framework": "langchain"
            }
    
    @weave.op()
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory statistics"""
        messages = self.memory.chat_memory.messages
        return {
            "total_messages": len(messages),
            "memory_window": self.memory.k,
            "recent_messages": [
                {
                    "type": type(msg).__name__,
                    "content": str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                }
                for msg in messages[-5:]  # Last 5 messages
            ]
        }
    
    @weave.op()
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    @weave.op()
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent configuration information"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "tools_count": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "memory_type": type(self.memory).__name__,
            "framework": "langchain",
            "agent_type": "openai_functions"
        }