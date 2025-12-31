from fastmcp import FastMCP
import os
from pathlib import Path

mcp = FastMCP("My FastMCP Server")

BASE_DIR = Path("C:\\Users\\user\\OneDrive\\문서").absolute()
BASE_DIR.mkdir(exist_ok=True)

# 2. 도구 정의 (Tools)
# @mcp.tool() 데코레이터가 함수의 Docstring과 타입을 분석해 
# 자동으로 MCP 프로토콜용 JSON Schema를 만들어줍니다.

@mcp.tool()
def list_files(relative_path: str = ".") -> list[str]:
    """특정 디렉토리의 파일 목록을 반환합니다."""
    target_path = (BASE_DIR / relative_path).resolve()
    return os.listdir(target_path)

@mcp.tool()
def read_file(file_path: str) -> str:
    """파일의 내용을 읽어옵니다."""
    target_path = (BASE_DIR / file_path).resolve()
    return target_path.read_text(encoding="utf-8")

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """새 파일을 생성하거나 내용을 작성합니다."""
    target_path = (BASE_DIR / file_path).resolve()
    target_path.write_text(content, encoding="utf-8")
    return f"파일 저장 완료: {file_path}"

# 3. 실행 (Stdio 모드)
if __name__ == "__main__":
    mcp.run()