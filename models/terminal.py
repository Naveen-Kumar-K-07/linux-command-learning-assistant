import json
from datetime import datetime, timezone
from . import db

class TerminalState(db.Model):
    __tablename__ = 'terminal_states'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    cwd = db.Column(db.String(255), default='/home/user', nullable=False)
    filesystem_json = db.Column(db.Text, nullable=False)
    command_history_json = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def get_filesystem(self):
        try:
            return json.loads(self.filesystem_json)
        except Exception:
            return None

    def set_filesystem(self, vfs_dict):
        self.filesystem_json = json.dumps(vfs_dict)

    def get_history(self):
        try:
            return json.loads(self.command_history_json) if self.command_history_json else []
        except Exception:
            return []

    def set_history(self, history_list):
        self.command_history_json = json.dumps(history_list[-50:])  # keep last 50

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'cwd': self.cwd,
            'filesystem': self.get_filesystem(),
            'history': self.get_history(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
