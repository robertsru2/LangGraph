from typing import Dict, TypedDict, List
from langgraph.graph import StateGraph, START, END
from collections import defaultdict
from IPython.display import display, Image
import json
import random

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
    
class AgentStateV(TypedDict):
    """
    A state schema for the agent that includes operations and numbers.
    This is used to define the state of the agent in the graph.
    """
    name: str
    number: List[int]
    counter: int

def greeting_node2(state: AgentStateV) -> AgentStateV:
    """
    A simple greeting node that initializes the state with a welcome message.
    """
    if 'name' not in state:
        state['name'] = "User"
    
    if 'number' not in state:
        state['number'] = []
    
    state['name'] = f"Hello {state['name']}! How can I assist you today?"
    state["counter"] = 0
    
    return state
    
def random_node(state: AgentStateV) -> AgentStateV:
    """
    A node that randomly genmerates a number from 1-10.
    """
   
    state['number'].append(random.randint(0, 10))
    state['counter'] += 1
    
    return state

def should_continue(state: AgentStateV) -> AgentStateV:    
    """
    Function to decide what to do next.
    """
    if state['counter'] < 5:
        print("ENTERING LOOP", state['counter'])
        return "loop"
    else:
        return "exit"

def run_graph_exerciseV(state: AgentStateV) -> AgentStateV:
    """
    Run a simple graph exercise with the given state.
    """
    graph = StateGraph(AgentStateV)
    
    # Define nodes
    graph.add_node("greeting", greeting_node2)
    graph.add_node("random", random_node)
    graph.add_edge("greeting", "random")
    # Define edges
        
    # Conditional edge based on the result of should_continue
    graph.add_conditional_edges("random", 
        should_continue, 
        {
            "loop": "random",
            "exit": END
        }
    )

    graph.add_edge(START, "greeting")
    app = graph.compile()
    create_graph_png(app, 'Exercise5_visualization.png') 
    # Invoke the graph
    result = app.invoke(state)
    
    return result

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
  

def router_node2(state: AgentState) -> str:
    """
    A router node that determines which operation to perform based on the operation in state.
    Returns the key for the next node.
    """
    if 'messages' not in state:
        state['messages'] = []

    if 'operation2' not in state:
        raise ValueError("State must contain 'operation2'.")
    if state['operation2'] == '+':
        return "addition_operation2"
    elif state['operation2'] == '-':
        return "subtraction_operation2"



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

def print_graph_result_manual(result: AgentStateTest) -> None:
    """
    Print the graph in a human-readable format.
    """
    print(result['messages'], f"\n*** How else can I help you?")

def print_graph_result_config(result: AgentState) -> None:
    """
    Print the graph in a human-readable format.
    """
    print(result['messages'], f"\n*** How else can I help you?")
    
def build_graph_from_config(config: dict, state_schema=AgentStateTest) -> StateGraph:
    """
    Build a complete StateGraph from configuration.
    
    :param config: Dictionary containing nodes, entry_point, and finish_point(s)
    :param state_schema: The state schema to use (defaults to AgentStateTest)
    :return: Configured StateGraph
    """
    graph = StateGraph(state_schema)
    
    # Add all nodes
    for node_name, node_info in config["nodes"].items():
        graph.add_node(node_name, node_info["function"])
    
    # Set entry point
    graph.set_entry_point(config["entry_point"])
    
    # Add regular edges and conditional edges
    for node_name, node_info in config["nodes"].items():
        # Add regular edges
        for target_node in node_info.get("edges_to", []):
            graph.add_edge(node_name, target_node)
        
        # Add conditional edges if they exist
        if "conditional_edges" in node_info:
            conditional_mapping = node_info["conditional_edges"]
            # Use the separate router function if provided, otherwise use the node function
            router_func = node_info.get("router_function", node_info["function"])
            graph.add_conditional_edges(
                node_name,
                router_func,
                conditional_mapping
            )
    
    # Handle finish points (single or multiple)
    if "finish_point" in config:
        graph.set_finish_point(config["finish_point"])
    elif "finish_points" in config:
        # For multiple finish points, connect each to END
        for finish_node in config["finish_points"]:
            graph.add_edge(finish_node, END)
    
    return graph


