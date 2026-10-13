import json
import hashlib
from datetime import datetime, timezone
from . import db

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_name = db.Column(db.String(255), default='Linux Commands Learning Assistant — Professional Mastery', nullable=False)
    issue_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    verification_hash = db.Column(db.String(255), nullable=False)
    criteria_summary_json = db.Column(db.Text, nullable=False)
    download_count = db.Column(db.Integer, default=0, nullable=False)

    @classmethod
    def generate_hash(cls, cert_id, user_id, user_email, issue_timestamp):
        raw = f"{cert_id}:{user_id}:{user_email}:{issue_timestamp}:linux_secret_salt"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get_criteria(self):
        try:
            return json.loads(self.criteria_summary_json)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'certificate_id': self.certificate_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Verified Student',
            'course_name': self.course_name,
            'issue_date': self.issue_date.strftime('%B %d, %Y'),
            'verification_hash': self.verification_hash,
            'criteria': self.get_criteria(),
            'download_count': self.download_count
        }

    def __repr__(self):
        return f'<Certificate {self.certificate_id} - User {self.user_id}>'
