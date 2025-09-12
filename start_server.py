#!/usr/bin/env python3
"""
Startup script for Cyber Law Chatbot API Server
"""

import os
import sys

def main():
    """Start the API server"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(script_dir, 'src')
        
        # Add src to Python path
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        # Set working directory to script directory
        os.chdir(script_dir)
        
        # Import and run the API server
        from src.api_server import app
        
        print("🚀 Starting Cyber Law Chatbot API Server...")
        print("📡 Server will be available at: http://localhost:5000")
        print("🔗 Frontend can connect to: http://localhost:5000/api/chat")
        print("📋 Health check: http://localhost:5000/health")
        print("=" * 60)
        
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disable debug mode to avoid restart issues
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("Make sure you have installed all requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()