def load_arithmetic_config_from_json(json_file_path: str, function_mapping_file: str = None) -> dict:
    """
    Load arithmetic nodes configuration from JSON file and convert function names to actual functions.
    
    :param json_file_path: Path to the JSON configuration file
    :param function_mapping_file: Optional path to separate function mapping JSON file
    :return: Configuration dictionary with actual function references
    """
    # Load JSON configuration
    with open(json_file_path, 'r') as f:
        json_config = json.load(f)
    
    # Load function mapping from separate file or from main config
    if function_mapping_file:
        # Option 1: Load from separate function mapping file
        with open(function_mapping_file, 'r') as f:
            mapping_config = json.load(f)
        function_mapping_config = mapping_config["function_mapping"]
    else:
        # Option 2: Load from integrated config file (if available)
        if "function_mapping" in json_config:
            function_mapping_config = json_config["function_mapping"]
        else:
            raise ValueError("No function mapping found. Either provide a separate function_mapping_file or include function_mapping in the main config.")
    
    # Build function mapping dynamically from config
    function_mapping = {}
    
    # Get current module's global namespace to access functions
    current_module = globals()
    
    for func_name, func_config in function_mapping_config.items():
        if func_config["type"] == "lambda":
            # Evaluate lambda expression safely
            function_mapping[func_name] = eval(func_config["expression"])
        elif func_config["type"] == "function_reference":
            # Get function from module globals
            module_func_name = func_config["module_function"]
            if module_func_name in current_module:
                function_mapping[func_name] = current_module[module_func_name]
            else:
                raise ValueError(f"Function '{module_func_name}' not found in current module")
        else:
            raise ValueError(f"Unknown function type: {func_config['type']}")
    
    # Convert to Python configuration format
    config = {
        "nodes": {},
        "entry_point": json_config["entry_point"],
        "finish_points": json_config["finish_points"]
    }
    
    # Process each node
    for node_name, node_info in json_config["nodes"].items():
        node_config = {
            "function": function_mapping[node_info["function_name"]],
            "edges_to": node_info["edges_to"]
        }
        
        # Add conditional edges if present
        if "conditional_edges" in node_info:
            node_config["conditional_edges"] = node_info["conditional_edges"]
        
        # Add router function if present
        if "router_function_name" in node_info:
            node_config["router_function"] = function_mapping[node_info["router_function_name"]]
        
        config["nodes"][node_name] = node_config
    
    return config


def create_graph_from_json_config(json_file_path: str, state_schema, function_mapping_file: str = None) -> StateGraph:
    """
    Convenience function to create a complete StateGraph from JSON configuration.
    
    :param json_file_path: Path to the JSON configuration file
    :param state_schema: The state schema to use (e.g., AgentState)
    :param function_mapping_file: Optional path to separate function mapping JSON file
    :return: Compiled StateGraph ready for execution
    """
    config = load_arithmetic_config_from_json(json_file_path, function_mapping_file)
    graph = build_graph_from_config(config, state_schema)
    return graph.compile()



# -- New nodes for arithmetic operations loaded from JSON
with open('config.json', 'r') as f:
    config = json.load(f)

json_path = config.get('config_path')
graph_nodes_config_file = json_path + config.get('graph_nodes', 'graph_nodes.json')
function_mapping_file = json_path + config.get('function_mapping', 'function_mapping.json')  # Only needed if you have a separate function mapping file
# Load the arithmetic nodes configuration from JSON                                          # If so, then pass function_mapping_file to load function.   
graph_nodes_config = load_arithmetic_config_from_json(graph_nodes_config_file)        

# Test the config-based graph creation
graph3 = build_graph_from_config(graph_nodes_config, AgentState)
app3 = graph3.compile()
create_graph_png(app3, 'Config_based_arithmetic_operations_visualization.png')

# Test both graphs with the same input
test_input = AgentState(operation='+', operation2='+',
                        number1=10, number2=5, 
                        number3=7, number4=3, 
                        final_number=0,final_number2=0, 
                         messages=[])

print("\n=== Config-based Graph (graph3) Results ===")
result2 = app3.invoke(test_input)
print_graph_result_config(result2)

## Now run exercise V
result = run_graph_exerciseV(AgentStateV(name="Alice", number=[], counter=-1))
print(result)
