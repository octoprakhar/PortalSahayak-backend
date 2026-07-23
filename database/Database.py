## Initialize the database here
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load the variables from your .env file
load_dotenv()

class Database:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url:
            raise RuntimeError("SUPABASE_URL is missing")
        
        if not key:
            raise RuntimeError("SUPABASE_SERVICE_KEY is missing")
        
        self.client: Client = create_client(url,key)