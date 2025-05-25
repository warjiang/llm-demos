from dotenv import load_dotenv
from mymcpclient import MyMCPClient

import os
import asyncio


load_dotenv()


async def main():
    my_mcp_client = MyMCPClient(
        base_url=os.environ.get("BASE_URL"),
        api_key=os.environ.get("API_KEY"),
        model=os.environ.get("MODEL")
    )
    try:
        """
        await my_mcp_client.connect_to_stdio_server(
            'karmada-mcp-server',
            '/Users/dingwenjiang/workspace/codereview/karmada-mcp-server/_output/bin/darwin/arm64/karmada-mcp-server',
            [
                "stdio",
                "--karmada-kubeconfig=/Users/dingwenjiang/.kube/karmada.config",
                "--karmada-context=karmada-apiserver",
                "--skip-karmada-apiserver-tls-verify"
            ]
        )
        """
        """
        await my_mcp_client.connect_to_sse_server("amap-mcp-server", f"https://mcp.amap.com/sse?key={os.environ.get('AMAP_KEY')}")
        """
        # get current folder according to buildin variable `__file__`
        current_dir = os.path.dirname(os.path.abspath(__file__))
        await my_mcp_client.mcp_json_config(os.path.join(current_dir, "mcp-server.json"))
        await my_mcp_client.chat_loop()
    finally:
        await my_mcp_client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
