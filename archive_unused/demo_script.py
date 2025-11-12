#!/usr/bin/env python3
"""
W&B Weave Agent Demo Script - Meeting PDF Requirements
Demonstrates: Tracing, Evaluations, Monitors, Multi-Agent Workflow
"""

import weave
import os
from dotenv import load_dotenv
from agent import WeaveAgent
from multi_agent.workflow import MultiAgentWorkflow
from evaluation.evaluators import ResponseQualityEvaluator, ToolUsageEvaluator
from evaluation.scorers import WeaveScorers
from monitoring.monitors import MonitoringDashboard

load_dotenv()

def setup_weave():
    """Initialize Weave with your project"""
    weave.init("fde-technical-demo")
    print("✅ Weave initialized for FDE Technical Demo")

@weave.op()
def demonstrate_tracing():
    """Requirement 2a: Tracing - capture full execution flow"""
    print("\n🔍 DEMONSTRATING TRACING")
    print("=" * 50)
    
    agent = WeaveAgent(use_mock=not bool(os.getenv("OPENAI_API_KEY")))
    
    # Test queries that show different execution paths
    test_queries = [
        "Calculate 25 * 4 + 10",  # Tool calling
        "Search for latest AI developments",  # Web search
        "What time is it now?",  # Time tool
    ]
    
    results = []
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = agent.process(query)
        results.append(result)
        
        print(f"🎯 Response: {result['response'][:100]}...")
        print(f"🔧 Tools Used: {result['selected_tools']}")
        print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
    
    print(f"\n✅ Traced {len(results)} agent interactions")
    return results

@weave.op()
def demonstrate_evaluations():
    """Requirement 2b: Evaluations - meaningful evaluation or Weave native scorer"""
    print("\n📊 DEMONSTRATING EVALUATIONS")
    print("=" * 50)
    
    agent = WeaveAgent(use_mock=not bool(os.getenv("OPENAI_API_KEY")))
    evaluator = ResponseQualityEvaluator()
    
    # Test query for evaluation
    query = "Explain quantum computing in simple terms"
    result = agent.process(query)
    
    # Custom evaluation
    quality_metrics = evaluator.evaluate(query, result["response"])
    print(f"\n📝 Query: {query}")
    print(f"🎯 Response: {result['response'][:150]}...")
    
    print(f"\n📊 Quality Metrics:")
    for metric, score in quality_metrics.items():
        print(f"  {metric}: {score:.2f}")
    
    # Weave native scorer
    weave_scores = WeaveScorers.comprehensive_scorer(query, result)
    print(f"\n🔬 Weave Native Scores:")
    for metric, score in weave_scores.items():
        if isinstance(score, (int, float)):
            print(f"  {metric}: {score:.2f}")
    
    return quality_metrics, weave_scores

@weave.op()
def demonstrate_monitors():
    """Requirement 2c: Monitors - track quality, error rate, performance"""
    print("\n📈 DEMONSTRATING MONITORS")
    print("=" * 50)
    
    dashboard = MonitoringDashboard()
    agent = WeaveAgent(use_mock=not bool(os.getenv("OPENAI_API_KEY")))
    
    # Generate some interactions for monitoring
    test_queries = [
        "Calculate 100 / 5",
        "Search for Python tutorials", 
        "What's the weather like?",
        "Invalid query with no clear intent"
    ]
    
    for query in test_queries:
        result = agent.process(query)
        dashboard.record_agent_interaction(result)
    
    # Get monitoring summary
    summary = dashboard.get_dashboard_summary()
    print(f"\n📊 Monitoring Summary:")
    
    if summary.get("performance", {}).get("status") != "no_data":
        perf = summary["performance"]
        print(f"  Average Response Time: {perf['avg_response_time']:.2f}s")
        print(f"  Total Interactions: {perf['total_interactions']}")
    
    if summary.get("errors", {}).get("status") != "no_data":
        errors = summary["errors"]
        print(f"  Success Rate: {errors['success_rate']:.2%}")
        print(f"  Error Count: {errors['error_count']}")
    
    return summary

@weave.op()
def demonstrate_multi_agent():
    """Extra Credit: Multi-agent workflow with Weave integration"""
    print("\n🤖 DEMONSTRATING MULTI-AGENT WORKFLOW")
    print("=" * 50)
    
    workflow = MultiAgentWorkflow(use_mock=not bool(os.getenv("OPENAI_API_KEY")))
    
    # Complex query requiring multiple specialists
    complex_query = "Research the latest developments in quantum computing and write a technical summary with business implications"
    
    print(f"📝 Complex Query: {complex_query}")
    result = workflow.run(complex_query)
    
    print(f"\n🎯 Final Response: {result['final_response'][:200]}...")
    print(f"🤖 Agents Used: {', '.join(result['agents_used'])}")
    print(f"🔧 Tools Used: {result.get('tools_used', [])}")
    print(f"⚡ Total Processing Time: {result['processing_time']:.2f}s")
    
    # Show specialist contributions
    print(f"\n👥 Specialist Contributions:")
    for agent_name, agent_result in result['specialist_results'].items():
        print(f"  {agent_name}: {agent_result['response'][:100]}...")
    
    return result

def main():
    """Main demo function meeting all PDF requirements"""
    print("🚀 W&B WEAVE AGENT - FDE TECHNICAL DEMO")
    print("=" * 60)
    print("Meeting PDF Requirements:")
    print("✅ 1. Weave instrumentation in custom agent")
    print("✅ 2a. Tracing - full execution flow capture")
    print("✅ 2b. Evaluations - custom + Weave native scorers")
    print("✅ 2c. Monitors - quality, error rate, performance")
    print("✅ 3. Reproducible setup (this script + README)")
    print("✅ Extra: Multi-agent workflow")
    print("✅ Extra: Custom evaluations/monitors")
    print("✅ Extra: OpenPipe RL integration")
    
    # Setup
    setup_weave()
    
    try:
        # Core Requirements
        tracing_results = demonstrate_tracing()
        evaluation_results = demonstrate_evaluations()
        monitoring_results = demonstrate_monitors()
        
        # Extra Credit
        multi_agent_results = demonstrate_multi_agent()
        
        print(f"\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print(f"📊 Check your W&B Weave dashboard: https://wandb.ai")
        print(f"🔍 Project: fde-technical-demo")
        
        return {
            "tracing": len(tracing_results),
            "evaluations": evaluation_results,
            "monitoring": monitoring_results,
            "multi_agent": multi_agent_results
        }
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        raise

if __name__ == "__main__":
    main()