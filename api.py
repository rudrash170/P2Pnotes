"""
api.py
Flask REST API for P2P Notes App.
Defines endpoints for notes, peers, and status.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import Note
import time
from datetime import datetime

def create_api(notes_manager, peer_manager, device_id, db_manager):
    app = Flask(__name__, template_folder="templates")

    @app.template_filter('datetime')
    def format_datetime(value):
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

    @app.route('/')
    @app.route('/notes/ui')
    def notes_ui():
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        notes = sorted(notes_manager.values(), key=lambda n: n.updated_at, reverse=True)
        return render_template('notes.html', notes=notes)

    @app.route('/notes/ui/add', methods=['POST'])
    def add_note_ui():
        content = request.form.get('content', '').strip()
        if content:
            from models import Note
            note = Note(content=content)
            db_manager.save_note(note)
        return redirect(url_for('notes_ui'))

    @app.route('/notes/ui/edit/<note_id>', methods=['POST'])
    def edit_note_ui(note_id):
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        note = notes_manager.get(note_id)
        if note:
            content = request.form.get('content', '').strip()
            if content:
                note.content = content
                note.updated_at = datetime.now().timestamp()
                db_manager.save_note(note)
        return redirect(url_for('notes_ui'))

    @app.route('/notes/ui/delete/<note_id>')
    def delete_note_ui(note_id):
        db_manager.delete_note(note_id)
        return redirect(url_for('notes_ui'))

    @app.route('/notes', methods=['GET'])
    def get_notes():
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        notes = [note.to_dict() for note in notes_manager.values()]
        return jsonify(notes)

    @app.route('/notes', methods=['POST'])
    def add_note():
        data = request.json
        content = data.get('content', '')
        if not content:
            return jsonify({'error': 'Content required'}), 400
        note = Note(content=content)
        db_manager.save_note(note)
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        return jsonify(note.to_dict()), 201

    @app.route('/notes/<note_id>', methods=['GET'])
    def get_note(note_id):
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        note = notes_manager.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        return jsonify(note.to_dict())

    @app.route('/notes/<note_id>', methods=['PUT'])
    def edit_note(note_id):
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        note = notes_manager.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        data = request.json
        content = data.get('content')
        if content:
            note.content = content
            note.updated_at = time.time()
            db_manager.save_note(note)
            notes_manager.clear()
            notes_manager.update(db_manager.load_notes())
        return jsonify(note.to_dict())

    @app.route('/notes/<note_id>', methods=['DELETE'])
    def delete_note_api(note_id):
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        if note_id not in notes_manager:
            return jsonify({'error': 'Note not found'}), 404
        db_manager.delete_note(note_id)
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        return jsonify({'result': 'deleted'})

    @app.route('/peers', methods=['GET'])
    def get_peers():
        return jsonify(list(peer_manager.peers))

    @app.route('/status', methods=['GET'])
    def get_status():
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        return jsonify({
            'device_id': device_id,
            'note_count': len(notes_manager),
            'peer_count': len(peer_manager.peers)
        })

    return app