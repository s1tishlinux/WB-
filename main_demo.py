#!/usr/bin/env python3
"""
Main Demo Script for Production Multi-Agent System
LangGraph + MCP + Weave + WandB Integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
import weave
import wandb

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_multi_agent import create_production_multi_agent
import json
import time

async def main():
    """Main demo function"""
    
    print("🚀 Production Multi-Agent System Demo")
    print("=" * 50)
    
    # Configuration
    USE_MOCK = not bool(os.getenv('OPENAI_API_KEY'))
    PROJECT_NAME = "multi-agent-demo"
    
    if USE_MOCK:
        print("⚠️  Running in MOCK mode (set OPENAI_API_KEY for production)")
    else:
        print("✅ Running in PRODUCTION mode with real APIs")
    
    print(f"📊 Project: {PROJECT_NAME}")
    print(f"🔧 Weave + WandB tracking enabled")
    print()
    
    # Initialize the multi-agent system
    try:
        agent_system = create_production_multi_agent(
            use_mock=USE_MOCK,
            project_name=PROJECT_NAME
        )
        print("✅ Multi-agent system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return
    
    # Demo queries showcasing different capabilities
    demo_queries = [
        {
            "query": "Calculate 25 * 17 + 100",
            "description": "Mathematical calculation using MCP calculator tool"
        },
        {
            "query": "What's the weather like in San Francisco?",
            "description": "Weather information using MCP weather tool"
        },
        {
            "query": "What time is it?",
            "description": "Time information using MCP time tool"
        },
        {
            "query": "Research the benefits of renewable energy",
            "description": "Research task using research specialist agent"
        },
        {
            "query": "Analyze the market trends for electric vehicles and write a summary",
            "description": "Complex multi-agent task (research + analysis + writing)"
        }
    ]
    
    print("🧪 Running Demo Queries...")
    print("-" * 30)
    
    results = []
    
    for i, demo in enumerate(demo_queries, 1):
        query = demo["query"]
        description = demo["description"]
        
        print(f"\n📝 Demo {i}: {description}")
        print(f"Query: {query}")
        print("Processing...", end="", flush=True)
        
        start_time = time.time()
        
        try:
            # Process the query
            result = agent_system.process_query(query)
            
            processing_time = time.time() - start_time
            print(f" ✅ ({processing_time:.2f}s)")
            
            # Display results
            print(f"🤖 Agents Used: {', '.join(result.get('agents_used', []))}")
            if result.get('tools_used'):
                print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
            
            print(f"💬 Response: {result['final_response'][:150]}...")
            
            # Store result for summary
            results.append({
                "query": query,
                "processing_time": result['processing_time'],
                "agents_used": result.get('agents_used', []),
                "tools_used": result.get('tools_used', []),
                "success": True
            })
            
        except Exception as e:
            print(f" ❌ Error: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "success": False
            })
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    # Display session summary
    print("\n" + "=" * 50)
    print("📊 Session Summary")
    print("=" * 50)
    
    session_stats = agent_system.get_session_stats()
    
    print(f"Total Queries: {session_stats['total_queries']}")
    print(f"Total Processing Time: {session_stats['total_processing_time']:.2f}s")
    print(f"Average Processing Time: {session_stats['total_processing_time']/max(session_stats['total_queries'], 1):.2f}s")
    print(f"Errors: {session_stats['errors']}")
    
    if session_stats['agents_used']:
        print(f"Agents Used: {dict(session_stats['agents_used'])}")
    
    if session_stats['tools_used']:
        print(f"Tools Used: {dict(session_stats['tools_used'])}")
    
    print(f"WandB Run ID: {session_stats['wandb_run_id']}")
    
    # MCP Tool Statistics
    mcp_stats = session_stats.get('mcp_stats', {})
    if mcp_stats:
        print("\n🔧 MCP Tool Statistics:")
        for tool_name, stats in mcp_stats.items():
            print(f"  {tool_name}: {stats['calls']} calls, {stats['success_rate']:.2%} success rate")
    
    # Display tracking URLs
    print("\n🔗 Tracking & Monitoring:")
    print(f"WandB Dashboard: https://wandb.ai/{os.getenv('WANDB_ENTITY', 'your-entity')}/{PROJECT_NAME}")
    print(f"Weave Dashboard: Check your Weave project for detailed traces")
    
    # Cleanup
    agent_system.close()
    print("\n✅ Demo completed successfully!")

def run_interactive_mode():
    """Run interactive mode for custom queries"""
    print("\n🎮 Interactive Mode")
    print("Enter your queries (type 'quit' to exit):")
    
    agent_system = create_production_multi_agent(
        use_mock=not bool(os.getenv('OPENAI_API_KEY')),
        project_name="multi-agent-interactive"
    )
    
    try:
        while True:
            query = input("\n> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print("Processing...", end="", flush=True)
            
            try:
                result = agent_system.process_query(query)
                print(f" ✅ ({result['processing_time']:.2f}s)")
                print(f"Response: {result['final_response']}")
                
                if result.get('agents_used'):
                    print(f"Agents: {', '.join(result['agents_used'])}")
                if result.get('tools_used'):
                    print(f"Tools: {', '.join(result['tools_used'])}")
                    
            except Exception as e:
                print(f" ❌ Error: {e}")
    
    finally:
        agent_system.close()
        print("Interactive session ended.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent System Demo")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--mock", action="store_true", help="Force mock mode")
    
    args = parser.parse_args()
    
    if args.mock:
        os.environ.pop('OPENAI_API_KEY', None)
    
    if args.interactive:
        run_interactive_mode()
    else:
        asyncio.run(main())