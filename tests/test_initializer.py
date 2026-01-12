import pytest
import os
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path
from alpha.initializer import ProjectInitializer

@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture to provide a temporary directory for project generation."""
    return tmp_path / "TestProject"

@pytest.fixture
def mock_templates_dir(tmp_path):
    """Creates a mock templates directory with dummy stacks."""
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "django").mkdir()
    (tpl_dir / "react").mkdir()
    (tpl_dir / "fastapi").mkdir()
    (tpl_dir / "go-gin").mkdir()
    return tpl_dir

def test_dynamic_stack_discovery(mock_templates_dir):
    """Verify that stacks are discovered dynamically from a templates directory."""
    initializer = ProjectInitializer(templates_dir=mock_templates_dir)
    stacks = initializer.get_available_stacks()
    
    assert "django" in stacks
    assert "react" in stacks
    assert "go-gin" in stacks

def test_docker_generation_django(temp_project_dir, mock_templates_dir):
    """Test Dockerfile generation for a Django project."""
    initializer = ProjectInitializer(templates_dir=mock_templates_dir)
    
    config = {
        "project_name": "TestProject",
        "target_dir": str(temp_project_dir.parent),
        "stack": "django",
        "use_docker": True,
        "ui_framework": None
    }
    
    initializer.generate_project(config)
    
    # Verify Dockerfile exists and contains Python
    dockerfile = temp_project_dir / "Dockerfile"
    assert dockerfile.exists()
    content = dockerfile.read_text()
    assert "FROM python:3.11-slim" in content
    assert "CMD" in content

def test_synology_docker_compose_compliance(temp_project_dir, mock_templates_dir):
    """Test that generated docker-compose.yml is compliant with Synology NAS."""
    initializer = ProjectInitializer(templates_dir=mock_templates_dir)
    
    config = {
        "project_name": "MyNasApp",
        "target_dir": str(temp_project_dir.parent),
        "stack": "react",
        "use_docker": True,
        "ui_framework": "tailwind"
    }

    initializer.generate_project(config)

    # Corretly pointing to the generated project directory "MyNasApp"
    project_dir = Path(config['target_dir']) / config['project_name']
    compose_file = project_dir / "docker-compose.yml"
    assert compose_file.exists()
    
    with open(compose_file) as f:
        compose_data = yaml.safe_load(f)
        
    # Synology Requirement: Version 3
    assert str(compose_data.get('version', '')).startswith('3')
    
    # Synology Requirement: Services must have keys
    services = compose_data.get('services', {})
    assert 'web' in services
    web_service = services['web']
    
    # Check for keys that might break Synology UI if not handled well
    # (Just verifying we stuck to the 'image' or 'build' standard)
    assert 'image' in web_service or 'build' in web_service

def test_ui_framework_injection_react(mock_templates_dir):
    """Test that selecting Tailwind adds it to the post-install commands."""
    initializer = ProjectInitializer(templates_dir=mock_templates_dir)
    
    commands = initializer.get_post_install_commands("react", "tailwind")
    # Verify strict string match or partial match
    assert any("npm install -D tailwindcss" in cmd for cmd in commands)

