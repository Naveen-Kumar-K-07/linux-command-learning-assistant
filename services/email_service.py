import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

class EmailService:
    @staticmethod
    def send_verification_email(user_email, user_name, code, token):
        """
        Sends email verification containing code and activation link.
        If SMTP server is configured, sends via Gmail SMTP;
        Otherwise logs in dev mode and returns code.
        """
        app = current_app
        mail_user = app.config.get('MAIL_USERNAME')
        mail_pass = app.config.get('MAIL_PASSWORD')
        mail_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = app.config.get('MAIL_PORT', 587)

        subject = "Verify your Linux Commands Learning Assistant Account"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #1e293b; padding: 30px; border-radius: 8px; border: 1px solid #10b981;">
                <h2 style="color: #10b981; margin-top: 0;">Linux Commands Learning Assistant</h2>
                <p>Hello <strong>{user_name}</strong>,</p>
                <p>Thank you for registering on the Linux Commands Learning Assistant platform. Please confirm your Gmail address using the 6-digit verification code below:</p>
                <div style="background: #0f172a; padding: 15px; border-radius: 6px; text-align: center; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #38bdf8;">{code}</span>
                </div>
                <p style="color: #94a3b8; font-size: 13px;">If you did not request this registration, you can safely ignore this email.</p>
            </div>
        </body>
        </html>
        """

        if mail_user and mail_pass:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = app.config.get('MAIL_DEFAULT_SENDER', mail_user)
                msg['To'] = user_email
                msg.attach(MIMEText(html_content, 'html'))

                server = smtplib.SMTP(mail_server, mail_port, timeout=10)
                if app.config.get('MAIL_USE_TLS', True):
                    server.starttls()
                server.login(mail_user, mail_pass)
                server.sendmail(msg['From'], [user_email], msg.as_string())
                server.quit()
                return True, "Verification email sent successfully to your Gmail address."
            except Exception as e:
                app.logger.warning(f"Failed to send email via SMTP: {e}")
                return False, f"Email delivery note: {str(e)}"
        else:
            # Dev mode fallback
            app.logger.info(f"[DEV_MODE] Gmail verification code for {user_email}: {code}")
            return True, f"Development Mode: Your verification code is {code}"
