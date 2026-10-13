import unittest
import json
import io
from app import create_app
from config import Config
from models import db, User, Lesson, UserProgress, UserLearningState, TerminalState, AssessmentQuiz, AssessmentAttempt, Certificate
from services.simulator import VirtualLinuxSimulator
from services.progress_service import ProgressService
from services.pdf_generator import CertificatePDFGenerator

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    DEV_MODE_AUTO_VERIFY = True

class LinuxAssistantTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    # -------------------------------------------------------------
    # 1. Authentication & Security Tests
    # -------------------------------------------------------------
    def test_user_registration(self):
        response = self.client.post('/register', data={
            'full_name': 'Test User',
            'email': 'testuser@gmail.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        user = User.query.filter_by(email='testuser@gmail.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_duplicate_email_rejection(self):
        self.client.post('/register', data={
            'full_name': 'First User',
            'email': 'duplicate@gmail.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        # Try registering same email
        resp2 = self.client.post('/register', data={
            'full_name': 'Second User',
            'email': 'duplicate@gmail.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', resp2.data)

    def test_invalid_login(self):
        resp = self.client.post('/login', data={
            'email': 'nonexistent@gmail.com',
            'password': 'wrong'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', resp.data)

    def test_successful_login_and_logout(self):
        # Register user
        self.client.post('/register', data={
            'full_name': 'Login Tester',
            'email': 'login_tester@gmail.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        # Login
        resp_login = self.client.post('/login', data={
            'email': 'login_tester@gmail.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome', resp_login.data)
        self.assertIn(b'Learn', resp_login.data)

        # Logout
        resp_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out securely', resp_logout.data)

    def test_protected_routes_require_login(self):
        resp = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in', resp.data)

        resp2 = self.client.get('/learn', follow_redirects=True)
        self.assertIn(b'Please log in', resp2.data)

    # -------------------------------------------------------------
    # 2. Terminal Simulator & VFS Execution Tests
    # -------------------------------------------------------------
    def test_simulator_basic_navigation(self):
        sim = VirtualLinuxSimulator()
        
        # Test pwd
        res_pwd = sim.execute('pwd')
        self.assertEqual(res_pwd['output'], '/home/user')
        self.assertEqual(res_pwd['status'], 'success')

        # Test ls
        res_ls = sim.execute('ls')
        self.assertIn('welcome.txt', res_ls['output'])
        self.assertIn('documents', res_ls['output'])

        # Test cd
        res_cd = sim.execute('cd documents')
        self.assertEqual(sim.cwd, '/home/user/documents')
        self.assertEqual(res_cd['status'], 'success')

    def test_simulator_mkdir_and_touch(self):
        sim = VirtualLinuxSimulator()
        
        # mkdir
        res_mkdir = sim.execute('mkdir test_folder')
        self.assertEqual(res_mkdir['status'], 'success')
        self.assertIn('test_folder', sim.vfs['children']['home']['children']['user']['children'])

        # touch
        res_touch = sim.execute('touch test_file.py')
        self.assertEqual(res_touch['status'], 'success')
        self.assertIn('test_file.py', sim.vfs['children']['home']['children']['user']['children'])

    def test_simulator_cat_and_echo_redirection(self):
        sim = VirtualLinuxSimulator()
        
        # echo with redirection >
        res_echo = sim.execute('echo "Hello Linux" > greeting.txt')
        self.assertEqual(res_echo['status'], 'success')

        # cat greeting.txt
        res_cat = sim.execute('cat greeting.txt')
        self.assertEqual(res_cat['output'], 'Hello Linux')

        # echo with append >>
        sim.execute('echo "Line 2" >> greeting.txt')
        res_cat2 = sim.execute('cat greeting.txt')
        self.assertIn('Hello Linux', res_cat2['output'])
        self.assertIn('Line 2', res_cat2['output'])

    def test_simulator_grep_and_pipe(self):
        sim = VirtualLinuxSimulator()
        res_pipe = sim.execute('cat documents/report.log | grep ERROR')
        self.assertEqual(res_pipe['status'], 'success')
        self.assertIn('ERROR', res_pipe['output'])

    def test_simulator_chmod(self):
        sim = VirtualLinuxSimulator()
        res_chmod = sim.execute('chmod 755 scripts/backup.sh')
        self.assertEqual(res_chmod['status'], 'success')
        backup_node = sim.get_node('/home/user/scripts/backup.sh')
        self.assertEqual(backup_node['perms'], 'rwxr-xr-x')

    def test_simulator_invalid_command(self):
        sim = VirtualLinuxSimulator()
        res = sim.execute('fake_nonexistent_command')
        self.assertEqual(res['status'], 'error')
        self.assertIn('command not found', res['output'])

    # -------------------------------------------------------------
    # 3. Learning Progress Persistence & User Isolation
    # -------------------------------------------------------------
    def test_user_progress_persistence_and_isolation(self):
        # Create user 1
        user1 = User(full_name='User One', email='user1@gmail.com')
        user1.set_password('pass123')
        db.session.add(user1)
        db.session.commit()

        # Create user 2
        user2 = User(full_name='User Two', email='user2@gmail.com')
        user2.set_password('pass123')
        db.session.add(user2)
        db.session.commit()

        lesson = Lesson.query.first()
        self.assertIsNotNone(lesson)

        # Mark completed for user 1
        ProgressService.record_progress(user1.id, lesson.id, is_completed=True)

        overview1 = ProgressService.get_user_overview(user1.id)
        overview2 = ProgressService.get_user_overview(user2.id)

        # User 1 has completed 1 lesson, User 2 has completed 0 (isolation test)
        self.assertIn(lesson.id, overview1['completed_lesson_ids'])
        self.assertNotIn(lesson.id, overview2['completed_lesson_ids'])
        self.assertEqual(overview2['completed_count'], 0)

    # -------------------------------------------------------------
    # 4. Assessment Attempt & Scoring Tests
    # -------------------------------------------------------------
    def test_assessment_scoring(self):
        user = User(full_name='Quiz User', email='quiz_user@gmail.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        quiz = AssessmentQuiz.query.first()
        self.assertIsNotNone(quiz)
        questions = quiz.questions.all()

        # Build perfect answers
        form_data = {}
        for q in questions:
            form_data[f'question_{q.id}'] = q.correct_option

        # Log in
        self.client.post('/login', data={'email': 'quiz_user@gmail.com', 'password': 'pass123'})

        # Post quiz submission
        resp = self.client.post(f'/assessment/{quiz.slug}', data=form_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        attempt = AssessmentAttempt.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, len(questions))
        self.assertEqual(attempt.percentage, 100.0)
        self.assertTrue(attempt.passed)

    # -------------------------------------------------------------
    # 5. Certification Eligibility & PDF Generation
    # -------------------------------------------------------------
    def test_certificate_eligibility_and_pdf(self):
        user = User(full_name='Cert User', email='cert_user@gmail.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Complete all lessons for user
        lessons = Lesson.query.all()
        for l in lessons:
            ProgressService.record_progress(user.id, l.id, is_completed=True)

        # Record a passed assessment attempt
        quiz = AssessmentQuiz.query.first()
        attempt = AssessmentAttempt(
            user_id=user.id,
            quiz_id=quiz.id,
            score=5,
            total_questions=5,
            percentage=100.0,
            passed=True
        )
        db.session.add(attempt)
        db.session.commit()

        # Check eligibility
        eligibility = ProgressService.check_certification_eligibility(user.id)
        self.assertTrue(eligibility['eligible'])

        # Test ReportLab PDF Generator directly
        pdf_buffer = CertificatePDFGenerator.generate(
            user_name=user.full_name,
            certificate_id='LCLA-2026-TEST123',
            issue_date_str='October 13, 2026'
        )
        self.assertIsInstance(pdf_buffer, io.BytesIO)
        pdf_bytes = pdf_buffer.getvalue()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1000)

    # -------------------------------------------------------------
    # 6. Interactive Practice Challenge Auto-Completion Tests
    # -------------------------------------------------------------
    def test_interactive_practice_challenge_auto_completes_lesson(self):
        user = User(full_name='Practice User', email='practice_user@gmail.com')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()

        # Log in
        self.client.post('/login', data={'email': 'practice_user@gmail.com', 'password': 'pass123'})

        lesson = Lesson.query.filter_by(lesson_slug='pwd').first()
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.practice_expected_command, 'pwd')

        # 1. Execute a command that does not match the practice task
        res_non_match = self.client.post('/api/terminal/execute', json={
            'command': 'whoami',
            'lesson_id': lesson.id
        })
        self.assertEqual(res_non_match.status_code, 200)
        data_non_match = res_non_match.get_json()
        self.assertFalse(data_non_match['practice_matched'])

        prog = UserProgress.query.filter_by(user_id=user.id, lesson_id=lesson.id).first()
        self.assertTrue(prog is None or not prog.is_completed)

        # 2. Execute the exact practice command
        res_match = self.client.post('/api/terminal/execute', json={
            'command': 'pwd',
            'lesson_id': lesson.id
        })
        self.assertEqual(res_match.status_code, 200)
        data_match = res_match.get_json()
        self.assertTrue(data_match['practice_matched'])

        # Verify database record updated to completed
        prog_completed = UserProgress.query.filter_by(user_id=user.id, lesson_id=lesson.id).first()
        self.assertIsNotNone(prog_completed)
        self.assertTrue(prog_completed.practice_completed)
        self.assertTrue(prog_completed.is_completed)

        # Verify overview includes completed lesson
        overview = ProgressService.get_user_overview(user.id)
        self.assertIn(lesson.id, overview['completed_lesson_ids'])
        self.assertGreaterEqual(overview['completed_count'], 1)

if __name__ == '__main__':
    unittest.main()
