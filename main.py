from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph
from collections import defaultdict
from IPython.display import display, Image


# Define a state schema for StateGraph
class AgentState(TypedDict):
    messages: List[str]= []
    values: List[int]
    operations: List[str]
    name: str
    skills: List[str] = []
    current_step: str
    result: str

def greeting_node(state: AgentState) -> AgentState:
    """
    A simple greeting node that initializes the state with a welcome message.
    """
    state['messages'].append(f"Hello {state['name']}! How can I assist you today?")
    return state

def process_values(state: AgentState) -> AgentState:
    """
    A node that processes a list of values and appends the result to the messages.
    """
    if not state['values']:
        state['messages'].append("No values provided.")
        return state
    operations_message = ''    
    if not state['operations']:
        state['messages'].append("No operations specified.")
        return state
    elif '+' in state['operations']:
        total = sum(state['values'])
        operations_message = "sum of the values "
    elif '-' in state['operations']:
        total = state['values'][0] - sum(state['values'][1:])
        operations_message = "subtraction of the values "
    elif '*' in state['operations']:
        total = 1
        for value in state['values']:
            total *= value
        operations_message = "multiplication of the values "
    elif '/' in state['operations']:
        total = state['values'][0]
        for value in state['values'][1:]:
            if value == 0:
                state['messages'].append("ivision by zero is not allowed.")
                return state
            total /= value
        operations_message = "division of the values "

    state['result'] = f"Hi {state['name']}. The {operations_message} is: {total}. "
    state['messages'].append(state['result'])
    return state

def post_processing(state: AgentState) -> AgentState:
    """
    A node that processes the final state and appends a closing message.
    """
    if not state['messages']:
        state['messages'].append("No messages to display.")
        return state
    state['messages'].append(f"You have these skills {state['skills']}.")
    # state['messages'].append(f"Thank you {state['name']}! Your request has been processed.")
    return state

def create_graph_png(app: StateGraph,
                     fname:str='graph_visualization.png') -> None:
    """
    Create a PNG visualization of the graph.
    """
    graph_png = app.get_graph().draw_mermaid_png()
    with open(fname, "wb") as f:
        f.write(graph_png)
    print(f"Graph saved as '{fname}'")

def print_graph_result(result: AgentState) -> None:
    """
    Print the graph in a human-readable format.
    """
    print(result['messages'], f"\n*** How else can I help you?")


def build_graph_from_config(config: dict) -> StateGraph:
    """
    Build a complete StateGraph from configuration.
    
    :param config: Dictionary containing nodes, entry_point, and finish_point
    :return: Configured StateGraph
    """
    graph = StateGraph(AgentState)
    
    # Add all nodes
    for node_name, node_info in config["nodes"].items():
        graph.add_node(node_name, node_info["function"])
    
    # Set entry point
    graph.set_entry_point(config["entry_point"])
    
    # Add edges
    for node_name, node_info in config["nodes"].items():
        for target_node in node_info["edges_to"]:
            graph.add_edge(node_name, target_node)
    
    # Set finish point
    graph.set_finish_point(config["finish_point"])
    
    return graph


# Enhanced nodes structure with topology information
nodes_config = {
    "nodes": {
        "greeting": {
            "function": greeting_node,
            "edges_to": ["processor"]
        },
        "processor": {
            "function": process_values,
            "edges_to": ["post_processing"]
        },
        "post_processing": {
            "function": post_processing,
            "edges_to": []  # No outgoing edges (finish point)
        }
    },
    "entry_point": "greeting",
    "finish_point": "post_processing"
}

graph = build_graph_from_config(nodes_config)

app = graph.compile()
create_graph_png(app, 'graph_complete_visualization.png')

# Test the complete workflow
result = app.invoke(AgentState(messages=[], operations=['*'], 
                               values=[1, 2, 3, 4, 5], name="Robert", result="",
                               skills=["Python", "Data Analysis", "C#"]))
print_graph_result(result)