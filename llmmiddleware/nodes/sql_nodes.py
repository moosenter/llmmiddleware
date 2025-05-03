from llmmiddleware.core.pocketflow import Node
import llmmiddleware.utils.call_vanna as vanna_utils
import logging
import pandas as pd
import orjson
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SetupNode(Node):
    """Node for setting up the Vanna client."""
    
    def __init__(self, max_retries=3, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to set up Vanna client")
        return shared.get("config", {})
    
    def exec(self, config):
        if not config:
            logger.warning("No configuration provided")
            return None
        
        logger.info(f"Setting up Vanna client with config: {config}")
        try:
            return vanna_utils.setup_vanna(config)
        except Exception as e:
            logger.error(f"Error setting up Vanna client: {e}")
            logger.error(traceback.format_exc())
            raise e
    
    def post(self, shared, prep_res, exec_res):
        if exec_res is not None:
            shared["vanna_client"] = exec_res
            logger.info("Vanna client set up successfully")
        else:
            logger.error("Failed to set up Vanna client")
        
        return "default"


class QuestionNode(Node):
    """Node for handling user questions."""
    
    def __init__(self, max_retries=1, wait=0):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to process user question")
        return shared.get("question")
    
    def exec(self, question):
        logger.info(f"Processing question: {question}")
        return question
    
    def post(self, shared, prep_res, exec_res):
        if exec_res:
            shared["question"] = exec_res
            logger.info(f"Question stored: {exec_res}")
            return "default"
        else:
            logger.warning("No question provided")
            return "no_question"


class GenerateSQLNode(Node):
    """Node for generating SQL from a natural language question."""
    
    def __init__(self, max_retries=3, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to generate SQL")
        return {
            "vanna_client": shared.get("vanna_client"),
            "question": shared.get("question")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        question = prep_data.get("question")
        
        if not vanna_client:
            logger.error("Missing Vanna client")
            return None
            
        if not question:
            logger.error("Missing question")
            return None
        
        logger.info(f"Generating SQL for question: {question}")
        try:
            sql = vanna_utils.generate_sql(vanna_client, question)
            if not sql:
                logger.warning("Generated SQL is empty")
                return None
            return sql
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            logger.error(traceback.format_exc())
            raise e
    
    def post(self, shared, prep_res, exec_res):
        if exec_res:
            shared["sql"] = exec_res
            logger.info(f"SQL generated: {exec_res}")
            return "default"
        else:
            error_msg = "Unable to understand the question. Please try a more specific data-related question."
            shared["error"] = error_msg
            logger.warning(error_msg)
            return "no_sql"


class ValidateSQLNode(Node):
    """Node for validating generated SQL."""
    
    def __init__(self, max_retries=2, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to validate SQL")
        return {
            "vanna_client": shared.get("vanna_client"),
            "sql": shared.get("sql")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        sql = prep_data.get("sql")
        
        if not vanna_client or not sql:
            logger.warning("Missing Vanna client or SQL")
            return False
        
        logger.info(f"Validating SQL: {sql}")
        try:
            return vanna_utils.is_sql_valid(vanna_client, sql)
        except Exception as e:
            logger.error(f"Error validating SQL: {e}")
            logger.error(traceback.format_exc())
            raise e
    
    def post(self, shared, prep_res, exec_res):
        shared["is_sql_valid"] = exec_res
        logger.info(f"SQL validation result: {exec_res}")
        
        if exec_res:
            return "valid"
        else:
            return "invalid"


class ExecuteSQLNode(Node):
    """Node for executing validated SQL and returning results."""
    
    def __init__(self, max_retries=3, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to execute SQL")
        return {
            "vanna_client": shared.get("vanna_client"),
            "sql": shared.get("sql")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        sql = prep_data.get("sql")
        
        if not vanna_client:
            logger.error("Missing Vanna client")
            return None
            
        if not sql:
            logger.error("Missing SQL query")
            return None
        
        logger.info(f"Executing SQL: {sql}")
        try:
            cleaned_sql = vanna_utils.clean_sql(sql)
            if not cleaned_sql:
                logger.error("SQL query is empty after cleaning")
                return None
                
            result = vanna_utils.run_sql(vanna_client, cleaned_sql)
            if result is None or (isinstance(result, pd.DataFrame) and result.empty):
                logger.warning("SQL execution returned no results")
                
            return result
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            logger.error(traceback.format_exc())
            raise e
    
    def post(self, shared, prep_res, exec_res):
        if exec_res is not None:
            shared["results"] = exec_res
            if isinstance(exec_res, pd.DataFrame):
                logger.info(f"SQL execution results shape: {exec_res.shape}")
            else:
                logger.info("SQL execution completed, but result is not a DataFrame")
            return "default"
        else:
            error_msg = "No results from SQL execution"
            shared["error"] = error_msg
            logger.warning(error_msg)
            return "no_results"


class ShouldGenerateChartNode(Node):
    """Node for determining if a chart should be generated."""
    
    def __init__(self, max_retries=2, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to check if chart should be generated")
        return {
            "vanna_client": shared.get("vanna_client"),
            "results": shared.get("results")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        results = prep_data.get("results")
        
        if not vanna_client or results is None:
            logger.warning("Missing Vanna client or results")
            return False
        
        logger.info("Checking if chart should be generated")
        try:
            return vanna_utils.should_generate_chart(vanna_client, results)
        except Exception as e:
            logger.error(f"Error determining if chart should be generated: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def post(self, shared, prep_res, exec_res):
        shared["should_chart"] = exec_res
        logger.info(f"Should generate chart: {exec_res}")
        
        if exec_res:
            return "chart"
        else:
            return "no_chart"


class GenerateChartNode(Node):
    """Node for generating a chart from query results."""
    
    def __init__(self, max_retries=3, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to generate chart")
        return {
            "vanna_client": shared.get("vanna_client"),
            "question": shared.get("question"),
            "sql": shared.get("sql"),
            "results": shared.get("results")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        question = prep_data.get("question")
        sql = prep_data.get("sql")
        results = prep_data.get("results")
        
        if not vanna_client or not question or not sql or results is None:
            logger.warning("Missing required data for chart generation")
            return None
        
        logger.info("Generating chart")
        try:
            # Generate Plotly code
            code = vanna_utils.generate_plotly_code(vanna_client, question, sql, results)
            # Generate Plotly figure
            figure = vanna_utils.get_plotly_figure(vanna_client, code, results)
            
            return {
                "code": code,
                "figure": figure
            }
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            logger.error(traceback.format_exc())
            raise e
    
    def post(self, shared, prep_res, exec_res):
        if exec_res:
            shared["chart_code"] = exec_res.get("code")
            shared["chart"] = exec_res.get("figure")
            logger.info("Chart generated successfully")
            return "default"
        else:
            logger.warning("No chart generated")
            return "no_chart"


class GenerateFollowupNode(Node):
    """Node for generating follow-up questions."""
    
    def __init__(self, max_retries=2, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to generate follow-up questions")
        return {
            "vanna_client": shared.get("vanna_client"),
            "question": shared.get("question"),
            "sql": shared.get("sql"),
            "results": shared.get("results")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        question = prep_data.get("question")
        sql = prep_data.get("sql")
        results = prep_data.get("results")
        
        if not vanna_client or not question or not sql or results is None:
            logger.warning("Missing required data for follow-up generation")
            return []
        
        logger.info("Generating follow-up questions")
        try:
            return vanna_utils.generate_followup_questions(vanna_client, question, sql, results)
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def post(self, shared, prep_res, exec_res):
        shared["followup_questions"] = exec_res
        logger.info(f"Generated {len(exec_res)} follow-up questions")
        return "default"


class GenerateSummaryNode(Node):
    """Node for generating a summary of the results."""
    
    def __init__(self, max_retries=2, wait=1):
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        logger.info("Preparing to generate summary")
        return {
            "vanna_client": shared.get("vanna_client"),
            "question": shared.get("question"),
            "results": shared.get("results")
        }
    
    def exec(self, prep_data):
        vanna_client = prep_data.get("vanna_client")
        question = prep_data.get("question")
        results = prep_data.get("results")
        
        if not vanna_client or not question or results is None:
            logger.warning("Missing required data for summary generation")
            return None
        
        logger.info("Generating summary")
        try:
            return vanna_utils.generate_summary(vanna_client, question, results)
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def post(self, shared, prep_res, exec_res):
        shared["summary"] = exec_res
        logger.info("Summary generated")
        return "default" 