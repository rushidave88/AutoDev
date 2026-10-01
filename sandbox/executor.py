import docker
import os
import tempfile
from typing import Dict, Any

def execute_code(code: str, tests: str) -> Dict[str, Any]:
    """
    Executes generated code and tests in a sandboxed Docker container.
    """
    # Workaround for docker-credential-desktop PATH issue on Windows
    temp_docker_config = tempfile.mkdtemp()
    import json
    with open(os.path.join(temp_docker_config, "config.json"), "w") as f:
        json.dump({"credsStore": ""}, f)
    os.environ["DOCKER_CONFIG"] = temp_docker_config
    
    client = docker.from_env()
    
    # Create a temporary directory to mount as a volume
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "main.py"), "w", encoding="utf-8") as f:
            f.write(code)
            
        with open(os.path.join(temp_dir, "test_main.py"), "w", encoding="utf-8") as f:
            f.write(tests)
            
        try:
            # Build the sandbox image if it doesn't exist
            dockerfile_path = os.path.dirname(__file__)
            image_tag = "autodev-sandbox:latest"
            try:
                client.images.get(image_tag)
            except docker.errors.ImageNotFound:
                print(f"Building {image_tag}...")
                client.images.build(path=dockerfile_path, tag=image_tag)
                
            # Run the container
            container = client.containers.run(
                image_tag,
                command=["pytest", "test_main.py"],
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                working_dir="/app",
                detach=True,
                remove=False
            )
            
            # Wait for the container to finish
            result = container.wait()
            exit_code = result['StatusCode']
            
            # Capture output
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # Clean up
            container.remove()
            
            return {
                "exit_code": exit_code,
                "output": logs,
                "status": "passed" if exit_code == 0 else "failed"
            }
            
        except docker.errors.ContainerError as e:
            return {
                "exit_code": e.exit_status,
                "output": e.stderr.decode('utf-8') if e.stderr else str(e),
                "status": "failed"
            }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return {
                "exit_code": -1,
                "output": f"{str(e)}\nTraceback:\n{tb}",
                "status": "error"
            }

if __name__ == '__main__':
    # Test the executor
    sample_code = "def add(a, b):\n    return a + b\n"
    sample_tests = "from main import add\ndef test_add():\n    assert add(1, 2) == 3\n"
    
    print("Testing Docker Executor...")
    result = execute_code(sample_code, sample_tests)
    print("Sandbox test result:", result)
