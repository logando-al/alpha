import os
import shutil
import yaml
import subprocess
import sys
import json
import logging
from pathlib import Path
from alpha.utils import get_resource_path

class ProjectInitializer:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = Path(templates_dir)
        self.commands_config = {}
        
        # Load commands.json
        cmd_path = Path(__file__).parent / "commands.json"
        if cmd_path.exists():
            with open(cmd_path) as f:
                self.commands_config = json.load(f)

    def get_available_stacks(self):
        """Returns list of supported stacks."""
        # Defaults from code + config
        defaults = ["django", "fastapi"] + list(self.commands_config.get("stacks", {}).keys())
        
        # Scan templates directory
        if self.templates_dir.exists():
            for item in self.templates_dir.iterdir():
                if item.is_dir() and not item.name.startswith((".", "__")):
                    defaults.append(item.name)
                    
        return sorted(list(set(defaults)))

    def generate_project(self, config):
        """Generates the project structure using CLI commands."""
        raw_name = config.get("project_name")
        stack = config.get("stack")
        
        # Stack-Specific Sanitization
        if stack in ["django", "fastapi"]:
            # Python: snake_case (no hyphens)
            project_name = raw_name.lower().replace(" ", "_").replace("-", "_")
        else:
            # JS/npm: kebab-case (no underscores conventions, but hyphens allowed)
            # Actually weak kebab: replace spaces with hyphens, lower.
            project_name = raw_name.lower().replace(" ", "-").replace("_", "-")
        
        target_dir = Path(config.get("target_dir"))
        use_docker = config.get("use_docker", False)
        ui_framework = config.get("ui_framework")

        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check if stack is in commands.json
            stack_cmd = self.commands_config.get("stacks", {}).get(stack)
            
            project_root = target_dir / project_name
            
            if stack_cmd:
                cmd = stack_cmd["init_command"].format(name=project_name)
                self._run_command(cmd, target_dir)
                
                # Post-Install Hooks (UI Frameworks)
                if ui_framework and ui_framework.lower() == "shadcn":
                    if stack == "nextjs":
                        self._apply_nextjs_shadcn(project_root)
                    elif stack in ["react", "vue"]:
                        # Vite based
                        self._apply_vite_shadcn(project_root)

            else:
                 self._copy_stack_template(stack, project_root)

            # Superpower Framework (before Docker)
            use_superpower = config.get("use_superpower", False)
            if use_superpower:
                self._apply_superpower_framework(project_root)

            # Docker is injected AFTER project creation
            if use_docker:
                self._generate_docker_files(stack, project_root, ui_framework)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {e}")

    def _apply_nextjs_shadcn(self, project_path):
        """Runs npx shadcn init for Next.js."""
        # Standard init with defaults
        cmd = "npx -y shadcn@latest init -d"
        self._run_command(cmd, project_path)

    def _apply_vite_shadcn(self, project_path):
        """Complex setup for Vite + Shadcn."""
        # 1. Install Tailwind & Plugin
        self._run_command("npm install tailwindcss @tailwindcss/vite", project_path)
        
        # 2. Update src/index.css
        index_css = project_path / "src" / "index.css"
        if index_css.exists():
            with open(index_css, "w") as f:
                f.write('@import "tailwindcss";\n')
                
        # 3. Update tsconfig.json
        self._update_json_config(project_path / "tsconfig.json", {
            "compilerOptions": {
                "baseUrl": ".",
                "paths": {"@/*": ["./src/*"]}
            }
        })
        
        # 4. Update tsconfig.app.json (if exists)
        if (project_path / "tsconfig.app.json").exists():
             self._update_json_config(project_path / "tsconfig.app.json", {
                "compilerOptions": {
                    "baseUrl": ".",
                    "paths": {"@/*": ["./src/*"]}
                }
            })

        # 5. Update vite.config.ts
        # This is harder to modify robustly with simple JSON/string matching.
        # We will attempt a naive text injection if pattern matches.
        vite_config = project_path / "vite.config.ts"
        if vite_config.exists():
            content = vite_config.read_text()
            # Inject Usage imports
            if "@tailwindcss/vite" not in content:
                content = 'import tailwindcss from "@tailwindcss/vite"\nimport path from "path"\n' + content
            
            # Inject plugins
            if "plugins: [" in content and "tailwindcss()" not in content:
                 content = content.replace("plugins: [", "plugins: [tailwindcss(), ")
            
            # Inject alias
            if "resolve: {" not in content:
                # Insert resolve before the last closing brace logic (risky) or replace regex
                # Ideally we replace defineConfig({ ... }) content but that's hard.
                # For now, append/insert logic:
                if "defineConfig({" in content:
                    content = content.replace("defineConfig({", 
                        'defineConfig({\n  resolve: {\n    alias: {\n      "@": path.resolve(__dirname, "./src"),\n    },\n  },')
            
            vite_config.write_text(content)

        # 6. Run Init
        self._run_command("npx -y shadcn@latest init -d", project_path)

    def _update_json_config(self, file_path, updates):
        """Helper to recursively update a JSON file."""
        if not file_path.exists():
            return
            
        try:
            with open(file_path, "r") as f:
                # Handle comments in JSON if necessary (standard json lib doesn't).
                # Assuming standard JSON for now.
                data = json.load(f)
                
            # Recursive update helper
            def recursive_merge(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = recursive_merge(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            
            recursive_merge(data, updates)
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            # If JSON parse fails (comments etc), we skip for safety to avoid corrupting
            pass

    def save_stack_config(self, stack_name, config):
        """Saves a stack configuration to commands.json."""
        cmd_path = Path(__file__).parent / "commands.json"
        
        # Load existing
        current_data = {"stacks": {}}
        if cmd_path.exists():
            with open(cmd_path, "r") as f:
                current_data = json.load(f)
        
        # Update
        current_data["stacks"][stack_name] = config
        
        # Save
        with open(cmd_path, "w") as f:
            json.dump(current_data, f, indent=4)
            
        # Refresh memory
        self.commands_config = current_data

    def delete_stack_config(self, stack_name):
        """Deletes a stack configuration from commands.json."""
        cmd_path = Path(__file__).parent / "commands.json"
        
        if not cmd_path.exists():
            return

        with open(cmd_path, "r") as f:
            current_data = json.load(f)
            
        if stack_name in current_data.get("stacks", {}):
            del current_data["stacks"][stack_name]
            
            with open(cmd_path, "w") as f:
                json.dump(current_data, f, indent=4)
                
            # Refresh memory
            self.commands_config = current_data

    def _run_command(self, cmd, cwd):
        """Helper to run shell commands."""
        # Shell=True usually needed for complex commands or Windows
        
        # CROSS-PLATFORM FIX:
        # If running on Linux/Mac, replace Windows venv paths
        if os.name != 'nt':
            cmd = cmd.replace("venv/Scripts/", "venv/bin/")
            cmd = cmd.replace("venv\\Scripts\\", "venv/bin/")
            cmd = cmd.replace("venv/Scripts", "venv/bin") # Just in case
            
        subprocess.run(cmd, cwd=cwd, shell=True, check=True)

    def _copy_stack_template(self, stack, destination):
        # Legacy/Fallback
        template_src = self.templates_dir / stack
        if template_src.exists():
             shutil.copytree(template_src, destination, dirs_exist_ok=True)
        else:
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "README.md").touch()

    def get_post_install_commands(self, stack, ui_framework):
        # ... logic ...
        return []

    def _generate_docker_files(self, stack, destination, ui_framework):
        # ... logic ...
        self._generate_dockerfile(stack, destination)
        self._generate_docker_compose(stack, destination)

    def _generate_dockerfile(self, stack, destination):
        # 1. Try Config First
        stack_config = self.commands_config.get("stacks", {}).get(stack)
        
        if stack_config:
            base = stack_config.get("docker_base", "alpine:latest")
            cmd = stack_config.get("docker_cmd", "echo 'No Launch Command'")
            
            # Basic Template based on Base Image Family
            if "node" in base:
                content = (
                    f"FROM {base}\n"
                    "WORKDIR /app\n"
                    "COPY package*.json .\n"
                    "RUN npm install\n"
                    "COPY . .\n"
                    f"CMD {json.dumps(cmd.split(' '))}" # Naive split, better to use exec form properly or shell form
                )
                # Revert to valid JSON list for CMD
                # Actually, simple shell form CMD "npm run dev" is fine too if we don't care about signals
                content = (
                    f"FROM {base}\n"
                    "WORKDIR /app\n"
                    "COPY package*.json .\n"
                    "RUN npm install\n"
                    "COPY . .\n"
                    f"CMD {cmd.split(' ')}" 
                ).replace("'", '"') # Fix quotes for JSON
                
            elif "python" in base:
                content = (
                    f"FROM {base}\n"
                    "WORKDIR /app\n"
                    "COPY requirements.txt .\n"
                    "RUN pip install --no-cache-dir -r requirements.txt\n"
                    "COPY . .\n"
                    f"CMD {cmd.split(' ')}"
                ).replace("'", '"')
            else:
                 content = f"FROM {base}\nCMD {cmd.split(' ')}".replace("'", '"')
                 
            with open(destination / "Dockerfile", "w") as f:
                f.write(content)
            return

        # Fallback (Should typically not be hit if everything is in commands.json)
        content = "FROM alpine:latest\nCMD [\"echo\", \"Hello World\"]"
        with open(destination / "Dockerfile", "w") as f:
            f.write(content)

    def _generate_docker_compose(self, stack, destination):
        # Try Config
        stack_config = self.commands_config.get("stacks", {}).get(stack)
        port_map = "8000:8000"
        
        if stack_config:
            port_map = stack_config.get("docker_port", port_map)
        
        # Cleanup N/A or empty
        if not port_map or port_map == "N/A":
             # Use a dummy open port or skip
             port_map = "80" 

        compose_data = {
            "version": "3",
            "services": {
                "web": {
                    "image": f"{destination.name.lower()}:latest",
                    "build": ".",
                    "ports": [port_map],
                    "volumes": ["./:/app"],
                    "restart": "always"
                }
            }
        }
        with open(destination / "docker-compose.yml", "w") as f:
            yaml.dump(compose_data, f, default_flow_style=False)

    def _apply_superpower_framework(self, project_path):
        """Copy bundled .agent folder and initialize git with a commit.
        
        This method handles errors gracefully - if anything fails, it logs
        a warning but doesn't fail the project creation.
        """
        try:
            # Locate bundled .agent folder
            bundled_agent = get_resource_path("alpha/superpower_framework/.agent")
            
            if not bundled_agent.exists():
                logging.warning(f"Bundled .agent folder not found at {bundled_agent}")
                return
            
            # Copy to project
            dest_agent = project_path / ".agent"
            shutil.copytree(bundled_agent, dest_agent, dirs_exist_ok=True)
            logging.info(f"Copied .agent framework to {dest_agent}")
            
            # Initialize git
            self._init_git_with_agent(project_path)
            
        except Exception as e:
            logging.warning(f"Superpower Framework setup failed (non-critical): {e}")

    def _init_git_with_agent(self, project_path):
        """Initialize git repo and commit .agent folder.
        
        Skips git init if repo already exists.
        """
        try:
            # Check if git is available
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                check=True
            )
            
            git_dir = project_path / ".git"
            
            # Only init if not already a git repo
            if not git_dir.exists():
                subprocess.run(["git", "init"], cwd=project_path, check=True)
                logging.info(f"Initialized git repository in {project_path}")
            
            # Add and commit .agent
            subprocess.run(["git", "add", ".agent"], cwd=project_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Add Superpowers framework"],
                cwd=project_path,
                check=True
            )
            logging.info("Committed .agent folder to git")
            
        except FileNotFoundError:
            logging.warning("Git not found on system - skipping git initialization")
        except subprocess.CalledProcessError as e:
            logging.warning(f"Git operation failed: {e}")
