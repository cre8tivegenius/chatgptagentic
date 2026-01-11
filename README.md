import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/workspace")).resolve()
TOKEN = os.environ.get("MCP_BEARER_TOKEN", "").strip()

mcp = FastMCP(name="BMAD Devbox MCP")

def _safe_path(rel: str) -> Path:
    if not rel or rel.strip() == "":
        raise ValueError("Path is required.")
    p = Path(rel)
    if p.is_absolute():
        raise ValueError("Absolute paths are not allowed.")
    full = (WORKSPACE_ROOT / p).resolve()
    if WORKSPACE_ROOT not in full.parents and full != WORKSPACE_ROOT:
        raise ValueError("Path escapes workspace.")
    return full

def _run(cmd: list[str], cwd: Optional[Path] = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.stdout

@mcp.tool
def workspace_reset() -> str:
    """Delete and recreate the workspace directory."""
    if WORKSPACE_ROOT.exists():
        shutil.rmtree(WORKSPACE_ROOT)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    return f"Workspace reset at {WORKSPACE_ROOT}"

@mcp.tool
def git_clone(repo_url: str, dest: str = "repo", branch: str = "main") -> str:
    """Clone a git repo into the workspace."""
    dest_path = _safe_path(dest)
    if dest_path.exists():
        raise ValueError(f"Destination already exists: {dest_path}")
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    return _run(["git", "clone", "--branch", branch, "--depth", "1", repo_url, str(dest_path)])

@mcp.tool
def read_text(path: str, max_bytes: int = 200_000) -> str:
    """Read a text file (size-limited)."""
    p = _safe_path(path)
    data = p.read_bytes()
    if len(data) > max_bytes:
        raise ValueError(f"File too large ({len(data)} bytes).")
    return data.decode("utf-8", errors="replace")

@mcp.tool
def write_text(path: str, content: str) -> str:
    """Write a text file (creates parent dirs)."""
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {p}"

@mcp.tool
def run_tests(cwd: str = "repo") -> str:
    """Run tests. Default: npm test (customize for your stack)."""
    d = _safe_path(cwd)
    return _run(["npm", "test"], cwd=d)

@mcp.tool
def bmad_flatten(input_dir: str = "repo", output_file: str = "flattened-codebase.xml") -> str:
    """
    Run BMAD's flattener:
      npx bmad-method flatten --input ... --output ...
    """
    in_dir = _safe_path(input_dir)
    out_path = _safe_path(output_file)
    out = _run(
        ["npx", "bmad-method", "flatten", "--input", str(in_dir), "--output", str(out_path)],
        cwd=in_dir,
    )
    return out + f"\n\nOutput file: {out_path}"

if __name__ == "__main__":
    # Hugging Face Docker Spaces commonly expose app_port 7860.  [oai_citation:4‡Hugging Face](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=7860,
        path="/mcp",
        # If your FastMCP version supports built-in auth, use it.
        # Otherwise, rely on a private Space or a fronting gateway.
    )