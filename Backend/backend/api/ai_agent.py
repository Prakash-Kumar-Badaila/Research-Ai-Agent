# Generated from: main.ipynb
# Converted at: 2026-06-30T15:41:52.837Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, BaseMessage
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
import asyncio
import json

model = ChatOllama(model = 'minimax-m3:cloud')
checkpointer = InMemorySaver()

with open('systemprompt.md', "r") as f:
    systemprompt = f.read()

class ChatState(TypedDict):
    messages  : Annotated[list[BaseMessage], add_messages] 

with open('mcp_servers.json', "r") as f:
    mcp_servers = json.load(f)


client = MultiServerMCPClient(mcp_servers)

tools = None
async def get_tools():
    tools = await client.get_tools()
    
get_tools()

model = model.bind_tools(tools)

def chat_node(state : ChatState):
    response = model.invoke(state['messages'])
    return {'messages' : [response]}

graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_node('tools', ToolNode(tools))

graph.add_edge(START, 'chat_node')
graph.add_conditional_edges('chat_node', tools_condition)
graph.add_edge('tools', 'chat_node')

workflow = graph.compile(checkpointer= checkpointer)
config  = {

    'configurable' :
    {
        'thread_id' : "1"
    }
}

workflow.update_state(
    config,
    {
        "messages": [
            SystemMessage(content=systemprompt)
        ]
    }
)

async def generate_output(msg):
        async for message, metadata in workflow.astream({'messages' : HumanMessage(content = msg)},stream_mode='messages', config= config):
         if message.content:
                if isinstance(message, AIMessage):
                 yield(message.content)