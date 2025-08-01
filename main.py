from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph, START, END
from collections import defaultdict
from IPython.display import display, Image


# Define a state schema for StateGraph
class AgentStateTest(TypedDict):
    messages: List[str]= []
    values: List[int]
    operations: List[str]
    name: str
    skills: List[str] = []
    current_step: str
    result: str

class AgentState(TypedDict):
    operation: str
    operation2: str
    number1: int
    number2: int
    number3: int
    number4: int
    final_number: int
    final_number2: int
    messages: List[str] = []  # This is NOT a default value!
    
    
def adder(state: AgentState) -> AgentState:
    """
    A simple adder node that adds two numbers and updates the state.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'number1' not in state or 'number2' not in state:
        raise ValueError("State must contain 'number1' and 'number2'.")
    
    state['final_number'] = state['number1'] + state['number2']
    state['messages'].append(f"Adding {state['number1']} and {state['number2']} gives {state['final_number']}.")
    return state

def subtractor(state: AgentState) -> AgentState:
    """
    A simple subtractor node that subtracts two numbers and updates the state.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'number1' not in state or 'number2' not in state:
        raise ValueError("State must contain 'number1' and 'number2'.")
    
    state['final_number'] = state['number1'] - state['number2']
    state['messages'].append(f"Subtracting {state['number2']} from {state['number1']} gives {state['final_number']}.")
    return state

def adder2(state: AgentState) -> AgentState:
    """
    A simple adder node that adds two numbers and updates the state.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'number3' not in state or 'number4' not in state:
        raise ValueError("State must contain 'number3' and 'number4'.")
    
    state['final_number2'] = state['number3'] + state['number4']
    state['messages'].append(f"Adding {state['number3']} and {state['number4']} gives {state['final_number']}.")
    return state

def subtractor2(state: AgentState) -> AgentState:
    """
    A simple subtractor node that subtracts two numbers and updates the state.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'number3' not in state or 'number4' not in state:
        raise ValueError("State must contain 'number3' and 'number4'.")
    
    state['final_number2'] = state['number3'] - state['number4']
    state['messages'].append(f"Subtracting {state['number3']} from {state['number4']} gives {state['final_number2']}.")
    return state

def decide_next_node(state: AgentState) -> AgentState:
    """
    A decision node that determines the next step based on the operation.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'operation' not in state:
        raise ValueError("State must contain 'operation'.")
    
    if state['operation'] == '+':
        # return adder(state)
        return "addition_operation"
    elif state['operation'] == '-':
        # return subtractor(state)
        return "subtraction_operation"
    else:
        raise ValueError("Unknown operation. Use '+' or '-'.")

def decide_next_node2(state: AgentState) -> AgentState:
    """
    A decision node that determines the next step based on the operation.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'operation' not in state:
        raise ValueError("State must contain 'operation'.")
    
    if state['operation2'] == '+':
        # return adder(state)
        return "addition_operation2"
    elif state['operation2'] == '-':
        # return subtractor(state)
        return "subtraction_operation2"
    else:
        raise ValueError("Unknown operation. Use '+' or '-'.")

def greeting_node(state: AgentStateTest) -> AgentStateTest:
    """
    A simple greeting node that initializes the state with a welcome message.
    """
    state['messages'].append(f"Hello {state['name']}! How can I assist you today?")
    return state

def process_values(state: AgentStateTest) -> AgentStateTest:
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

def router_node(state: AgentState) -> str:
    """
    A router node that determines which operation to perform based on the operation in state.
    Returns the key for the next node.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'operation' not in state:
        raise ValueError("State must contain 'operation'.")
    
    if state['operation'] == '+':
        return "addition_operation"
    elif state['operation'] == '-':
        return "subtraction_operation"
    else:
        return "post_processing"  # Default case

def router_node2(state: AgentState) -> str:
    """
    A router node that determines which operation to perform based on the operation in state.
    Returns the key for the next node.
    """
    if 'messages' not in state:
        state['messages'] = []
    
    if 'operation' not in state:
        raise ValueError("State must contain 'operation'.")
    
    if state['operation'] == '+':
        return "addition_operation2"
    elif state['operation'] == '-':
        return "subtraction_operation2"
    else:
        return "post_processing"  # Default case


def post_processing(state: AgentStateTest) -> AgentStateTest:
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

def print_graph_result(result: AgentStateTest) -> None:
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
    graph = StateGraph(AgentStateTest)
    
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
result = app.invoke(AgentStateTest(messages=[], operations=['*'], 
                               values=[1, 2, 3, 4, 5], name="Robert", result="",
                               skills=["Python", "Data Analysis", "C#"]))
print_graph_result(result)

# -- New nodes for arithmetic operations
arithmetic_nodes_config = {
    "nodes": {
        "addition_operation": {
            "function": adder,
            "edges_to": ["decide_next_node"],
        },
        "subtraction_operation": {
            "function": subtractor,
            "edges_to": ["decide_next_node"]
        },
            "addition_operation2": {
            "function": adder,
            "edges_to": ["decide_next_node2"],
        },
        "subtraction_operation2": {
            "function": subtractor2,
            "edges_to": ["decide_next_node2"]
        },
        "decide_next_node": {
            "function": decide_next_node,
            "edges_to": ["post_processing"],
            "flow_control": {
                "type": "conditional",
                "condition": lambda state: state
            }
        },
        "post_processing": {
            "function": post_processing,
            "edges_to": []  # No outgoing edges (finish point)
        }
    },
    "entry_point": "addition_operation",  # Start with addition operation
    "finish_point": "post_processing"
}

   
graph2 = StateGraph(AgentState)
graph2.add_node("addition_operation", adder)
graph2.add_node("subtraction_operation", subtractor)
graph2.add_node("router", lambda state: state)  #  Proper router function

graph2.add_edge(START, "router")

graph2.add_conditional_edges(
    "router", 
    router_node,
    {
        "addition_operation": "addition_operation",
        "subtraction_operation": "subtraction_operation"
    }
)

graph2.add_node("addition_operation2", adder2)
graph2.add_node("subtraction_operation2", subtractor2)
graph2.add_node("router2", lambda state: state)

graph2.add_edge("addition_operation", "router2" )
graph2.add_edge("subtraction_operation", "router2" )

graph2.add_conditional_edges(
    "router2", 
    router_node2,
    {
        "addition_operation2": "addition_operation2",
        "subtraction_operation2": "subtraction_operation2"
    }
)

graph2.add_edge("addition_operation2", END)
graph2.add_edge("subtraction_operation2", END)

#build_graph_from_config(arithmetic_nodes_config)
app2 = graph2.compile()
create_graph_png(app2, 'Conditional graph_arithmetic_operations_visualization.png') 

result = app2.invoke(AgentState(number1=10, 
                    operation='+', number2=5, 
                    final_number=0, number3=7,
                    number4=3, final_number2=0, 
                    operation2='+',messages=[]))

print_graph_result(result)

