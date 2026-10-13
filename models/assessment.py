import json
from datetime import datetime, timezone
from . import db

class AssessmentQuiz(db.Model):
    __tablename__ = 'assessment_quizzes'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Advanced, Comprehensive
    passing_score = db.Column(db.Integer, default=70, nullable=False)
    time_limit_minutes = db.Column(db.Integer, default=15, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    questions = db.relationship('AssessmentQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan', order_by='AssessmentQuestion.order_num')
    attempts = db.relationship('AssessmentAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'difficulty_level': self.difficulty_level,
            'passing_score': self.passing_score,
            'time_limit_minutes': self.time_limit_minutes,
            'total_questions': self.questions.count()
        }


class AssessmentQuestion(db.Model):
    __tablename__ = 'assessment_questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('assessment_quizzes.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='mcq', nullable=False)  # mcq, syntax, scenario, output
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(5), nullable=False)  # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text, nullable=False)
    order_num = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self, include_correct=False):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'order_num': self.order_num
        }
        if include_correct:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
        return data


class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('assessment_quizzes.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    passed = db.Column(db.Boolean, default=False, nullable=False)
    answers_json = db.Column(db.Text, nullable=True)
    attempted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_answers(self):
        try:
            return json.loads(self.answers_json) if self.answers_json else {}
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title if self.quiz else 'Assessment',
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': round(self.percentage, 1),
            'passed': self.passed,
            'answers': self.get_answers(),
            'attempted_at': self.attempted_at.strftime('%Y-%m-%d %H:%M UTC')
        }
