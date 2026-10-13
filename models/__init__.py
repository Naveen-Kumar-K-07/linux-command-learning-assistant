from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .lesson import Lesson
from .progress import UserProgress, UserLearningState
from .terminal import TerminalState
from .assessment import AssessmentQuiz, AssessmentQuestion, AssessmentAttempt
from .certificate import Certificate

__all__ = [
    'db',
    'User',
    'Lesson',
    'UserProgress',
    'UserLearningState',
    'TerminalState',
    'AssessmentQuiz',
    'AssessmentQuestion',
    'AssessmentAttempt',
    'Certificate'
]
