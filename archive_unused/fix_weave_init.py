#!/usr/bin/env python3
"""
Fix Weave initialization by using correct entity format
"""

import weave
import wandb
from dotenv import load_dotenv

def fix_weave_init():
    print("🔧 Fixing Weave Initialization")
    print("=" * 40)
    
    load_dotenv()
    
    # Get actual W&B user info
    try:
        api = wandb.Api()
        user = api.viewer
        print(f"✅ W&B user: {user.username}")
        
        # Try different project name formats
        project_formats = [
            "fde-technical-interview",
            "chat17447/fde-technical-interview", 
            "weave-agent-demo",
            "chat17447/weave-agent-demo"
        ]
        
        for project_name in project_formats:
            try:
                print(f"\n🔍 Testing: {project_name}")
                weave.init(project_name)
                print(f"✅ SUCCESS with: {project_name}")
                
                # Test basic operation
                @weave.op()
                def test_op(x):
                    return x * 2
                
                result = test_op(5)
                print(f"✅ Test operation: 5 * 2 = {result}")
                return project_name
                
            except Exception as e:
                print(f"❌ Failed: {str(e)[:100]}...")
                continue
        
        print("❌ All project formats failed")
        return None
        
    except Exception as e:
        print(f"❌ W&B API error: {e}")
        return None

if __name__ == "__main__":
    success = fix_weave_init()
    if success:
        print(f"\n🎉 Use this project name: {success}")
    else:
        print("\n❌ Could not initialize Weave")