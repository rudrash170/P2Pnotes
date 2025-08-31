"""
main.py
Entry point for P2P Notes App.
Runs the main orchestrator from app.py.
"""

from app import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())