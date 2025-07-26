from fastmcp import Client
import asyncio

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        tools = await client.list_tools()
        for tool in tools:
            print(tool.name)
           

if __name__ == "__main__":
    asyncio.run(main())

