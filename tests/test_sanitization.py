import pytest
from alpha.initializer import ProjectInitializer
from unittest.mock import patch, MagicMock, ANY

@pytest.fixture
def initializer():
    return ProjectInitializer()

def test_sanitization_python(initializer):
    """Test snake_case for Django/FastAPI."""
    with patch("alpha.initializer.subprocess.run"):
        # Django
        config = {"project_name": "My Cool App", "target_dir": ".", "stack": "django"}
        
        with patch.object(initializer, "_run_command") as mock_run:
            initializer.generate_project(config)
            # Check for sanitized name in command
            # Django init usually involves "startproject <name>"
            # We just check if the sanitized string was used in the formatted command
            call_args = mock_run.call_args[0][0]
            assert "my_cool_app" in call_args
        
        # FastAPI
        config["stack"] = "fastapi"
        config["project_name"] = "Fast-API-Demo"
        
        with patch.object(initializer, "_run_command") as mock_run:
             initializer.generate_project(config)
             call_args = mock_run.call_args[0][0]
             assert "fast_api_demo" in call_args

def test_sanitization_js(initializer):
    """Test kebab-case for JS stacks."""
    with patch("alpha.initializer.subprocess.run"):
        # Next.js
        config = {"project_name": "My_Cool_App", "target_dir": ".", "stack": "nextjs"} 
        # Note: we replace underscores with hyphens for JS preference
        
        with patch.object(initializer, "_run_command") as mock_run:
            initializer.generate_project(config)
            # Check for npx ... my-cool-app
            call_args = mock_run.call_args[0][0]
            assert "my-cool-app" in call_args
