from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tools: Annotated[Sequence[str], "List of available tools"]
    tool_calls: Annotated[Sequence[str], "List of tool calls made"]
    tool_results: Annotated[Sequence[str], "List of results from tool calls"]
    
@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

tools = [add, subtract, multiply]

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro").bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    """
    Call the model with the current state and update the state with the response.
    """
    # Send messages to the model
    system_prompt = SystemMessage(content="You are my AI Assistant, please help me with my tasks.")
    response = model.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

def should_continue(state: AgentState) -> bool:
    """
    Determine if the agent should continue processing based on the state.
    """
    # Check if the last message is from the AI and contains a specific keyword
    last_message = state['messages'][-1] 
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def pretty_print(state):
    """
    Pretty print the agent state/messages:
    1. Human Messages
    2. Tool Calls
    3. Tool Messages
    4. AI Messages
    """
    print("\n--- Conversation Trace ---\n")
    for msg in state['messages']:
        if msg.__class__.__name__ == "HumanMessage":
            print(f"Human: {msg.content}")
        elif msg.__class__.__name__ == "AIMessage":
            # Print tool calls if present
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"Tool Call: {tc['name']}({tc['args']}) [id: {tc.get('id','')}]")
            print(f"AI: {msg.content}")
        elif msg.__class__.__name__ == "ToolMessage":
            print(f"Tool Message: {msg.name} returned {msg.content} [tool_call_id: {msg.tool_call_id}]")
        else:
            print(f"Other ({msg.__class__.__name__}): {msg.content}")
    print("\n-------------------------\n")

graph = StateGraph(AgentState) 
graph.add_node("our_agent", model_call) 

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)
graph.set_entry_point("our_agent")
#graph.add_edge(START, "our_agent")
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)
graph.add_edge("tools", "our_agent")  # Loop back to the model call after tool execution
graph.add_edge("our_agent", END)  # Final state, no further processing
app = graph.compile()

inputs = {"messages": [("user", "Add 34 + 21.  Add 12 + 13. Then subtract 5 from the result of the first addition.")]}
pretty_print(app.invoke(inputs, stream_mode="values"))


