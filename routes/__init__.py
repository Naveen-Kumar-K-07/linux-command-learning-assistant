from .auth import auth_bp
from .dashboard import dashboard_bp
from .learn import learn_bp
from .terminal import terminal_bp
from .assessment import assessment_bp
from .certificate import certificate_bp
from .code import code_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'learn_bp',
    'terminal_bp',
    'assessment_bp',
    'certificate_bp',
    'code_bp'
]
