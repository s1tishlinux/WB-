#!/usr/bin/env python3
"""
Main demo script for technical interview
Shows all required features: tracing, evaluation, monitoring
"""

import weave
import time
from dotenv import load_dotenv
from agent import WeaveAgent
from evaluation.evaluators import ResponseQualityEvaluator
from monitoring.monitors import MonitoringDashboard

load_dotenv()

@weave.op()
def demo_single_agent():
    """Demonstrate single agent with tracing"""
    print("\n🤖 DEMO 1: Single Agent with Weave Tracing")
    print("=" * 60)
    
    agent = WeaveAgent(use_mock=False)
    dashboard = MonitoringDashboard()
    evaluator = ResponseQualityEvaluator()
    
    queries = [
        "Calculate 15 * 23",
        "What time is it?", 
        "Search for AI news",
        "What's the weather in Tokyo?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/4] Query: {query}")
        
        result = agent.process(query)
        
        # Evaluate
        quality = evaluator.evaluate(query, result["response"])
        
        # Monitor
        dashboard.record_agent_interaction(result, quality)
        
        print(f"Response: {result['response'][:100]}...")
        print(f"Tools: {result['selected_tools']}")
        print(f"Time: {result['processing_time']:.2f}s")
        print(f"Quality: {sum(quality.values())/len(quality):.2f}")
    
    return dashboard.get_dashboard_summary()

@weave.op()
def demo_evaluations():
    """Demonstrate evaluation system"""
    print("\n📊 DEMO 2: Evaluation System")
    print("=" * 60)
    
    agent = WeaveAgent(use_mock=False)
    evaluator = ResponseQualityEvaluator()
    
    test_cases = [
        ("Explain quantum computing", "technical_explanation"),
        ("What is 100 / 4?", "calculation"),
        ("Tell me about the weather", "general_query")
    ]
    
    results = []
    for query, category in test_cases:
        print(f"\nEvaluating: {query}")
        
        result = agent.process(query)
        quality = evaluator.evaluate(query, result["response"])
        
        print(f"Relevance: {quality['relevance']:.2f}")
        print(f"Completeness: {quality['completeness']:.2f}")
        print(f"Clarity: {quality['clarity']:.2f}")
        
        results.append({
            "query": query,
            "category": category,
            "quality": quality,
            "overall": sum(quality.values()) / len(quality)
        })
    
    return results

@weave.op()
def demo_monitoring():
    """Demonstrate monitoring dashboard"""
    print("\n📈 DEMO 3: Monitoring Dashboard")
    print("=" * 60)
    
    dashboard = MonitoringDashboard()
    
    # Simulate some interactions
    agent = WeaveAgent(use_mock=False)
    
    for i in range(5):
        result = agent.process(f"Test query {i+1}")
        quality = {"relevance": 0.8 + i*0.05, "completeness": 0.7 + i*0.06}
        dashboard.record_agent_interaction(result, quality)
    
    summary = dashboard.get_dashboard_summary()
    
    print("Performance Metrics:")
    if summary.get("performance", {}).get("status") != "no_data":
        print(f"  Avg Response Time: {summary['performance']['avg_response_time']:.2f}s")
        print(f"  Success Rate: {summary['errors']['success_rate']:.2%}")
    
    if summary.get("quality", {}).get("status") != "no_data":
        print(f"  Avg Quality: {summary['quality']['avg_quality']:.2f}")
        print(f"  Quality Trend: {summary['quality']['quality_trend']}")
    
    return summary

def main():
    """Run complete demo"""
    print("🎯 W&B Weave Agent Technical Interview Demo")
    print("=" * 70)
    
    # Initialize Weave
    weave.init('fde-technical-interview')
    print("✅ Weave initialized for project: fde-technical-interview")
    
    try:
        # Run demos
        agent_summary = demo_single_agent()
        eval_results = demo_evaluations()
        monitor_summary = demo_monitoring()
        
        print("\n🎉 DEMO COMPLETE!")
        print("=" * 70)
        print("✅ Tracing: All agent operations traced in Weave")
        print("✅ Evaluations: Quality metrics calculated")
        print("✅ Monitoring: Performance dashboard active")
        print("\n🔗 Check your W&B dashboard at: https://wandb.ai")
        print("   Project: fde-technical-interview")
        print("   Entity: mani-varma-bekkam")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    main()