import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import Config
from models import db, User
from routes import auth_bp, dashboard_bp, learn_bp, terminal_bp, assessment_bp, certificate_bp, code_bp
from database.seed_data import seed_curriculum

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access the requested resource.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(terminal_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(certificate_bp)
    app.register_blueprint(code_bp)

    # Landing page route
    @app.route('/')
    def landing():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('landing.html')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Ensure database tables exist & seed on startup
    with app.app_context():
        try:
            db.create_all()
            seed_curriculum()
        except Exception as e:
            app.logger.warning(f"Database initialization notice: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
