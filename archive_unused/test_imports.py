#!/usr/bin/env python3
"""Test script to verify all imports work"""

try:
    import weave
    print("✅ weave imported successfully")
except ImportError as e:
    print(f"❌ weave import failed: {e}")

try:
    import streamlit as st
    print("✅ streamlit imported successfully")
except ImportError as e:
    print(f"❌ streamlit import failed: {e}")

try:
    from agent import WeaveAgent
    print("✅ WeaveAgent imported successfully")
except ImportError as e:
    print(f"❌ WeaveAgent import failed: {e}")

try:
    from rl_training import RLAgent
    print("✅ RLAgent imported successfully")
except ImportError as e:
    print(f"❌ RLAgent import failed: {e}")

print("\n🎯 If all imports work, run: streamlit run streamlit_app.py")