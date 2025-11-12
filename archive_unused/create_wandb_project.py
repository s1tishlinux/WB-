#!/usr/bin/env python3
"""
Create W&B project and test Weave initialization
"""

import wandb
import weave
from dotenv import load_dotenv

def create_project():
    print("🔧 Creating W&B Project")
    print("=" * 30)
    
    load_dotenv()
    
    # Initialize a simple W&B run to create the project
    try:
        run = wandb.init(
            project="fde-technical-interview",
            name="setup-test",
            job_type="setup"
        )
        
        # Log a simple metric to create the project
        wandb.log({"setup": 1})
        
        print("✅ W&B project created")
        run.finish()
        
        # Now test Weave
        print("\n🔍 Testing Weave...")
        weave.init("fde-technical-interview")
        
        @weave.op()
        def test_op(x):
            return x * 2
        
        result = test_op(5)
        print(f"✅ Weave working: 5 * 2 = {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_project()
    if success:
        print("\n🎉 Ready for demo!")
    else:
        print("\n❌ Setup failed")