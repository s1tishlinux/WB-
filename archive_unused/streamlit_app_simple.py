#!/usr/bin/env python3
"""
Simplified Streamlit UI for W&B Weave Agent (No Weave Dependency)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from dotenv import load_dotenv
import json
import time

load_dotenv()

# Mock weave decorator
def mock_weave_op():
    def decorator(func):
        return func
    return decorator

# Simple Agent without Weave
class SimpleAgent:
    def __init__(self):
        self.tools = ["calculator", "web_search", "time", "weather"]
        
    def process(self, query):
        start_time = time.time()
        
        # Simple tool selection
        selected_tools = []
        if any(op in query for op in ["+", "-", "*", "/"]):
            selected_tools.append("calculator")
        if "search" in query.lower():
            selected_tools.append("web_search")
        if "time" in query.lower():
            selected_tools.append("time")
        if "weather" in query.lower():
            selected_tools.append("weather")
            
        # Mock response
        response = f"Mock response for: {query}"
        if selected_tools:
            response += f" (Used tools: {', '.join(selected_tools)})"
            
        return {
            "query": query,
            "response": response,
            "selected_tools": selected_tools,
            "processing_time": time.time() - start_time,
            "reasoning": {"reasoning": f"Analyzed query: {query}"}
        }

def main():
    st.set_page_config(page_title="W&B Weave Agent Demo", page_icon="🤖")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_stats" not in st.session_state:
        st.session_state.agent_stats = []
    
    # Initialize agent
    agent = SimpleAgent()
    
    st.title("🤖 W&B Weave Agent Demo")
    st.markdown("**Demo Mode** - Shows functionality without API dependencies")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        agent_mode = st.selectbox(
            "Agent Mode",
            ["Single Agent", "Multi-Agent Workflow"]
        )
        
        st.header("📊 Statistics")
        if st.session_state.agent_stats:
            avg_time = sum(s["time"] for s in st.session_state.agent_stats) / len(st.session_state.agent_stats)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
            st.metric("Total Queries", len(st.session_state.agent_stats))
        
        st.header("🔧 Available Tools")
        for tool in agent.tools:
            st.write(f"• {tool}")
    
    # Main interface
    st.header("💬 Chat Interface")
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Agent:** {message['content']}")
            if "metadata" in message:
                with st.expander("📊 Details"):
                    st.json(message["metadata"])
        st.markdown("---")
    
    # Input form
    with st.form(key="chat_form", clear_on_submit=True):
        prompt = st.text_input("Ask me anything...")
        submit_button = st.form_submit_button("Send")
    
    if submit_button and prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process with agent
        with st.spinner("Processing..."):
            result = agent.process(prompt)
            
            # Record stats
            st.session_state.agent_stats.append({
                "time": result["processing_time"],
                "tools": result["selected_tools"],
                "query": prompt
            })
            
            # Add response
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"],
                "metadata": {
                    "processing_time": result["processing_time"],
                    "tools_used": result["selected_tools"]
                }
            })
        
        st.rerun()
    
    # Sample queries
    st.header("🎯 Try These Sample Queries")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Calculate 55 + 45"):
            st.session_state.messages.append({"role": "user", "content": "Calculate 55 + 45"})
            st.rerun()
    
    with col2:
        if st.button("Search for AI news"):
            st.session_state.messages.append({"role": "user", "content": "Search for AI news"})
            st.rerun()
    
    # Footer
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent_stats = []
        st.rerun()

if __name__ == "__main__":
    main()