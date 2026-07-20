## Initialize the database here
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load the variables from your .env file
load_dotenv()

# 2. Extract the variables into your script
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")