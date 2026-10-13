from datetime import datetime, timezone
from models import db, User, Lesson, UserProgress, UserLearningState, AssessmentQuiz, AssessmentAttempt, Certificate

class ProgressService:
    @staticmethod
    def get_or_create_state(user_id):
        state = UserLearningState.query.filter_by(user_id=user_id).first()
        if not state:
            first_lesson = Lesson.query.order_by(Lesson.lesson_order.asc()).first()
            state = UserLearningState(
                user_id=user_id,
                current_level="Beginner",
                current_category="Basic Navigation",
                current_lesson_id=first_lesson.id if first_lesson else None,
                total_lessons_completed=0,
                completion_percentage=0.0
            )
            db.session.add(state)
            db.session.commit()
        return state

    @staticmethod
    def record_progress(user_id, lesson_id, is_completed=None, practice_completed=None, last_position=None):
        """Updates progress record for a specific lesson and re-computes global completion."""
        progress = UserProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        if not progress:
            progress = UserProgress(user_id=user_id, lesson_id=lesson_id)
            db.session.add(progress)

        if is_completed is not None:
            progress.is_completed = is_completed
            if is_completed and not progress.completed_at:
                progress.completed_at = datetime.now(timezone.utc)
        if practice_completed is not None:
            progress.practice_completed = practice_completed
        if last_position is not None:
            progress.last_position = last_position

        progress.updated_at = datetime.now(timezone.utc)

        # Update global learning state
        state = ProgressService.get_or_create_state(user_id)
        current_lesson = db.session.get(Lesson, lesson_id)
        if current_lesson:
            state.current_lesson_id = lesson_id
            state.current_level = current_lesson.difficulty_level
            state.current_category = current_lesson.category

        total_lessons = Lesson.query.count()
        completed_count = UserProgress.query.filter_by(user_id=user_id, is_completed=True).count()
        state.total_lessons_completed = completed_count
        state.completion_percentage = (completed_count / total_lessons * 100.0) if total_lessons > 0 else 0.0
        state.last_activity = datetime.now(timezone.utc)

        db.session.commit()
        return progress

    @staticmethod
    def get_user_overview(user_id):
        """Returns complete progress statistics and next lesson to resume."""
        state = ProgressService.get_or_create_state(user_id)
        total_lessons = Lesson.query.count()
        completed_records = UserProgress.query.filter_by(user_id=user_id, is_completed=True).all()
        completed_ids = {p.lesson_id for p in completed_records}

        # Determine next lesson to continue
        next_lesson = None
        if state.current_lesson_id:
            curr = db.session.get(Lesson, state.current_lesson_id)
            if curr and curr.id not in completed_ids:
                next_lesson = curr

        if not next_lesson:
            next_lesson = Lesson.query.filter(~Lesson.id.in_(completed_ids)).order_by(Lesson.lesson_order.asc()).first()
        if not next_lesson:
            next_lesson = Lesson.query.order_by(Lesson.lesson_order.desc()).first()

        completed_count = len(completed_ids)
        percentage = round((completed_count / total_lessons * 100.0), 1) if total_lessons > 0 else 0.0

        # Category statistics
        categories = db.session.query(Lesson.category).distinct().all()
        category_stats = []
        for (cat_name,) in categories:
            cat_total = Lesson.query.filter_by(category=cat_name).count()
            cat_done = UserProgress.query.join(Lesson).filter(
                UserProgress.user_id == user_id,
                UserProgress.is_completed == True,
                Lesson.category == cat_name
            ).count()
            category_stats.append({
                'category': cat_name,
                'total': cat_total,
                'completed': cat_done,
                'percentage': round((cat_done / cat_total * 100.0), 1) if cat_total > 0 else 0.0
            })

        return {
            'state': state,
            'total_lessons': total_lessons,
            'completed_count': completed_count,
            'completion_percentage': percentage,
            'next_lesson': next_lesson,
            'completed_lesson_ids': list(completed_ids),
            'category_stats': category_stats
        }

    @staticmethod
    def check_certification_eligibility(user_id):
        """
        Calculates whether the user satisfies requirements to earn a certificate.
        Requirements:
        1. Complete at least 80% of all lessons.
        2. Pass at least one comprehensive or advanced assessment quiz (score >= passing_score).
        """
        overview = ProgressService.get_user_overview(user_id)
        completion_pct = overview['completion_percentage']

        passed_attempts = AssessmentAttempt.query.filter_by(user_id=user_id, passed=True).all()
        passed_quiz_ids = {a.quiz_id for a in passed_attempts}

        total_quizzes = AssessmentQuiz.query.count()
        passed_count = len(passed_quiz_ids)

        # Eligibility criteria
        meets_lesson_criteria = completion_pct >= 80.0
        meets_quiz_criteria = passed_count >= 1

        missing = []
        if not meets_lesson_criteria:
            missing.append(f"Complete at least 80% of lessons (current: {completion_pct}%)")
        if not meets_quiz_criteria:
            missing.append("Pass at least 1 Assessment examination (passing score 70%)")

        eligible = meets_lesson_criteria and meets_quiz_criteria

        existing_cert = Certificate.query.filter_by(user_id=user_id).first()

        return {
            'eligible': eligible,
            'completion_percentage': completion_pct,
            'completed_lessons': overview['completed_count'],
            'total_lessons': overview['total_lessons'],
            'passed_quizzes': passed_count,
            'total_quizzes': total_quizzes,
            'missing_requirements': missing,
            'existing_certificate': existing_cert
        }
