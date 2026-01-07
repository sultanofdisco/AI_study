import asyncio
from dotenv import load_dotenv
load_dotenv()


from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from langchain_mcp_adapters.tools import load_mcp_tools, convert_mcp_tool_to_langchain_tool
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.shared.exceptions import McpError


async def load_tools_with_fallback(session: ClientSession):
    """
    1) 기본: langchain_mcp_adapters.load_mcp_tools(session)
       - 내부에서 session.list_tools(cursor=...) 를 호출함
    2) 서버가 cursor 파라미터를 거부하면(Invalid request parameters),
       - session.list_tools() (no-args) 로 tool 목록을 받아서
       - convert_mcp_tool_to_langchain_tool로 수동 변환
    """
    try:
        return await load_mcp_tools(session)
    except McpError as e:
        if "Invalid request parameters" not in str(e):
            raise

        # ✅ cursor/params를 보내지 않는 list_tools()로 우회
        tools_result = await session.list_tools()   # no cursor
        mcp_tool_defs = tools_result.tools

        # MCP tool definition -> LangChain tool 변환
        return [convert_mcp_tool_to_langchain_tool(session, t) for t in mcp_tool_defs]


async def main():
    # 1. Claude LLM 설정
    llm = ChatAnthropic(model="claude-sonnet-4-5")

    # 2. MCP 서버 파라미터 (uv run server.py로 실행)
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "server.py"],
    )

    # 3. MCP Client 연결
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # ✅ 초기화(핸드셰이크)
            await session.initialize()

            # ✅ 여기만 원래 코드에서 “약간” 바뀜 (fallback 추가)
            mcp_tools = await load_tools_with_fallback(session)

            # 4. 프롬프트 설정
            prompt = ChatPromptTemplate.from_messages([
                ("system", "너는 로컬 파일을 관리하는 업무 자동화 에이전트야. "
                           "특정 디렉토리 파일 목록 조회, 텍스트 파일 읽기, 새 마크다운 파일 생성을 할 때만 제공된 MCP 도구를 사용해."),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])

            # 5. 에이전트 생성
            agent = create_tool_calling_agent(llm, mcp_tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=mcp_tools, verbose=True)

            # 6. 시나리오 실행 테스트
            result = await agent_executor.ainvoke({
                "input": "이 경로에 있는 코드를 보고 깃헙에 올릴 readme.md 파일을 만들어줘: ."
            })
            print(result)


if __name__ == "__main__":
    asyncio.run(main())

