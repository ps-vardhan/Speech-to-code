from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import tempfile
import subprocess
import shlex
from pathlib import Path
import uuid
import json
import time

from browser_client.pipeline import generate_code_from_raw_text

app = FastAPI()

# ==== FRONTEND SERVING SETUP ====

BASE_DIR = os.path.dirname(os.path.dirname(__file__))         # D:\PseudoCode
FRONTEND_DIR = os.path.join(BASE_DIR, "browser_client")       # path to index.html

# Serve static frontend files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Show index.html when user opens "/"
@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ==== API ====

class GenerateRequest(BaseModel):
    text: str


@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    result = generate_code_from_raw_text(req.text)
    return {
        "code": result.get("code", ""),
        "meta": result
    }


# ==== RUNNER CONSTANTS ====

RUNNER_CONFIG = {
    "python": {
        "image": "python:3.11-slim",
        "file_suffix": ".py",
        "cmd": "python /code/{fname}"
    },
    "java": {
        "image": "openjdk:17-slim",
        "file_suffix": ".java",
        "cmd": "/bin/sh -c \"javac /code/{fname} && java -cp /code Main\""
    }
}

DOCKER_BASE_ARGS = [
    "docker", "run",
    "--rm",
    "--network", "none",
    "--pids-limit", "64",
    "--memory", "200m",
    "--cpus", "0.5",
    "--read-only",
    "--volume", "{hostdir}:/code:ro"
]


class RunRequest(BaseModel):
    code: str
    language: str


@app.post("/api/run")
def api_run(req: RunRequest):
    language = req.language.lower()
    if language not in RUNNER_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported language")

    cfg = RUNNER_CONFIG[language]
    unique = uuid.uuid4().hex
    
    # Create temp directory
    with tempfile.TemporaryDirectory(prefix=f"code-run-{unique}-") as tmpdir:
        # Determine filename
        if language == "java":
            fname = "Main" + cfg["file_suffix"]
            # Heuristic: Wrap in public class Main if not present
            if "class " not in req.code:
                # Basic wrapper for snippet execution
                req.code = (
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        " + req.code.replace("\n", "\n        ") + "\n"
                    "    }\n"
                    "}\n"
                )
        else:
            fname = "script" + cfg["file_suffix"]

        file_path = Path(tmpdir) / fname
        file_path.write_text(req.code, encoding="utf-8")

        # Prepare Docker command
        docker_args = [a.format(hostdir=tmpdir) if "{hostdir}" in a else a for a in DOCKER_BASE_ARGS]
        docker_args += [cfg["image"]]
        docker_cmd = cfg["cmd"].format(fname=fname)
        
        full_cmd = docker_args + shlex.split(docker_cmd)
        TIMEOUT = 8

        try:
            start = time.time()
            proc = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=TIMEOUT
            )
            elapsed = time.time() - start

            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exit_code": proc.returncode,
                "elapsed_seconds": round(elapsed, 3)
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {TIMEOUT} seconds.",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Runner error: {e}",
                "exit_code": -1
            }
