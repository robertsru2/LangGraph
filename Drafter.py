from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

# This is a global variable to hold the conversation history
document_content = ""
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tools: Annotated[Sequence[str], "List of available tools"]
    tool_calls: Annotated[Sequence[str], "List of tool calls made"]
    tool_results: Annotated[Sequence[str], "List of results from tool calls"]
    
@tool
def update(content: str) -> str:
    """Update the document content."""
    global document_content
    document_content = content
    return f"Document updated with content: {content}"

@tool
def save(filename: str) -> str:
    """Save the document content to a file.
    
    Args:
        filename (str): The name of the file to save the content to.
    Returns:
        str: Confirmation message indicating the file has been saved.
    """
    if filename == "":
        filename = "default_document.txt"
    if not filename.endswith(".txt"):
        # Ensure the filename ends with .txt
        filename += ".txt"
    
    global document_content
    try:
        with open(filename, "w") as f:
            f.write(document_content)
        return f"Document saved to {filename}"
    except Exception as e:
        return f"Error saving document: {str(e)}"


tools = [update, save]

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro").bind_tools(tools).bind_tools(tools)

def our_agent(state: AgentState) -> str:
    
    system_prompt = SystemMessage(content=f"""You are Document Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
                                   - If the user wants to update or modify the document, use the `update` tool with the complete updated content.
                                   - If the user wants to save and finish the document, use the `save` tool with the filename.
                                   - If the user asks for help, provide a brief overview of the available tools and their usage.
                                   - If the user asks to exit, respond with a polite farewell message.
                                   - If the user asks to see the current document content, return the content of the document
                                   - Make sure to always show the current document state after each interaction.
                                   - The current document content is: {document_content}
                                   - Always respond in a friendly and helpful manner.
                                  """)      
    
    
    # Send messages to the model  
    # no document content   
    if not state['messages']:
        user_input = "Hello, I'm ready to help you with a document.  What would you like to create?"
        user_message = HumanMessage(content=user_input)      
    else:  # Document content exists
        user_input = input("\nWhat would you like to do with the document? ")   
        print(f"\nUser Input: {user_input}\n")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state['messages']) + [user_message]
    response = model.invoke(all_messages)
    
    print(f"\nLLM Response: {response.content}\n")
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"Tool Calls: {response.tool_calls}\n")
        state['tool_calls'].extend(response.tool_calls)
    if hasattr(response, 'tool_results') and response.tool_results:
        print(f"Tool Results: {response.tool_results}\n")
        state['tool_results'].extend(response.tool_results)
    

def should_continue(state: AgentState) -> str:
    """
    Determine if the agent should continue processing based on the state.
    """
    # Check if the last message is from the AI and contains a specific keyword
    messages = state['messages'] 
    if not messages:
        return "continue"
 
    for message in reversed(messages):
        if (isinstance(message, ToolMessage) and 
            "saved" in message.content.lower() and
            "document" in message.content.lower()):
            print("Document has been saved. Ending conversation.")  
            return "end"

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

def run_document_agent():
    print("\n ==== Document Drafter Agent ====\n")
    state = {"messages": []}

    # Initial prompt
    user_input = input("Hello, I'm ready to help you with a document. What would you like to create?\n> ")
    state["messages"].append(HumanMessage(content=user_input))

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            pretty_print({"messages": step["messages"]})
    print("\n ==== End of Document Drafter Agent ====\n")
    

graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools=tools))
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END,
    },
)
app = graph.compile()

if __name__ == "__main__":
    run_document_agent()
    # Uncomment the line below to run the agent in a loop
    # while True:
    #     run_document_agent()
    #     if input("Do you want to continue? (yes/no): ").strip().