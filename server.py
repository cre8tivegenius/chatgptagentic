import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from mcp import McpError
from mcp.types import ErrorData

WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/workspace")).resolve()
EXPECTED = os.environ.get("MCP_BEARER_TOKEN", "").strip()

if not EXPECTED:
    raise RuntimeError("MCP_BEARER_TOKEN is not set. Add it as a Hugging Face Space Secret.")

def _auth_ok() -> bool:
    headers = get_http_headers()
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    return auth == f"Bearer {EXPECTED}"

class BearerAuthMiddleware(Middleware):
    async def on_initialize(self, context: MiddlewareContext, call_next):
        if not _auth_ok():
            raise McpError(ErrorData(code=-32001, message="Unauthorized"))
        await call_next(context)

    async def on_request(self, context: MiddlewareContext, call_next):
        if not _auth_ok():
            raise McpError(ErrorData(code=-32001, message="Unauthorized"))
        return await call_next(context)

mcp = FastMCP(name="BMAD Devbox MCP")
mcp.add_middleware(BearerAuthMiddleware())

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
    if WORKSPACE_ROOT.exists():
        shutil.rmtree(WORKSPACE_ROOT)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    return f"Workspace reset at {WORKSPACE_ROOT}"

@mcp.tool
def git_clone(repo_url: str, dest: str = "repo", branch: str = "main") -> str:
    dest_path = _safe_path(dest)
    if dest_path.exists():
        raise ValueError(f"Destination already exists: {dest_path}")
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    return _run(["git", "clone", "--branch", branch, "--depth", "1", repo_url, str(dest_path)])

@mcp.tool
def read_text(path: str, max_bytes: int = 200_000) -> str:
    p = _safe_path(path)
    data = p.read_bytes()
    if len(data) > max_bytes:
        raise ValueError(f"File too large ({len(data)} bytes).")
    return data.decode("utf-8", errors="replace")

@mcp.tool
def write_text(path: str, content: str) -> str:
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {p}"

@mcp.tool
def run_tests(cwd: str = "repo") -> str:
    d = _safe_path(cwd)
    return _run(["npm", "test"], cwd=d)

@mcp.tool
def bmad_flatten(input_dir: str = "repo", output_file: str = "flattened-codebase.xml") -> str:
    in_dir = _safe_path(input_dir)
    out_path = _safe_path(output_file)
    out = _run(
        ["npx", "bmad-method", "flatten", "--input", str(in_dir), "--output", str(out_path)],
        cwd=in_dir,
    )
    return out + f"\n\nOutput file: {out_path}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    mcp.run(transport="http", host="0.0.0.0", port=port, path="/mcp")
