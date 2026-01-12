import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import json
from alpha.initializer import ProjectInitializer

@pytest.fixture
def mock_initializer():
    return ProjectInitializer()

def test_project_name_sanitization(mock_initializer):
    """Test that project names are converted to lowercase/hyphenated."""
    # We might need to expose the sanitization method or check generate_project calls
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        config = {
            "project_name": "My Cool Project",
            "target_dir": ".",
            "stack": "nextjs"
        }
        mock_initializer.generate_project(config)
        
        # Check that the command used the sanitized name
        # "my-cool-project"
        calls = mock_run.call_args_list
        # npx create-next-app@latest my-cool-project --yes
        cmd = calls[0][0][0] # first call, first arg
        assert "my-cool-project" in cmd
        assert "My Cool Project" not in cmd

def test_vite_shadcn_hook_logic(mock_initializer, tmp_path):
    """Test the file manipulation logic for Vite + Shadcn."""
    
    # Setup verify separate hook method if we factor it out
    # For TDD, let's assume we implement a method `_apply_vite_shadcn(project_path)`
    
    project_path = tmp_path / "vite-app"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src/index.css").write_text("body { color: red; }")
    (project_path / "tsconfig.json").write_text('{"compilerOptions": {}}')
    (project_path / "tsconfig.app.json").write_text('{"compilerOptions": {}}')
    (project_path / "vite.config.ts").write_text('export default defineConfig({})')
    
    with patch("alpha.initializer.subprocess.run") as mock_run: 
        # Call the private method we intend to write
        mock_initializer._apply_vite_shadcn(project_path)
        
        # 1. Verify index.css
        assert "@import \"tailwindcss\";" in (project_path / "src/index.css").read_text()
        
        # 2. Verify tsconfig.json
        tsconfig = json.loads((project_path / "tsconfig.json").read_text())
        assert tsconfig["compilerOptions"]["baseUrl"] == "."
        assert "@/*" in tsconfig["compilerOptions"]["paths"]
        
        # 3. Verify subprocess calls (install tailwind, init shadcn)
        # npm install tailwindcss @tailwindcss/vite
        install_called = any("tailwindcss" in c[0][0] and "install" in c[0][0] for c in mock_run.call_args_list)
        assert install_called
        
        # npx -y shadcn@latest init
        init_called = any("shadcn@latest" in c[0][0] and "-y" in c[0][0] for c in mock_run.call_args_list)
        assert init_called

def test_nextjs_shadcn_hook(mock_initializer):
    """Test Next.js Shadcn hook execution."""
    with patch("alpha.initializer.subprocess.run") as mock_run:
        config = {
            "project_name": "next-shadcn",
            "target_dir": ".",
            "stack": "nextjs",
            "ui_framework": "shadcn"
        }
        mock_initializer.generate_project(config)
        
        # Verify npx shadcn init was called
        # We expect 2 calls: create-next-app, then shadcn init
        calls = mock_run.call_args_list
        shadcn_called = any("shadcn@latest" in c[0][0] and "init" in c[0][0] and "-y" in c[0][0] for c in calls)
        assert shadcn_called
