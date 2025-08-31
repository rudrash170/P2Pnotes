"""
app.py
Main orchestrator for P2P Notes App.
Initializes and runs all components: database, peer manager, API, and CLI.
"""

import threading
import asyncio
import uuid
from config import DB_PATH, PORT, FLASK_PORT, DEVICE_ID_LENGTH
from db import DatabaseManager
from p2p import PeerManager
from api import create_api
from cli import run_cli


def run_flask_api(app, port):
    """
    Runs the Flask API in a separate thread and binds to all interfaces for network access.
    Args:
        app (Flask): The Flask app instance.
        port (int): Port to run the Flask server on.
    """
    app.run(host="0.0.0.0", port=port, threaded=True)


async def main():
    """
    Main orchestrator for P2P Notes App.
    Initializes and runs all components: database, peer manager, API, and CLI.
    """
    device_id = str(uuid.uuid4())[:DEVICE_ID_LENGTH]
    db_manager = DatabaseManager(DB_PATH)
    notes_manager = db_manager.load_notes()
    peer_manager = PeerManager(device_id, PORT, notes_manager, db_manager)
    flask_app = create_api(notes_manager, peer_manager, device_id, db_manager)

    flask_thread = threading.Thread(
        target=run_flask_api, args=(flask_app, FLASK_PORT), daemon=True
    )
    flask_thread.start()

    tasks = [
        asyncio.create_task(peer_manager.discover_peers()),
        asyncio.create_task(peer_manager.listen_for_discovery()),
        asyncio.create_task(peer_manager.start_server()),
        asyncio.create_task(peer_manager.sync_all_peers()),
        asyncio.create_task(run_cli(device_id, notes_manager, peer_manager, db_manager)),
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())