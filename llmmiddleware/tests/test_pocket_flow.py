from pocketflow import Flow, Node

class SimpleNode(Node):
    def prep(self, shared):
        return shared.get("input", "No input provided")
    
    def exec(self, prep_result):
        return f"Processed: {prep_result}"
    
    def post(self, shared, prep_res, exec_res):
        shared["output"] = exec_res
        return "default"

def main():
    # Create a simple node
    simple_node = SimpleNode()
    
    # Create a flow
    flow = Flow(start=simple_node)
    
    # Initialize shared store
    shared = {
        "input": "Hello, PocketFlow!"
    }
    
    # Run the flow
    flow.run(shared)
    
    # Print the output
    print(shared["output"])

if __name__ == "__main__":
    main() 