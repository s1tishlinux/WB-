#!/usr/bin/env python3
"""
W&B Weave Agent Project - Main Runner
Demonstrates agent capabilities with comprehensive Weave integration
"""

import weave
import os
from dotenv import load_dotenv
from agent import WeaveAgent
from evaluation.evaluators import ResponseQualityEvaluator, ToolUsageEvaluator
from evaluation.scorers import WeaveScorers
from monitoring.monitors import MonitoringDashboard
from multi_agent.workflow import MultiAgentWorkflow

# Load environment variables
load_dotenv()

def setup_weave():
    """Initialize Weave with W&B project"""
    weave.init("weave-agent-project")
    print(" Weave initialized successfully")

@weave.op()
def run_single_agent_demo():
    """Demonstrate single agent capabilities"""
    print("\n🤖 Single Agent Demo")
    print("=" * 50)
    
    # Initialize agent and monitoring
    agent = WeaveAgent()
    dashboard = MonitoringDashboard()
    quality_evaluator = ResponseQualityEvaluator()
    tool_evaluator = ToolUsageEvaluator()
    
    # Test queries
    test_queries = [
        "What's the weather like in San Francisco?",
        "Calculate the area of a circle with radius 5",
        "Search for information about machine learning",
        "What time is it now?"
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\n Query: {query}")
        
        # Process with agent
        result = agent.process(query)
        results.append(result)
        
        # Evaluate response quality
        quality_metrics = quality_evaluator.evaluate(query, result["response"])
        
        # Evaluate tool usage
        tool_metrics = tool_evaluator.evaluate(
            query, 
            result["selected_tools"], 
            result["tool_results"],
            agent.tools.list_tools()
        )
        
        # Record in monitoring dashboard
        dashboard.record_agent_interaction(result, quality_metrics)
        
        # Display results
        print(f"🎯 Response: {result['response'][:100]}...")
        print(f"⚡ Processing Time: {result['processing_time']:.2f}s")
        print(f"🔧 Tools Used: {result['selected_tools']}")
        print(f" Quality Score: {sum(quality_metrics.values())/len(quality_metrics):.2f}")
    
    # Display monitoring summary
    print("\n Monitoring Summary")
    print("=" * 30)
    summary = dashboard.get_dashboard_summary()
    
    if summary.get("performance", {}).get("status") != "no_data":
        print(f"Average Response Time: {summary['performance']['avg_response_time']:.2f}s")
        print(f"Success Rate: {summary['errors']['success_rate']:.2%}")
    
    if summary.get("quality", {}).get("status") != "no_data":
        print(f"Average Quality: {summary['quality']['avg_quality']:.2f}")
        print(f"Quality Trend: {summary['quality']['quality_trend']}")
    
    print(f"Total Queries Processed: {len(results)}")
    print(f"Tools Used: {set([t for r in results for t in r['selected_tools']])}")
    
    return results

@weave.op()
def run_multi_agent_demo_disabled():
    """Demonstrate multi-agent workflow"""
    print("\n Multi-Agent Demo")
    print("=" * 50)
    
    # Initialize multi-agent workflow
    workflow = MultiAgentWorkflow()
    
    # Test complex query requiring multiple specialists
    complex_query = "Analyze the current state of artificial intelligence, research recent developments, and write a technical summary with recommendations for businesses."
    
    print(f" Complex Query: {complex_query}")
    
    # Execute workflow
    result = workflow.execute_workflow(complex_query)
    
    # Display results
    print(f"\n Final Response: {result['final_response'][:200]}...")
    print(f"⚡ Total Processing Time: {result['processing_time']:.2f}s")
    print(f" Agents Used: {', '.join(result['agents_used'])}")
    
    # Show specialist contributions
    print("\n Specialist Contributions:")
    for agent_name, agent_result in result['specialist_results'].items():
        print(f"  {agent_name}: {agent_result['response'][:100]}...")
    
    return result

@weave.op()
def run_evaluation_demo():
    """Demonstrate comprehensive evaluation"""
    print("\n Evaluation Demo")
    print("=" * 50)
    
    # Create test data
    agent = WeaveAgent()
    test_query = "Explain quantum computing in simple terms"
    result = agent.process(test_query)
    
    # Run comprehensive scoring
    scores = WeaveScorers.comprehensive_scorer(test_query, result)
    
    print(f"Query: {test_query}")
    print(f"Response: {result['response'][:150]}...")
    print("\n Evaluation Scores:")
    
    for metric, score in scores.items():
        if isinstance(score, dict):
            print(f"  {metric}:")
            for sub_metric, sub_score in score.items():
                if isinstance(sub_score, (int, float)):
                    print(f"    {sub_metric}: {sub_score:.2f}")
        elif isinstance(score, (int, float)):
            print(f"  {metric}: {score:.2f}")
    
    return scores

def main():
    """Main execution function"""
    print(" W&B Weave Agent Project")
    print("=" * 60)
    
    # Setup
    setup_weave()
    
    try:
        # Run demonstrations
        single_results = run_single_agent_demo()
        # multi_results = run_multi_agent_demo()
        evaluation_results = run_evaluation_demo()
        
        print("\n All demonstrations completed successfully!")
        print("\n Summary:")
        print(f"  - Single agent interactions: {len(single_results)}")
        # print(f"  - Multi-agent workflow executed: 1")
        print(f"  - Evaluation metrics calculated: {len(evaluation_results)}")
        print("\n Check your W&B dashboard for detailed traces and metrics!")
        
    except Exception as e:
        print(f" Error during execution: {e}")
        raise

if __name__ == "__main__":
    main()