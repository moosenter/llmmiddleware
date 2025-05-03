from llmmiddleware.core.pocketflow import Flow
from llmmiddleware.nodes.sql_nodes import (
    SetupNode, QuestionNode, GenerateSQLNode, ValidateSQLNode,
    ExecuteSQLNode, ShouldGenerateChartNode, GenerateChartNode,
    GenerateFollowupNode, GenerateSummaryNode
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sql_generation_flow():
    """
    Create and return a flow for generating SQL from natural language questions.
    
    Returns:
        Flow: A PocketFlow flow for SQL generation
    """
    logger.info("Creating SQL generation flow")
    
    # Create nodes
    setup_node = SetupNode()
    question_node = QuestionNode()
    generate_sql_node = GenerateSQLNode()
    validate_sql_node = ValidateSQLNode()
    execute_sql_node = ExecuteSQLNode()
    should_chart_node = ShouldGenerateChartNode()
    generate_chart_node = GenerateChartNode()
    generate_followup_node = GenerateFollowupNode()
    generate_summary_node = GenerateSummaryNode()
    
    # Connect nodes
    setup_node >> question_node
    question_node >> generate_sql_node
    generate_sql_node >> validate_sql_node
    
    # Conditional transitions
    validate_sql_node - "valid" >> execute_sql_node
    validate_sql_node - "invalid" >> question_node  # Loop back to question if SQL is invalid
    
    execute_sql_node >> should_chart_node
    
    should_chart_node - "chart" >> generate_chart_node
    should_chart_node - "no_chart" >> generate_followup_node
    
    generate_chart_node >> generate_followup_node
    generate_followup_node >> generate_summary_node
    
    # Create flow
    flow = Flow(start=setup_node)
    
    logger.info("SQL generation flow created")
    return flow

def create_sql_execution_flow():
    """
    Create and return a flow for executing pre-existing SQL without regeneration.
    
    Returns:
        Flow: A PocketFlow flow for SQL execution
    """
    logger.info("Creating SQL execution flow")
    
    # Create nodes
    setup_node = SetupNode()
    execute_sql_node = ExecuteSQLNode()
    should_chart_node = ShouldGenerateChartNode()
    generate_chart_node = GenerateChartNode()
    generate_followup_node = GenerateFollowupNode()
    generate_summary_node = GenerateSummaryNode()
    
    # Connect nodes
    setup_node >> execute_sql_node
    execute_sql_node >> should_chart_node
    
    # Conditional transitions
    should_chart_node - "chart" >> generate_chart_node
    should_chart_node - "no_chart" >> generate_followup_node
    
    generate_chart_node >> generate_followup_node
    generate_followup_node >> generate_summary_node
    
    # Create flow
    flow = Flow(start=setup_node)
    
    logger.info("SQL execution flow created")
    return flow

def create_suggestion_flow():
    """
    Create and return a flow for generating suggested questions.
    
    Returns:
        Flow: A PocketFlow flow for generating suggestions
    """
    logger.info("Creating suggestion flow")
    
    # Create nodes
    setup_node = SetupNode()
    
    # This flow only sets up the Vanna client, actual question generation
    # is handled separately in middleware.py
    
    # Create flow
    flow = Flow(start=setup_node)
    
    logger.info("Suggestion flow created")
    return flow

if __name__ == "__main__":
    # Just for testing the flow creation
    flow = create_sql_generation_flow()
    print("Flow created successfully") 