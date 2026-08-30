from supabase import Client, create_client


class AuthService:
    def __init__(self, url: str, key: str):
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY are required")
        self.client: Client = create_client(url, key)
