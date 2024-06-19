import os
from dotenv import load_dotenv

def load_env_vars():
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    credentials_json_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    gpt_model_name = os.getenv('GPT_MODEL_NAME')
    
    if not openai_api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable in .env file.")
    
    if not credentials_json_path:
        raise ValueError("Please set the GOOGLE_SHEETS_CREDENTIALS_JSON environment variable in .env file.")

    if os.path.isdir(credentials_json_path):
        raise ValueError("The path specified for GOOGLE_SHEETS_CREDENTIALS_JSON is a directory. It should be the path to the credentials JSON file.")

    if not gpt_model_name:
        raise ValueError("Please set the GPT_MODEL_NAME environment variable in .env file.")
    
    return openai_api_key, credentials_json_path, gpt_model_name
