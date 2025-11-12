#!/usr/bin/env python3
"""
Fix W&B entity issue by using default entity or creating project without entity
"""

import weave
import wandb
from dotenv import load_dotenv

load_dotenv()

def test_weave_without_entity():
    """Test Weave with just project name"""
    try:
        print("🔍 Testing Weave with project name only...")
        weave.init('fde-technical-interview')
        print("✅ Weave initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_wandb_entity():
    """Check what entity W&B is using"""
    try:
        print("🔍 Checking W&B entity...")
        api = wandb.Api()
        user = api.viewer
        print(f"✅ W&B user: {user}")
        print(f"✅ Default entity: {user}")
        return str(user)
    except Exception as e:
        print(f"❌ W&B API error: {e}")
        return None

def main():
    print("🔧 Fixing W&B Entity Issue")
    print("=" * 40)
    
    # Check W&B entity
    entity = test_wandb_entity()
    
    if entity:
        print(f"\n📝 Update your .env file:")
        print(f"WANDB_ENTITY={entity}")
    
    # Test Weave
    test_weave_without_entity()

if __name__ == "__main__":
    main()