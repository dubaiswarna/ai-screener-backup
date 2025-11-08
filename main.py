"""
Main entry point for Railway deployment
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "8080")
    
    # Start Streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "enhanced_screener.py",
        f"--server.port={port}",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ])

