from typing import Optional
from contextlib import AsyncExitStack

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from lxml import etree
import re, os, json


class MyMCPClient:
    def __init__(
            self,
            base_url: str | None,
            api_key: str,
            model: str
    ):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.messages = []
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # get current folder according to buildin variable `__file__`
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f"{script_dir}/prompt.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

        self.sse = None
        self.stdio = None
        self.write = None
        self.sessions = {}

    async def connect_to_stdio_server(
            self,
            mcp_name: str,
            command: str,
            args: list[str],
            env: dict[str, str] | None = None
    ):
        """
        Connect to an MCP server
        Args:
            :param mcp_name:
            :param command:
            :param args:
            :param env:
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()
        # 将MCP信息添加到system_prompt
        response = await self.session.list_tools()
        # available_tools = [
        #     '##' + mcp_name + '\n### Available Tools\n- ' + tool.name + "\n" + tool.description + "\n" + json.dumps(
        #         tool.inputSchema) for tool in response.tools
        # ]
        available_tools = [
            f"## {mcp_name}",
            "### Available Tools",
            *[
                f"- {tool.name}\n  {tool.description}\n  {json.dumps(tool.inputSchema)}"
                for tool in response.tools
            ]
        ]
        self.system_prompt = self.system_prompt.replace(
            "<$MCP_INFO$>",
            "\n".join(available_tools) + "\n<$MCP_INFO$>"
        )
        tools = response.tools
        print(f"Successfully connected to {mcp_name} server with tools:", [tool.name for tool in tools])

    async def connect_to_sse_server(self, mcp_name, server_url: str):
        """
        Connect to an MCP server

       Args:
           :param mcp_name:
           :param server_url:
       """
        stdio_transport = await self.exit_stack.enter_async_context(sse_client(server_url))
        self.sse, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.sse, self.write))
        self.sessions[mcp_name] = self.session

        await self.session.initialize()
        # List available tools
        response = await self.session.list_tools()
        available_tools = [
            f"## {mcp_name}",
            "### Available Tools",
            *[
                f"- {tool.name}\n  {tool.description}\n  {json.dumps(tool.inputSchema)}"
                for tool in response.tools
            ]
        ]
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools) + "\n<$MCP_INFO$>\n")
        tools = response.tools
        print(f"Successfully connected to {mcp_name} server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        self.messages.append(
            {
                "role": "system",
                "content": self.system_prompt
            }
        )
        self.messages.append(
            {
                "role": "user",
                "content": query
            }
        )

        # Initial Claude API call
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=self.messages,
        )

        # Process response and handle tool calls
        final_text = []
        content = response.choices[0].message.content
        if '<use_mcp_tool>' not in content:
            final_text.append(content)
        else:
            # 解析tool_string
            server_name, tool_name, tool_args = self.parse_tool_string(content)

            # 执行工具调用
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"[Calling tool {tool_name} with args {tool_args}]")
            print("-" * 40)
            print("Server:", server_name)
            print("Tool:", tool_name)
            print("Args:", tool_args)
            print("-" * 40)
            print("Result:", result.content[0].text)
            print("-" * 40)
            self.messages.append({
                "role": "assistant",
                "content": content
            })
            self.messages.append({
                "role": "user",
                "content": f"[Tool {tool_name} \n returned: {result}]"
            })

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=self.messages
            )
            final_text.append(response.choices[0].message.content)
        return "\n".join(final_text)

    @staticmethod
    def parse_tool_string(tool_string: str) -> tuple[str, str, dict]:
        """
        解析大模型工具调用返回的字符串
        tool_string:
        '
        我将会查询控制面上的所有 namespace。请稍等。
        <use_mcp_tool>
            <server_name>karmada-mcp-server</server_name>
            <tool_name>list_namespace</tool_name>
            <arguments>{}</arguments>
        </use_mcp_tool>
        '
        """
        tool_string = re.findall("(<use_mcp_tool>.*?</use_mcp_tool>)", tool_string, re.S)[0]
        root = etree.fromstring(tool_string)
        server_name = root.find('server_name').text
        tool_name = root.find('tool_name').text
        try:
            tool_args = json.loads(root.find('arguments').text)
        except json.JSONDecodeError:
            raise ValueError("Invalid tool arguments")
        return server_name, tool_name, tool_args

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        self.messages = []
        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break
                if query.strip() == '':
                    print("Please enter a query.")
                    continue
                response = await self.process_query(query)
                print(response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
