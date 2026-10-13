import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, AssessmentQuiz, AssessmentQuestion, AssessmentAttempt

assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/assessment')
@login_required
def index():
    """
    Renders Assessment module home with available quizzes, difficulty badges,
    passing criteria, and user attempt history.
    """
    quizzes = AssessmentQuiz.query.all()
    user_attempts = AssessmentAttempt.query.filter_by(user_id=current_user.id).order_by(AssessmentAttempt.attempted_at.desc()).all()

    # Calculate user best score per quiz
    best_scores = {}
    for attempt in user_attempts:
        qid = attempt.quiz_id
        if qid not in best_scores or attempt.percentage > best_scores[qid]['percentage']:
            best_scores[qid] = {
                'percentage': attempt.percentage,
                'passed': attempt.passed,
                'score': attempt.score,
                'total': attempt.total_questions
            }

    return render_template(
        'assessment/index.html',
        quizzes=quizzes,
        attempts=user_attempts,
        best_scores=best_scores
    )

@assessment_bp.route('/assessment/<slug>', methods=['GET', 'POST'])
@login_required
def take_quiz(slug):
    """
    Renders the interactive quiz interface and processes answer submissions.
    """
    quiz = AssessmentQuiz.query.filter_by(slug=slug).first_or_404()
    questions = quiz.questions.all()

    if request.method == 'POST':
        user_answers = {}
        score = 0
        total = len(questions)

        for q in questions:
            user_choice = request.form.get(f'question_{q.id}', '').strip().upper()
            user_answers[str(q.id)] = user_choice
            if user_choice == q.correct_option.upper():
                score += 1

        percentage = round((score / total * 100.0), 1) if total > 0 else 0.0
        passed = percentage >= quiz.passing_score

        # Save attempt in MySQL
        attempt = AssessmentAttempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=score,
            total_questions=total,
            percentage=percentage,
            passed=passed,
            answers_json=json.dumps(user_answers)
        )
        db.session.add(attempt)
        db.session.commit()

        return redirect(url_for('assessment.result', attempt_id=attempt.id))

    return render_template(
        'assessment/quiz.html',
        quiz=quiz,
        questions=questions
    )

@assessment_bp.route('/assessment/result/<int:attempt_id>')
@login_required
def result(attempt_id):
    """
    Displays assessment evaluation result, score, percentage, pass/fail status,
    and question-by-question breakdown with correct answers and explanations.
    """
    attempt = AssessmentAttempt.query.filter_by(id=attempt_id, user_id=current_user.id).first_or_404()
    quiz = attempt.quiz
    questions = quiz.questions.all()
    user_answers = attempt.get_answers()

    review_data = []
    for q in questions:
        selected = user_answers.get(str(q.id), 'None')
        is_correct = selected == q.correct_option
        review_data.append({
            'question': q,
            'selected': selected,
            'is_correct': is_correct
        })

    return render_template(
        'assessment/result.html',
        attempt=attempt,
        quiz=quiz,
        review_data=review_data
    )
