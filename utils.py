import os
from dotenv import load_dotenv, find_dotenv


def get_openai_key():
    _ = load_dotenv(find_dotenv())
    api_key = os.environ['OPENAI_API_KEY']
    return api_key
