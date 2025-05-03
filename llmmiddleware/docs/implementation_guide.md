# LLM Middleware Implementation Guide

This guide provides practical instructions for developers who want to extend or modify the LLM Middleware project. The project is built on the PocketFlow framework, which emphasizes modularity and composability.

## Adding New Features

### 1. Adding a New Node

To create a new node:

1. Add your node class to `llmmiddleware/nodes/sql_nodes.py` or create a new file in the `nodes` directory
2. Inherit from `Node` (or specialized nodes like `BatchNode` or `AsyncNode`)
3. Implement the required methods:
   - `prep(self, shared)`: Prepare data from the shared store
   - `exec(self, prep_res)`: Execute the core functionality
   - `post(self, shared, prep_res, exec_res)`: Store results and return the next action

Example:
```python
from llmmiddleware.core.pocketflow import Node

class MyCustomNode(Node):
    def __init__(self, max_retries=3, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        # Get data from shared store
        return shared.get("some_data")
    
    def exec(self, prep_res):
        # Process the data
        return process_data(prep_res)
    
    def post(self, shared, prep_res, exec_res):
        # Store the result
        shared["processed_data"] = exec_res
        return "success"  # Action for flow control
```

### 2. Creating a New Flow

To create a new flow:

1. Add your flow creation function to `llmmiddleware/flows/sql_flows.py` or create a new file in the `flows` directory
2. Create and connect nodes with the `>>` operator
3. Use conditional transitions with the `-` operator followed by `>>` for different paths

Example:
```python
from llmmiddleware.core.pocketflow import Flow
from llmmiddleware.nodes.sql_nodes import SetupNode
from llmmiddleware.nodes.my_custom_nodes import ProcessDataNode, ValidateDataNode

def create_data_processing_flow():
    """Create a flow for processing data."""
    # Create nodes
    setup_node = SetupNode()
    process_node = ProcessDataNode()
    validate_node = ValidateDataNode()
    
    # Connect nodes
    setup_node >> process_node >> validate_node
    
    # Conditional transitions
    validate_node - "valid" >> finish_node
    validate_node - "invalid" >> process_node  # Loop back if invalid
    
    # Create flow
    return Flow(start=setup_node)
```

### 3. Adding a New Utility Function

To add a new utility function:

1. Add your function to an existing file in `llmmiddleware/utils/` or create a new file
2. Ensure your function has clear documentation and error handling
3. Add a test case for your function

Example:
```python
# llmmiddleware/utils/data_utils.py

def process_data(data):
    """
    Process data in a specific way.
    
    Args:
        data (dict): Data to process
        
    Returns:
        dict: Processed data
    """
    # Process the data
    processed = {}
    
    # Return the processed data
    return processed
    
if __name__ == "__main__":
    # Test the function
    test_data = {"key": "value"}
    result = process_data(test_data)
    print(result)
```

## Integration with the Middleware

To integrate your new components with the middleware:

1. Update the `middleware.py` file to use your new flow
2. Expose new endpoints if needed for your functionality
3. Update the web interface in `app.py` to use your new features

## Best Practices

1. **Follow PocketFlow Patterns**
   - Use the shared store for communication between nodes
   - Design nodes with single responsibilities
   - Create clear transitions between nodes

2. **Error Handling**
   - Set appropriate `max_retries` and `wait` times for nodes
   - Implement `exec_fallback` for graceful failure handling
   - Add detailed error messages and logging

3. **Testing**
   - Create unit tests for utility functions
   - Test nodes individually
   - Create integration tests for flows

4. **Documentation**
   - Update this guide and `design.md` when adding significant features
   - Document parameters and return values for new functions
   - Add examples for how to use new components

## Common Patterns

### Batch Processing

For processing multiple items in parallel:

```python
from llmmiddleware.core.pocketflow import BatchNode

class ProcessBatchNode(BatchNode):
    def exec(self, item):
        # Process a single item
        return process_item(item)
```

### Async Operations

For non-blocking operations:

```python
from llmmiddleware.core.pocketflow import AsyncNode

class AsyncOperationNode(AsyncNode):
    async def prep_async(self, shared):
        return shared.get("data")
        
    async def exec_async(self, prep_res):
        # Async operation
        return await async_operation(prep_res)
        
    async def post_async(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        return "default"
```

## Debugging Tips

1. Add print statements in node methods to see data flow
2. Use `logging` to record node execution
3. Run individual nodes with test data:
   ```python
   node = MyCustomNode()
   shared = {"test_data": "value"}
   result = node.run(shared)
   print(shared)  # Check updated shared store
   ```

## Next Steps

After implementing your extensions:

1. Update tests to cover your new functionality
2. Document your changes in the appropriate files
3. Test with real data to ensure everything works as expected 