"""
p2p.py
Peer-to-peer networking for P2P Notes App.
Contains PeerManager for peer discovery and note synchronization.
"""

import asyncio
import json
import socket
from typing import Set, Dict
from models import Note

class PeerManager:
    def __init__(self, device_id, port, notes: Dict[str, Note], db_manager):
        self.device_id = device_id
        self.port = port
        self.peers: Set[str] = set()
        self.notes = notes
        self.db_manager = db_manager
        self.running = True

    async def discover_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while self.running:
            try:
                message = json.dumps({
                    'type': 'discovery',
                    'device_id': self.device_id,
                    'port': self.port
                })
                sock.sendto(message.encode(), ('255.255.255.255', 9999))
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Discovery error: {e}")
                await asyncio.sleep(5)

    async def listen_for_discovery(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 9999))
        sock.setblocking(False)
        while self.running:
            try:
                loop = asyncio.get_event_loop()
                data, addr = await loop.sock_recvfrom(sock, 1024)
                message = json.loads(data.decode())
                if message['type'] == 'discovery' and message['device_id'] != self.device_id:
                    peer_addr = f"{addr[0]}:{message['port']}"
                    if peer_addr not in self.peers:
                        self.peers.add(peer_addr)
                        print(f"Discovered peer: {message['device_id']} at {peer_addr}")
                        asyncio.create_task(self.sync_with_peer(addr[0], message['port']))
            except Exception as e:
                await asyncio.sleep(1)

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, '0.0.0.0', self.port
        )
        print(f"Server listening on port {self.port}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(1024 * 1024)
            if not data:
                return
            message = json.loads(data.decode())
            if message['type'] == 'sync':
                remote_notes = {nid: Note.from_dict(ndata) for nid, ndata in message['notes'].items()}
                merged_count = self.merge_notes(remote_notes)
                response = {
                    'type': 'sync_response',
                    'notes': {nid: note.to_dict() for nid, note in self.notes.items()}
                }
                writer.write(json.dumps(response).encode())
                await writer.drain()
                if merged_count > 0:
                    print(f"Synced {merged_count} notes from peer")
        except Exception as e:
            print(f"Sync error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    def merge_notes(self, remote_notes: Dict[str, Note]) -> int:
        merged_count = 0
        for note_id, remote_note in remote_notes.items():
            if note_id not in self.notes or remote_note.updated_at > self.notes[note_id].updated_at:
                self.db_manager.save_note(remote_note)
                merged_count += 1
        # Reload notes from DB after merge
        self.notes.clear()
        self.notes.update(self.db_manager.load_notes())
        return merged_count

    async def sync_with_peer(self, host: str, port: int):
        try:
            reader, writer = await asyncio.open_connection(host, port)
            message = {
                'type': 'sync',
                'notes': {nid: note.to_dict() for nid, note in self.notes.items()}
            }
            writer.write(json.dumps(message).encode())
            await writer.drain()
            data = await reader.read(1024 * 1024)
            if data:
                response = json.loads(data.decode())
                if response['type'] == 'sync_response':
                    remote_notes = {nid: Note.from_dict(ndata) for nid, ndata in response['notes'].items()}
                    merged_count = self.merge_notes(remote_notes)
                    if merged_count > 0:
                        print(f"Received {merged_count} notes from peer")
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            pass

    async def sync_all_peers(self):
        while self.running:
            for peer_addr in list(self.peers):
                try:
                    host, port = peer_addr.split(':')
                    await self.sync_with_peer(host, int(port))
                except Exception:
                    self.peers.discard(peer_addr)
            await asyncio.sleep(10)