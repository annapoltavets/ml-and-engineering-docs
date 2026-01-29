"""
MCP agent using OpenAI GPT + LangChain.

- Reads MCP servers from ./browser_mcp.json
- Commands: 'clear' to wipe memory, 'quit'/'exit' to leave
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import streamlit as st

async def run_chat() -> None:
    client = MCPClient.from_config_file("browser_mcp.json")
    
    load_dotenv()
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # or "gpt-4" for better performance
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,
    )

    print("===== MCP Chat (OpenAI GPT) =====")
    print("Type 'quit' or 'exit' to leave; 'clear' to wipe memory.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            agent.clear_conversation_history()
            print("[Conversation history cleared]")
            continue

        response = await agent.run(user_input)
        print("Agent:", response)

    if hasattr(client, "close_all_sessions"):
        await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_chat())
