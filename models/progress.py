from datetime import datetime, timezone
from . import db

class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    practice_completed = db.Column(db.Boolean, default=False, nullable=False)
    last_position = db.Column(db.String(100), default='overview', nullable=False)  # 'overview', 'terminal', 'practice'
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),
    )

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'practice_completed': self.practice_completed,
            'last_position': self.last_position,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UserLearningState(db.Model):
    __tablename__ = 'user_learning_state'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    current_level = db.Column(db.String(50), default='Beginner', nullable=False)
    current_category = db.Column(db.String(100), default='Basic Navigation', nullable=False)
    current_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='SET NULL'), nullable=True)
    total_lessons_completed = db.Column(db.Integer, default=0, nullable=False)
    completion_percentage = db.Column(db.Float, default=0.0, nullable=False)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    current_lesson = db.relationship('Lesson', foreign_keys=[current_lesson_id])

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'current_level': self.current_level,
            'current_category': self.current_category,
            'current_lesson_id': self.current_lesson_id,
            'total_lessons_completed': self.total_lessons_completed,
            'completion_percentage': round(self.completion_percentage, 1),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
