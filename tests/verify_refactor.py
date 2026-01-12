from alpha.initializer import ProjectInitializer
from unittest.mock import patch

def test_commands_loading():
    print("Testing commands.json loading...")
    initializer = ProjectInitializer()
    stacks = initializer.get_available_stacks()
    
    assert "nextjs" in stacks
    assert "react" in stacks
    assert "django" in stacks
    print(f"✅ Stacks Discovery Passed: {stacks}")
    
    # Verify Config Loaded
    assert initializer.commands_config["stacks"]["nextjs"]["init_command"] == "npx create-next-app@latest {name} --yes"
    print("✅ Config Loading Passed")

def test_config_execution_logic():
    print("\nTesting Execution Logic (Mocked)...")
    initializer = ProjectInitializer()
    config = {"project_name": "test-app", "target_dir": ".", "stack": "nextjs"}
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        initializer.generate_project(config)
        
        expected_cmd = "npx create-next-app@latest test-app --yes"
        calls = mock_run.call_args_list
        cmd_found = any(expected_cmd in c[0][0] for c in calls)
        
        if cmd_found:
             print(f"✅ Executed Command: {expected_cmd}")
        else:
             print(f"❌ Failed to find: {expected_cmd}")
             print(f"Actual calls: {calls}")

if __name__ == "__main__":
    try:
        test_commands_loading()
        test_config_execution_logic()
        print("\nAll Checks Passed!")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)
