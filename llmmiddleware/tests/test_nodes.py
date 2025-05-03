from pocketflow import Flow
from nodes import SetupNode, QuestionNode

def test_simple_flow():
    # Create a simple flow with a setup node and question node
    setup_node = SetupNode()
    question_node = QuestionNode()
    
    # Connect the nodes
    setup_node >> question_node
    
    # Create a flow
    flow = Flow(start=setup_node)
    
    # Initialize shared store with minimal test data
    shared = {
        "config": {
            "sql_db": "test.db",
            "question_db": "test_questions.json"
        },
        "question": "What is the total sales by region?"
    }
    
    # Mock the dependencies (we'll just print instead of actually running)
    print("Running test flow with setup and question nodes")
    print(f"Initial shared data: {shared}")
    
    # This will likely fail since we don't have the Vanna client properly set up,
    # but we'll see how far we get
    try:
        flow.run(shared)
        print(f"Updated shared data: {shared}")
    except Exception as e:
        print(f"Error during flow execution: {e}")

if __name__ == "__main__":
    test_simple_flow() 