from flask import Flask

from app.controllers.main_controller import main_bp
from app.models.database import init_db


def create_app() -> Flask:
    """Application factory for the Career & Education Advisor."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "career-education-advisor-secret"
    app.config["DATABASE"] = "career_advisor.db"

    init_db(app)
    app.register_blueprint(main_bp)
    return app
