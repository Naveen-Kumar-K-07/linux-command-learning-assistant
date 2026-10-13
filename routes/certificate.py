import secrets
import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from models import db, Certificate
from services.progress_service import ProgressService
from services.pdf_generator import CertificatePDFGenerator

certificate_bp = Blueprint('certificate', __name__)

@certificate_bp.route('/certification')
@login_required
def index():
    """
    Renders Certification dashboard showing user learning progress,
    assessment results, checklist of criteria, and unlocked/earned certificates.
    """
    eligibility = ProgressService.check_certification_eligibility(current_user.id)
    user_certs = Certificate.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'certificate/index.html',
        eligibility=eligibility,
        certificates=user_certs
    )

@certificate_bp.route('/certification/issue', methods=['POST'])
@login_required
def issue_certificate():
    """
    Verifies eligibility on backend before issuing official certificate.
    Prevents unauthorized or spoofed generation.
    """
    eligibility = ProgressService.check_certification_eligibility(current_user.id)
    if not eligibility['eligible']:
        flash('You do not meet the certification criteria yet. Please fulfill all requirements.', 'danger')
        return redirect(url_for('certificate.index'))

    # Check if user already has an issued certificate
    existing = Certificate.query.filter_by(user_id=current_user.id).first()
    if existing:
        flash('Your certificate has already been issued! You can download it below.', 'info')
        return redirect(url_for('certificate.index'))

    # Generate unique Certificate ID
    token_suffix = secrets.token_hex(4).upper()
    cert_id = f"LCLA-{datetime.now().year}-{token_suffix}"
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.strftime('%Y-%m-%d %H:%M:%S')

    v_hash = Certificate.generate_hash(cert_id, current_user.id, current_user.email, now_str)

    summary = {
        'completion_percentage': eligibility['completion_percentage'],
        'completed_lessons': eligibility['completed_lessons'],
        'passed_quizzes': eligibility['passed_quizzes']
    }

    cert = Certificate(
        certificate_id=cert_id,
        user_id=current_user.id,
        course_name='Linux Commands Learning Assistant — Professional Mastery',
        issue_date=now_utc,
        verification_hash=v_hash,
        criteria_summary_json=json.dumps(summary),
        download_count=0
    )
    db.session.add(cert)
    db.session.commit()

    flash('Congratulations! Your official Linux Certificate of Competency has been issued.', 'success')
    return redirect(url_for('certificate.index'))

@certificate_bp.route('/certification/download/<cert_id>')
@login_required
def download_pdf(cert_id):
    """
    Generates and streams downloadable vector PDF certificate.
    Verifies user ownership or admin authority.
    """
    cert = Certificate.query.filter_by(certificate_id=cert_id, user_id=current_user.id).first_or_404()
    cert.download_count += 1
    db.session.commit()

    user_name = current_user.full_name
    issue_date_str = cert.issue_date.strftime('%B %d, %Y')

    pdf_buffer = CertificatePDFGenerator.generate(
        user_name=user_name,
        certificate_id=cert.certificate_id,
        issue_date_str=issue_date_str,
        course_name=cert.course_name,
        verification_hash=cert.verification_hash
    )

    filename = f"Certificate_{cert.certificate_id}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@certificate_bp.route('/verify-certificate/<cert_id>')
def verify_public(cert_id):
    """
    Publicly accessible certificate verification endpoint for employers and validators.
    """
    cert = Certificate.query.filter_by(certificate_id=cert_id).first()
    return render_template('certificate/verify.html', cert=cert, cert_id=cert_id)
