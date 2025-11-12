#!/usr/bin/env python3
"""
Test script for W&B Weave Agent setup
Run this to verify everything is working before the demo
"""

import os
import sys
from dotenv import load_dotenv

def test_basic_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    try:
        import weave
        import openai
        import wandb
        print(f"✅ Weave version: {weave.__version__}")
        print(f"✅ OpenAI imported")
        print(f"✅ W&B imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key missing or invalid")
        return False
    
    print("✅ Environment loaded")
    return True

def test_weave_init():
    """Test Weave initialization"""
    print("\n🔍 Testing Weave initialization...")
    try:
        import weave
        weave.init('fde-technical-interview')
        print("✅ Weave initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Weave init failed: {e}")
        return False

def test_agent():
    """Test basic agent functionality"""
    print("\n🔍 Testing agent...")
    try:
        from agent import WeaveAgent
        agent = WeaveAgent(use_mock=False)
        result = agent.process("What is 2 + 2?")
        print(f"✅ Agent response: {result['response'][:50]}...")
        print(f"✅ Tools used: {result['selected_tools']}")
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 W&B Weave Agent Setup Test")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_environment,
        test_weave_init,
        test_agent
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        else:
            break
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Ready for demo.")
        return True
    else:
        print("❌ Some tests failed. Check configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)