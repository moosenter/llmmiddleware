from pocketflow import Flow, Node

# Mock nodes that simulate our actual nodes without external dependencies
class MockSetupNode(Node):
    def prep(self, shared):
        print("MockSetupNode: Preparing")
        return shared.get("config", {})
    
    def exec(self, config):
        print(f"MockSetupNode: Executing with config: {config}")
        # Simulate setting up a client
        return "mock_vanna_client"
    
    def post(self, shared, prep_res, exec_res):
        print("MockSetupNode: Post-processing")
        shared["vanna_client"] = exec_res
        return "default"

class MockQuestionNode(Node):
    def prep(self, shared):
        print("MockQuestionNode: Preparing")
        return shared.get("question")
    
    def exec(self, question):
        print(f"MockQuestionNode: Processing question: {question}")
        return question
    
    def post(self, shared, prep_res, exec_res):
        print("MockQuestionNode: Post-processing")
        shared["question"] = exec_res
        return "default"

class MockGenerateSQLNode(Node):
    def prep(self, shared):
        print("MockGenerateSQLNode: Preparing")
        return {
            "vanna_client": shared.get("vanna_client"),
            "question": shared.get("question")
        }
    
    def exec(self, prep_data):
        print(f"MockGenerateSQLNode: Generating SQL for: {prep_data}")
        return "SELECT * FROM sales GROUP BY region"
    
    def post(self, shared, prep_res, exec_res):
        print("MockGenerateSQLNode: Post-processing")
        shared["sql"] = exec_res
        return "default"

def test_mock_flow():
    # Create a simple flow with mock nodes
    setup_node = MockSetupNode()
    question_node = MockQuestionNode()
    sql_node = MockGenerateSQLNode()
    
    # Connect the nodes
    setup_node >> question_node >> sql_node
    
    # Create a flow
    flow = Flow(start=setup_node)
    
    # Initialize shared store with test data
    shared = {
        "config": {
            "sql_db": "test.db",
            "question_db": "test_questions.json"
        },
        "question": "What is the total sales by region?"
    }
    
    print("Running test flow with mock nodes")
    print(f"Initial shared data: {shared}")
    
    # Run the flow
    flow.run(shared)
    
    print(f"Updated shared data: {shared}")

if __name__ == "__main__":
    test_mock_flow() 