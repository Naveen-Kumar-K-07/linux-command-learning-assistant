import re
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, TerminalState
from services.email_service import EmailService
from services.simulator import VirtualLinuxSimulator
from services.progress_service import ProgressService

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validates email format, specifically supporting and verifying gmail."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validations
        if not full_name or not email or not password or not confirm_password:
            flash('All registration fields are required.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email)

        if not is_valid_email(email):
            flash('Please enter a valid email address (e.g. yourname@gmail.com).', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter your password.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email)

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login', email=email))

        # Create new user
        new_user = User(
            full_name=full_name,
            email=email
        )
        new_user.set_password(password)
        code = new_user.generate_verification()

        # In dev mode, we can auto-verify or display code
        dev_auto_verify = current_app.config.get('DEV_MODE_AUTO_VERIFY', True)
        if dev_auto_verify:
            new_user.is_verified = True

        db.session.add(new_user)
        db.session.flush()

        # Initialize user's isolated virtual terminal state
        vfs_default = VirtualLinuxSimulator.get_default_vfs()
        term_state = TerminalState(
            user_id=new_user.id,
            cwd='/home/user',
            filesystem_json=VirtualLinuxSimulator().vfs
        )
        term_state.set_filesystem(vfs_default)
        db.session.add(term_state)

        # Initialize user learning state
        ProgressService.get_or_create_state(new_user.id)

        db.session.commit()

        # Dispatch email
        EmailService.send_verification_email(new_user.email, new_user.full_name, code, new_user.verification_token)

        if dev_auto_verify:
            flash(f'Account created and verified! Welcome, {new_user.full_name}. You may now log in.', 'success')
            return redirect(url_for('auth.login', email=email))
        else:
            flash(f'Account created! A verification code was sent to {email}.', 'info')
            return redirect(url_for('auth.verify_email', email=email, dev_code=code))

    return render_template('auth/register.html')

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email', '') or request.form.get('email', '')
    dev_code = request.args.get('dev_code', '')

    if request.method == 'POST':
        code_input = request.form.get('verification_code', '').strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found. Please register.', 'danger')
            return redirect(url_for('auth.register'))

        if user.is_verified:
            flash('Account is already verified. Please log in.', 'success')
            return redirect(url_for('auth.login'))

        if user.verification_code and user.verification_code == code_input:
            user.is_verified = True
            user.verification_code = None
            db.session.commit()
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login', email=email))
        else:
            flash('Invalid verification code. Please check your inbox or code.', 'danger')

    return render_template('auth/verify_email.html', email=email, dev_code=dev_code)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    email_prefill = request.args.get('email', '')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

        if not user.is_verified:
            # Allow automatic verification in local dev
            if current_app.config.get('DEV_MODE_AUTO_VERIFY', True):
                user.is_verified = True
                db.session.commit()
            else:
                flash('Please verify your Gmail address before logging in.', 'warning')
                return redirect(url_for('auth.verify_email', email=user.email, dev_code=user.verification_code))

        # Log in the user
        login_user(user, remember=remember)
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', email=email_prefill)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account with that email was found.', 'danger')
            return render_template('auth/forgot_password.html', email=email)

        if len(new_password) < 6 or new_password != confirm_password:
            flash('Passwords must match and have at least 6 characters.', 'danger')
            return render_template('auth/forgot_password.html', email=email)

        user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully! You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login', email=email))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Securely terminates authenticated session, clears cookies,
    while preserving all user progress and database records.
    """
    user_name = current_user.full_name
    logout_user()
    session.clear()
    flash(f'You have been logged out securely. Your learning progress is saved in the database.', 'info')
    return redirect(url_for('landing'))
