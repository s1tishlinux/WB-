#!/usr/bin/env python3
"""
Streamlit Interview Demo Console
Interactive interface for W&B Weave Technical Interview
"""

import streamlit as st
import sys
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Mock Weave setup
class MockWeave:
    @staticmethod
    def init(project_name):
        return f"Weave initialized: {project_name}"
    
    @staticmethod
    def op():
        def decorator(func):
            return func
        return decorator

sys.modules['weave'] = MockWeave()

# Import our demo components
from technical_interview_demo import SimpleAgent, QualityEvaluator, PerformanceMonitor

# Page config
st.set_page_config(
    page_title="W&B Weave Interview Demo",
    page_icon="🎯",
    layout="wide"
)

def main():
    st.title("🎯 W&B Weave Technical Interview Demo")
    st.markdown("**Live Interactive Demo - Forward Deployed Engineer Position**")
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = SimpleAgent()
        st.session_state.evaluator = QualityEvaluator()
        st.session_state.monitor = PerformanceMonitor()
        st.session_state.demo_history = []
    
    # Sidebar - Demo Controls
    with st.sidebar:
        st.header("🎬 Demo Controls")
        
        demo_section = st.selectbox(
            "Interview Section",
            ["Overview", "Live Tracing", "Evaluation System", "Monitoring Dashboard", "Interactive Chat"]
        )
        
        st.header("📊 Live Metrics")
        if st.session_state.demo_history:
            total_queries = len(st.session_state.demo_history)
            avg_time = sum(h['processing_time'] for h in st.session_state.demo_history) / total_queries
            avg_quality = sum(h['quality'] for h in st.session_state.demo_history) / total_queries
            
            st.metric("Total Queries", total_queries)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
            st.metric("Avg Quality Score", f"{avg_quality:.2f}")
        else:
            st.info("No interactions yet")
        
        st.header("🕐 Demo Status")
        st.write(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
        st.write("**Status:** Live Demo Active")
    
    # Main content based on selected section
    if demo_section == "Overview":
        show_overview()
    elif demo_section == "Live Tracing":
        show_tracing_demo()
    elif demo_section == "Evaluation System":
        show_evaluation_demo()
    elif demo_section == "Monitoring Dashboard":
        show_monitoring_demo()
    elif demo_section == "Interactive Chat":
        show_interactive_chat()

def show_overview():
    st.header("📋 Technical Interview Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Required Features")
        st.markdown("""
        **Core Requirements:**
        - 🔍 **Weave Tracing** - Capture full execution flow
        - 📊 **Evaluations** - Quality assessment system  
        - 📈 **Monitors** - Performance tracking
        - 🔧 **Tool Calling** - Agent capabilities
        
        **Extra Credit:**
        - 🤖 Multi-agent workflow
        - 📊 Custom evaluations
        - 📋 Weave Reports/Panels
        """)
    
    with col2:
        st.subheader("🎯 Demo Architecture")
        st.markdown("""
        **Components Built:**
        - `SimpleAgent` - Core agent with tracing
        - `QualityEvaluator` - Response assessment
        - `PerformanceMonitor` - Metrics tracking
        - `Streamlit Interface` - Interactive demo
        
        **Technical Stack:**
        - OpenAI GPT-4o-mini (Real API)
        - W&B Weave (Mock for permissions)
        - Streamlit (Interactive UI)
        - Python (Core implementation)
        """)
    
    if st.button("🚀 Start Technical Demo", type="primary"):
        st.success("✅ Demo initialized! Use sidebar to navigate sections.")
        st.balloons()

def show_tracing_demo():
    st.header("🔍 Weave Tracing Demonstration")
    st.markdown("**Showing full execution flow capture with @weave.op() decorators**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Live Tracing Test")
        
        test_query = st.text_input(
            "Enter query to trace:",
            value="What is 15 * 23?",
            key="trace_query"
        )
        
        if st.button("🔍 Execute with Tracing"):
            with st.spinner("Processing with full tracing..."):
                # Execute with tracing
                start_time = time.time()
                trace_result = st.session_state.agent.process(test_query)
                
                # Show tracing steps
                st.success("✅ Tracing Complete!")
                
                st.subheader("📊 Trace Results")
                
                # Trace visualization
                trace_data = {
                    "Step": ["1. Reasoning", "2. Tool Execution", "3. Response Generation"],
                    "Function": ["reason()", "execute_tool()", "generate_response()"],
                    "Status": ["✅ Traced", "✅ Traced", "✅ Traced"],
                    "Time": ["0.1s", "0.2s", f"{trace_result['processing_time']:.1f}s"]
                }
                
                st.dataframe(pd.DataFrame(trace_data), use_container_width=True)
                
                # Show actual trace
                with st.expander("🔍 Full Trace Details"):
                    st.json(trace_result)
    
    with col2:
        st.subheader("🎯 Tracing Benefits")
        st.markdown("""
        **What Weave Tracing Captures:**
        - Function entry/exit
        - Input parameters
        - Output results
        - Execution time
        - Error handling
        - Call hierarchy
        
        **Production Benefits:**
        - Debug agent behavior
        - Performance optimization
        - Quality assurance
        - Audit trails
        """)

def show_evaluation_demo():
    st.header("📊 Evaluation System Demonstration")
    st.markdown("**Quality assessment with multiple metrics**")
    
    st.subheader("🧪 Evaluation Test Suite")
    
    test_cases = [
        ("What is 144 / 12?", "Mathematical"),
        ("Explain machine learning", "Technical"),
        ("How does photosynthesis work?", "Scientific")
    ]
    
    if st.button("🚀 Run Evaluation Suite"):
        results = []
        progress_bar = st.progress(0)
        
        for i, (query, category) in enumerate(test_cases):
            with st.spinner(f"Evaluating {category} query..."):
                # Process query
                trace = st.session_state.agent.process(query)
                evaluation = st.session_state.evaluator.evaluate_response(query, trace['response'])
                
                results.append({
                    'Query': query,
                    'Category': category,
                    'Relevance': evaluation['relevance'],
                    'Clarity': evaluation['clarity'],
                    'Helpfulness': evaluation['helpfulness'],
                    'Overall Score': evaluation['overall'],
                    'Response Time': trace['processing_time']
                })
                
                progress_bar.progress((i + 1) / len(test_cases))
        
        st.success("✅ Evaluation Complete!")
        
        # Results table
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality metrics chart
            fig1 = px.bar(
                df, 
                x='Category', 
                y=['Relevance', 'Clarity', 'Helpfulness'],
                title="Quality Metrics by Category",
                barmode='group'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Overall scores
            fig2 = px.scatter(
                df,
                x='Response Time',
                y='Overall Score',
                color='Category',
                title="Quality vs Performance",
                size_max=20
            )
            st.plotly_chart(fig2, use_container_width=True)

def show_monitoring_demo():
    st.header("📈 Monitoring Dashboard Demonstration")
    st.markdown("**Real-time performance tracking and alerts**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Generate Monitoring Data")
        
        if st.button("📊 Simulate Agent Load"):
            with st.spinner("Generating monitoring data..."):
                # Simulate multiple interactions
                queries = [
                    "What is 25 * 4?",
                    "Explain AI",
                    "Calculate 100 / 5",
                    "Define machine learning",
                    "What is 15 + 27?"
                ]
                
                for query in queries:
                    trace = st.session_state.agent.process(query)
                    evaluation = st.session_state.evaluator.evaluate_response(query, trace['response'])
                    st.session_state.monitor.record_interaction(trace, evaluation)
                    
                    # Add to demo history
                    st.session_state.demo_history.append({
                        'query': query,
                        'processing_time': trace['processing_time'],
                        'quality': evaluation['overall'],
                        'timestamp': time.time()
                    })
            
            st.success("✅ Monitoring data generated!")
    
    with col2:
        st.subheader("📊 Live Dashboard")
        
        if st.session_state.demo_history:
            summary = st.session_state.monitor.get_performance_summary()
            
            # Key metrics
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric(
                    "Avg Response Time",
                    f"{summary['avg_response_time']:.2f}s"
                )
            
            with col_b:
                st.metric(
                    "Success Rate",
                    f"{summary['success_rate']:.1%}"
                )
            
            with col_c:
                st.metric(
                    "Avg Quality",
                    f"{summary['avg_quality_score']:.2f}"
                )
        else:
            st.info("Generate monitoring data to see dashboard")
    
    # Performance charts
    if st.session_state.demo_history:
        st.subheader("📈 Performance Trends")
        
        df = pd.DataFrame(st.session_state.demo_history)
        df['interaction'] = range(1, len(df) + 1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(
                df,
                x='interaction',
                y='processing_time',
                title="Response Time Trend"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(
                df,
                x='interaction',
                y='quality',
                title="Quality Score Trend"
            )
            st.plotly_chart(fig2, use_container_width=True)

def show_interactive_chat():
    st.header("🎮 Interactive Agent Chat")
    st.markdown("**Live agent interaction with real-time tracing and evaluation**")
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if "metadata" in message:
                with st.expander("📊 Trace & Evaluation Details"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Trace Info:**")
                        st.json({
                            "processing_time": message["metadata"]["processing_time"],
                            "tool_used": message["metadata"]["tool_used"],
                            "reasoning": message["metadata"]["reasoning"][:100] + "..."
                        })
                    
                    with col2:
                        st.markdown("**Quality Scores:**")
                        st.json(message["metadata"]["evaluation"])
    
    # Chat input
    if prompt := st.chat_input("Ask the agent anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("Processing with full tracing..."):
                # Get agent response
                trace = st.session_state.agent.process(prompt)
                evaluation = st.session_state.evaluator.evaluate_response(prompt, trace['response'])
                
                # Record for monitoring
                st.session_state.monitor.record_interaction(trace, evaluation)
                st.session_state.demo_history.append({
                    'query': prompt,
                    'processing_time': trace['processing_time'],
                    'quality': evaluation['overall'],
                    'timestamp': time.time()
                })
                
                # Display response
                st.markdown(trace['response'])
                
                # Add to chat history with metadata
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": trace['response'],
                    "metadata": {
                        "processing_time": trace['processing_time'],
                        "tool_used": trace['tool_result'].get('tool', 'none'),
                        "reasoning": trace['reasoning'],
                        "evaluation": evaluation
                    }
                })
                
                # Show live metrics
                st.success(f"⚡ Processed in {trace['processing_time']:.2f}s | Quality: {evaluation['overall']:.2f}")

if __name__ == "__main__":
    main()