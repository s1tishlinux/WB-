#!/usr/bin/env python3
"""
LEARNING STEP 1: Understanding and Testing Tools
Let's see how the tool system works
"""

from dotenv import load_dotenv
load_dotenv()

# Mock weave for learning
class MockWeave:
    @staticmethod
    def op():
        def decorator(func):
            return func
        return decorator

import sys
sys.modules['weave'] = MockWeave()

from agent.tools import ToolRegistry

def learn_tools():
    print("🔧 LEARNING STEP 1: Tool System")
    print("=" * 50)
    
    # Create tool registry
    tools = ToolRegistry()
    
    print("📋 Available Tools:")
    for tool_name in tools.list_tools():
        print(f"  • {tool_name}")
    
    print("\n🧪 Testing Each Tool:")
    
    # Test calculator
    print("\n1️⃣ Calculator Tool:")
    calc_result = tools.execute("calculator", "15 * 23")
    print(f"   Input: 15 * 23")
    print(f"   Output: {calc_result}")
    
    # Test time
    print("\n2️⃣ Time Tool:")
    time_result = tools.execute("time")
    print(f"   Output: {time_result}")
    
    # Test weather (simulated)
    print("\n3️⃣ Weather Tool:")
    weather_result = tools.execute("weather", "San Francisco")
    print(f"   Input: San Francisco")
    print(f"   Output: {weather_result}")
    
    # Test web search (simulated without API key)
    print("\n4️⃣ Web Search Tool:")
    search_result = tools.execute("web_search", "Python tutorials")
    print(f"   Input: Python tutorials")
    print(f"   Output: {search_result}")
    
    # Show tool statistics
    print("\n📊 Tool Usage Statistics:")
    stats = tools.get_tool_stats()
    for tool_name, tool_stats in stats.items():
        print(f"   {tool_name}:")
        print(f"     Usage: {tool_stats['usage_count']}")
        print(f"     Success Rate: {tool_stats['success_rate']:.1%}")

if __name__ == "__main__":
    learn_tools()