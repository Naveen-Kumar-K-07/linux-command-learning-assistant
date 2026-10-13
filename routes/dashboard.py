from flask import Blueprint, render_template
from flask_login import login_required, current_user
from services.progress_service import ProgressService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Renders personalized dashboard featuring EXACTLY four main navigation icons:
    1. Learn
    2. Assessment
    3. Certification
    4. Logout
    plus user welcome message, learning progress statistics, and quick-continue banner.
    """
    overview = ProgressService.get_user_overview(current_user.id)
    eligibility = ProgressService.check_certification_eligibility(current_user.id)

    return render_template(
        'dashboard.html',
        user=current_user,
        overview=overview,
        eligibility=eligibility
    )
