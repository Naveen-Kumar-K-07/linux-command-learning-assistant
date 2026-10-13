from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import db, Lesson, UserProgress
from services.progress_service import ProgressService

learn_bp = Blueprint('learn', __name__)

@learn_bp.route('/learn')
@login_required
def index():
    """
    Renders main learning center, categorized by difficulty levels (Beginner, Intermediate, Advanced)
    with 'Continue Learning' banner and track progress indicators.
    """
    overview = ProgressService.get_user_overview(current_user.id)
    
    # Query all lessons grouped by difficulty
    beginner_lessons = Lesson.query.filter_by(difficulty_level='Beginner').order_by(Lesson.lesson_order.asc()).all()
    intermediate_lessons = Lesson.query.filter_by(difficulty_level='Intermediate').order_by(Lesson.lesson_order.asc()).all()
    advanced_lessons = Lesson.query.filter_by(difficulty_level='Advanced').order_by(Lesson.lesson_order.asc()).all()

    completed_ids = set(overview['completed_lesson_ids'])

    return render_template(
        'learn/index.html',
        overview=overview,
        beginner_lessons=beginner_lessons,
        intermediate_lessons=intermediate_lessons,
        advanced_lessons=advanced_lessons,
        completed_ids=completed_ids
    )

@learn_bp.route('/learn/continue')
@login_required
def continue_learning():
    """Directly redirects user to their last active or next incomplete lesson."""
    overview = ProgressService.get_user_overview(current_user.id)
    target = overview.get('next_lesson')
    if target:
        return redirect(url_for('learn.lesson_detail', slug=target.lesson_slug))
    first = Lesson.query.order_by(Lesson.lesson_order.asc()).first()
    return redirect(url_for('learn.lesson_detail', slug=first.lesson_slug if first else 'pwd'))

@learn_bp.route('/learn/<slug>')
@login_required
def lesson_detail(slug):
    """
    Renders the comprehensive interactive lesson page containing command documentation,
    interactive terminal simulator, live VFS tree visualizer, and practice tasks.
    """
    lesson = Lesson.query.filter_by(lesson_slug=slug).first_or_404()
    
    # Update user's current position and learning state
    ProgressService.record_progress(current_user.id, lesson.id, last_position='terminal')

    # Get user progress for this lesson
    user_prog = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    is_completed = user_prog.is_completed if user_prog else False
    practice_completed = user_prog.practice_completed if user_prog else False

    # Find previous and next lessons
    prev_lesson = Lesson.query.filter(Lesson.lesson_order < lesson.lesson_order).order_by(Lesson.lesson_order.desc()).first()
    next_lesson = Lesson.query.filter(Lesson.lesson_order > lesson.lesson_order).order_by(Lesson.lesson_order.asc()).first()

    all_lessons = Lesson.query.order_by(Lesson.lesson_order.asc()).all()
    completed_ids = {p.lesson_id for p in UserProgress.query.filter_by(user_id=current_user.id, is_completed=True).all()}

    return render_template(
        'learn/lesson.html',
        lesson=lesson,
        is_completed=is_completed,
        practice_completed=practice_completed,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        all_lessons=all_lessons,
        completed_ids=completed_ids
    )

@learn_bp.route('/api/learn/complete', methods=['POST'])
@login_required
def mark_completed():
    """API to toggle or mark lesson completion status."""
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    completed = data.get('completed', True)

    if not lesson_id:
        return jsonify({'success': False, 'error': 'Missing lesson_id'}), 400

    prog = ProgressService.record_progress(current_user.id, lesson_id, is_completed=completed)
    overview = ProgressService.get_user_overview(current_user.id)

    return jsonify({
        'success': True,
        'is_completed': prog.is_completed,
        'total_completed': overview['completed_count'],
        'percentage': overview['completion_percentage']
    })

@learn_bp.route('/api/learn/complete-practice', methods=['POST'])
@login_required
def complete_practice():
    """API called when user completes the practice task via the terminal simulator."""
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')

    if not lesson_id:
        return jsonify({'success': False, 'error': 'Missing lesson_id'}), 400

    prog = ProgressService.record_progress(current_user.id, lesson_id, practice_completed=True, is_completed=True)
    overview = ProgressService.get_user_overview(current_user.id)

    return jsonify({
        'success': True,
        'practice_completed': True,
        'is_completed': prog.is_completed,
        'percentage': overview['completion_percentage']
    })
