"""Shared test setup. Tests never touch the real database, Supabase or Groq."""
import os
import sys

# Make `import app...` work when pytest is run from the backend folder.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Some modules create clients when they are imported, so give them harmless dummy values.
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/test")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault(
    "SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.dummy",
)
os.environ.setdefault("GROQ_API_KEY", "test")
