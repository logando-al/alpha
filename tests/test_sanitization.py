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
        
        # Monkey patch _init_django to assert
        initializer._init_django = MagicMock()
        initializer.generate_project(config)
        initializer._init_django.assert_called_with(ANY, "my_cool_app")
        
        # FastAPI
        config["stack"] = "fastapi"
        config["project_name"] = "Fast-API-Demo"
        initializer._init_fastapi = MagicMock()
        initializer.generate_project(config)
        initializer._init_fastapi.assert_called_with(ANY, "fast_api_demo")

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
