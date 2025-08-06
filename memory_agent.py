from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage, ToolMessage]]
    tools: List[str]
    tool_calls: List[str]
    tool_results: List[str]
    
#llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_retries=3)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")


def process(state: AgentState) -> AgentState:
    """
    Process the agent state by sending messages to the LLM and updating the state.
    """
    # Prepare the messages for the LLM
    messages = state['messages']
    
    # Send messages to the LLM
    response = llm.invoke(messages)
    
    print(f"LLM Full Response: {response}\n\n")
    # Update the state with the LLM's response
    state['messages'].append(AIMessage(content=response.content))
    print(f"\nI: {response.content}\n")
    print(f"CURRENT STATE: {state['messages']}\n")
    
    return state    

def write_history():
        # Save the conversation history to a file
    with open("conversation_history.txt", "a") as f:
        for message in conversation_history:
            if isinstance(message, HumanMessage):
                f.write(f"You: {message.content}\n")
            elif isinstance(message, AIMessage):
                f.write(f"AI: {message.content}\n")
        f.write("\n")

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)  # Final state, no processing needed
agent = graph.compile()

conversation_history = []

user_input = input("You: ")
while user_input.lower() != "exit":
    # Append the user's message to the conversation history
    conversation_history.append(HumanMessage(content=user_input ))
    #result = agent.invoke({"messages": conversation_history})
    result = agent.invoke({"messages": conversation_history})
    # Append the LLM's response to the conversation history
    conversation_history.append(AIMessage(content=result['messages'][-1].content))
    print(f"AI: {result['messages'][-1].content}")
    user_input = input("You: ")
    

write_history()

