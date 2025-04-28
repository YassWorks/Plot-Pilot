# this file is meant to handle the raw python code
# that the LLM generated
# we must be careful of LLM injections and hallucinations
# a user could send a malicious code and we must not execute it

import docker
import tempfile
from pathlib import Path
import os

EXECUTOR_DIR = Path("/app/executor")
EXECUTOR_DOCKERFILE_PATH = EXECUTOR_DIR
EXECUTOR_CONTEXT_PATH = EXECUTOR_DIR
IMAGE_NAME = "plot-executor:latest"

def handle_code(code: str, file_content: str | None) -> bytes | None:
    """
    Executes the provided Python code in an isolated Docker container.

    Args:
        code: The Python code string to execute.
        file_content: The content of the uploaded data file as a string, or None.

    Returns:
        The generated plot image as bytes, or None if execution fails.
    """
    client = docker.from_env()

    # 1. Build the executor Docker image (if it doesn't exist)
    try:
        print(f"Building Docker image '{IMAGE_NAME}'...")
        client.images.build(
            path=str(EXECUTOR_CONTEXT_PATH),
            dockerfile=str(EXECUTOR_DOCKERFILE_PATH / "executor.Dockerfile"),
            tag=IMAGE_NAME,
            rm=True,  # Remove intermediate containers
            forcerm=True,  # Force remove intermediate containers
        )
        print("Docker image built successfully.")
    except docker.errors.BuildError as e:
        print(f"Error building Docker image: {e}")
        for line in e.build_log:
            if "stream" in line:
                print(line["stream"].strip())
        return None
    except Exception as e:
        print(f"An unexpected error occurred during image build: {e}")
        return None

    # 2. Create temporary directories for input and output
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        code_file = input_dir / "script.py"
        data_file = input_dir / "data.csv"  # Assume CSV for now
        output_image = output_dir / "plot.png"

        # Write code and data to temp files
        code_file.write_text(code)
        if file_content:
            data_file.write_text(file_content)
        else:
            # Create an empty file if no data was uploaded,
            # the executed code needs to handle this case.
            data_file.touch()

        # 3. Run the container
        volumes = {
            str(input_dir): {
                "bind": "/app/input",
                "mode": "ro",
            },  # Mount input read-only
            str(output_dir): {
                "bind": "/app/output",
                "mode": "rw",
            },  # Mount output read-write
        }

        # Command for the container's entrypoint (execute_code.py)
        # It expects: code_path data_path output_path
        command = [
            "/app/input/script.py",
            "/app/input/data.csv",
            "/app/output/plot.png",
        ]

        container = None
        try:
            print("Running container...")
            container = client.containers.run(
                IMAGE_NAME,
                command=command,
                volumes=volumes,
                network_disabled=True,  # Disable network access!
                mem_limit="512m",  # Limit memory
                cpu_quota=50000,
                cpu_period=100000,
                stderr=True,  # Capture stderr
                stdout=True,  # Capture stdout
                detach=False,  # Run in foreground and wait
                remove=True,  # Automatically remove container when done
            )
            # container output is bytes, decode it
            stdout_logs = container.decode("utf-8")
            print("Container stdout:")
            print(stdout_logs)

            # Check if the output image exists
            if output_image.exists():
                print("Plot image generated successfully.")
                return output_image.read_bytes()
            else:
                print("Execution finished, but output image not found.")
                # Check stderr if available (depends on how run was called)
                # stderr_logs = container.logs(stderr=True, stdout=False).decode('utf-8')
                # print("Container stderr:")
                # print(stderr_logs) # This won't work with detach=False, remove=True
                print(
                    "Check execute_code.py logic and generated code for saving issues."
                )
                return None

        except docker.errors.ContainerError as e:
            print(f"Error running container: {e}")
            print("Container logs (stderr):")
            # Access logs directly from the exception if possible, or re-run with detach=True if needed for debugging
            print(e.stderr.decode("utf-8") if e.stderr else "No stderr captured.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during container run: {e}")
            return None
        finally:
            # Ensure container is stopped and removed if something went wrong and detach=True was used
            if container:
               try:
                   container.stop()
                   container.remove()
               except docker.errors.NotFound:
                   pass # Already removed
               except Exception as cleanup_err:
                   print(f"Error during container cleanup: {cleanup_err}")

    return None  # Should not be reached if successful