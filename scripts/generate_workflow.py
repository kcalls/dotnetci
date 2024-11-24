import yaml
import os
from jinja2 import Template
from github import Github

# GitHub repository and token (use GITHUB_TOKEN in CI/CD)
REPO_NAME = os.getenv("GITHUB_REPOSITORY")  # e.g., "user/repo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Paths
CONFIG_FILE = "config.yaml"
WORKFLOW_FILE = ".github/workflows/dynamic-workflow.yml"

# Validate config.yaml
def validate_config(config):
    if "failover_tasks" not in config or not isinstance(config["failover_tasks"], list):
        raise ValueError("Invalid config.yaml: Missing 'failover_tasks' or it's not a list.")
    for task in config["failover_tasks"]:
        if not all(key in task for key in ["Task", "Type", "resource", "payload"]):
            raise ValueError(f"Task {task} is missing mandatory fields.")

# Generate workflow content using Jinja2
def generate_workflow(config):
    workflow_template = """
    name: Dynamic Workflow

    on:
      push:
        branches:
          - main

    jobs:
      failover-tasks:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout repository
            uses: actions/checkout@v3

    {% for task in failover_tasks %}
          - name: Run Task {{ task.Task }}: {{ task.description }}
            uses: ./github/workflows/{{ 'invoke-lambda.yaml' if task.Type == 'invoke-lambda' else 'invoke-step-function.yaml' }}
            with:
              resource: {{ task.resource }}
              payload: {{ task.payload }}
    {% endfor %}
    """
    template = Template(workflow_template)
    return template.render(failover_tasks=config["failover_tasks"])

# Write workflow file
def write_workflow(content):
    os.makedirs(os.path.dirname(WORKFLOW_FILE), exist_ok=True)
    with open(WORKFLOW_FILE, "w") as file:
        file.write(content)

# Commit and push to GitHub
def push_to_github(file_path):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    with open(file_path, "r") as file:
        content = file.read()

    try:
        workflow_file = repo.get_contents(WORKFLOW_FILE)
        repo.update_file(
            workflow_file.path,
            "Update dynamic workflow",
            content,
            workflow_file.sha,
            branch="main",
        )
    except Exception:
        repo.create_file(
            WORKFLOW_FILE,
            "Create dynamic workflow",
            content,
            branch="main",
        )

# Main function
def main():
    # Step 1: Parse config.yaml
    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file)

    # Step 2: Validate config
    validate_config(config)

    # Step 3: Generate workflow content
    workflow_content = generate_workflow(config)

    # Step 4: Write workflow file
    write_workflow(workflow_content)

    # Step 5: Push to GitHub
    push_to_github(WORKFLOW_FILE)

if __name__ == "__main__":
    main()
