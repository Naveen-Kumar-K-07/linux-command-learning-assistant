import json
from datetime import datetime, timezone
from . import db

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    lesson_slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    difficulty_level = db.Column(db.String(50), nullable=False, index=True)  # Beginner, Intermediate, Advanced
    command_name = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    syntax = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    practical_examples = db.Column(db.Text, nullable=False)  # JSON formatted list of examples
    expected_output = db.Column(db.Text, nullable=False)
    step_by_step = db.Column(db.Text, nullable=False)
    common_mistakes = db.Column(db.Text, nullable=False)
    practice_task = db.Column(db.Text, nullable=False)
    practice_expected_command = db.Column(db.String(255), nullable=False)
    lesson_order = db.Column(db.Integer, nullable=False, default=1, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    progress_records = db.relationship('UserProgress', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')

    def get_examples(self):
        try:
            return json.loads(self.practical_examples)
        except Exception:
            return [{"command": self.command_name, "desc": "Basic example", "output": self.expected_output}]

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.lesson_slug,
            'title': self.title,
            'category': self.category,
            'difficulty': self.difficulty_level,
            'command': self.command_name,
            'purpose': self.purpose,
            'syntax': self.syntax,
            'explanation': self.explanation,
            'examples': self.get_examples(),
            'expected_output': self.expected_output,
            'step_by_step': self.step_by_step,
            'common_mistakes': self.common_mistakes,
            'practice_task': self.practice_task,
            'practice_expected_command': self.practice_expected_command,
            'order': self.lesson_order
        }

    def __repr__(self):
        return f'<Lesson {self.command_name} - {self.title}>'
