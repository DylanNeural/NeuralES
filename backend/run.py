#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.main import app
    print("App imported successfully")
    import uvicorn
    print("Starting server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()