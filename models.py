"""
models.py
Data models for P2P Notes App.
Contains the Note class.
"""

import uuid
import time


class Note:
    def __init__(self, id: str = None, content: str = "", updated_at: float = None):
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.updated_at = updated_at or time.time()

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['content'], data['updated_at'])