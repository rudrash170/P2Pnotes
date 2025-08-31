# P2P Notes

A peer-to-peer notes app with automatic local network discovery, bidirectional sync, and a web UI. Works on Windows, Linux, Mac, and Android (via browser).

## Features
- Create, edit, and delete notes
- Automatic peer discovery and sync on local network
- REST API for programmatic access
- Dark theme UI
- SQLite database for persistence
- Cross-platform

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install flask rich
   ```
2. **Run the app:**
   ```bash
   python main.py
   ```
3. **Access the web UI:**
   - Open a browser and go to `http://<your_ip>:5000/`
   - Use the CLI in the terminal for interactive note management

## Ports Used

| Port   | Protocol | Purpose                                   |
|--------|----------|-------------------------------------------|
| 5000   | TCP      | Flask REST API & Web UI                   |
| 9876   | TCP      | P2P sync server (note exchange)           |
| 9999   | UDP      | Peer discovery broadcast/listen           |

### Port Details
- **5000 (TCP):**
  - Used by Flask to serve the REST API and web UI.
  - Accessible from any device on the same network.
  - Make sure this port is open in your firewall for remote access.

- **9876 (TCP):**
  - Used for direct peer-to-peer note sync between devices.
  - Each device runs a TCP server on this port.
  - Allow this port for full sync functionality.

- **9999 (UDP):**
  - Used for peer discovery via UDP broadcast.
  - Devices broadcast their presence and listen for others.
  - Allow this port for automatic peer discovery.

## Database Location
- By default, notes are stored in a SQLite file at:
  - **Windows:** `Project_repo\.p2p_notes.db`
- You can change the location in `config.py`.

## Firewall Configuration
- Allow inbound connections on ports 5000 (TCP), 9876 (TCP), and 9999 (UDP).
- On Windows, use Windows Defender Firewall > Advanced Settings > Inbound Rules.

## Endpoints
- `GET /notes` — List all notes
- `POST /notes` — Add a note (`{"content": "text"}`)
- `PUT /notes/<id>` — Edit a note
- `DELETE /notes/<id>` — Delete a note
- `GET /peers` — List known peers
- `GET /status` — App/device status

## Web UI
- Accessible at `http://<your_ip>:5000/` or `localhost:5000`
- Fully dark-themed, mobile-friendly
- Add, edit, delete notes with instant sync

## P2P Sync
- Run the app on multiple devices in the same network
- Notes will sync automatically between peers

## Contributing
- Fork the repo, create a branch, and submit a pull request

---

**Enjoy your secure, decentralized notes!**