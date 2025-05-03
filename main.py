#!/usr/bin/env python3

"""
LLM Middleware - Main entry point
This script serves as the main entry point for the LLM Middleware application.
"""

import logging
from llmmiddleware.flows.sql_flows import create_sql_generation_flow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the LLM Middleware application."""
    logger.info("Starting LLM Middleware application")
    
    # Initialize shared store
    shared = {
        "config": {},  # Will be populated with configuration
        "question": None,  # Will be populated with user question
        "results": None,  # Will store query results
    }
    
    # Create and run the SQL generation flow
    flow = create_sql_generation_flow()
    flow.run(shared)
    
    logger.info("LLM Middleware application finished")

if __name__ == "__main__":
    main() 