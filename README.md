# My MCP Server

로컬 파일 관리를 위한 MCP(Model Context Protocol) 서버와 LangChain 에이전트 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 FastMCP를 사용하여 로컬 파일 시스템을 관리하는 MCP 서버를 구축하고, LangChain과 Anthropic Claude를 활용한 AI 에이전트를 통해 자동화된 파일 작업을 수행합니다.

## ✨ 주요 기능

### MCP 서버 (server.py)
- **파일 목록 조회** (`list_files`): 특정 디렉토리의 파일 목록 반환
- **파일 읽기** (`read_file`): 텍스트 파일 내용 읽기
- **파일 작성** (`write_file`): 새 파일 생성 또는 내용 작성
- **마크다운 생성** (`create_markdown_file`): 마크다운 파일 생성 및 작성

### AI 에이전트 (agent.py)
- Claude Sonnet 4.5 모델을 사용한 대화형 에이전트
- MCP 도구와 LangChain 통합
- 자연어 명령으로 파일 작업 자동화
- Cursor 파라미터 호환성 문제 해결을 위한 폴백(fallback) 로직

## 🛠️ 기술 스택

- **Python**: 3.13+
- **FastMCP**: MCP 서버 프레임워크
- **LangChain**: AI 에이전트 오케스트레이션
- **Anthropic Claude**: LLM (Claude Sonnet 4.5)
- **MCP (Model Context Protocol)**: AI와 도구 간 통신 프로토콜

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd my-mcp-server
```

### 2. 의존성 설치
```bash
uv sync
```

또는 pip 사용:
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 Anthropic API 키를 설정합니다:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## 🚀 사용 방법

### MCP 서버 실행
```bash
uv run server.py
```

### AI 에이전트 실행
```bash
uv run agent.py
```

에이전트는 자동으로 MCP 서버에 연결하여 파일 작업을 수행합니다.

## 💡 사용 예시

에이전트에게 다음과 같은 작업을 요청할 수 있습니다:

```python
# agent.py의 예시 실행
result = await agent_executor.ainvoke({
    "input": "이 경로에 있는 코드를 보고 깃헙에 올릴 readme.md 파일을 만들어줘: ."
})
```

에이전트는:
1. 현재 디렉토리의 파일 목록을 조회
2. 주요 코드 파일들을 읽기
3. 내용을 분석하여 README.md 파일 자동 생성

## 🏗️ 프로젝트 구조

```
my-mcp-server/
├── agent.py           # LangChain AI 에이전트
├── server.py          # FastMCP 서버
├── pyproject.toml     # 프로젝트 설정 및 의존성
├── .env               # 환경 변수 (API 키)
├── .gitignore         # Git 무시 파일 목록
└── README.md          # 프로젝트 문서
```

## 🔧 주요 의존성

```toml
fastmcp>=2.14.1
langchain>=1.2.0
langchain-anthropic>=1.3.0
langchain-mcp-adapters>=0.2.1
mcp>=1.25.0
pandas>=2.3.3
requests>=2.32.5
```

## 🐛 문제 해결

### MCP Cursor 파라미터 오류
일부 MCP 서버는 `cursor` 파라미터를 지원하지 않습니다. 이 프로젝트는 자동 폴백 로직을 포함하여 이 문제를 해결합니다:

```python
async def load_tools_with_fallback(session: ClientSession):
    try:
        return await load_mcp_tools(session)
    except McpError as e:
        if "Invalid request parameters" not in str(e):
            raise
        # cursor 없이 재시도
        tools_result = await session.list_tools()
        return [convert_mcp_tool_to_langchain_tool(session, t) 
                for t in tools_result.tools]
```

## 📝 라이선스

이 프로젝트는 자유롭게 사용하실 수 있습니다.

## 🤝 기여

이슈 제기와 풀 리퀘스트를 환영합니다!

---

**Note**: `BASE_DIR` 경로를 본인의 환경에 맞게 `server.py`에서 수정해주세요.