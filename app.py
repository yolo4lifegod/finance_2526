from flask import Flask, render_template
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Seed DesignTeam table from the static DESIGN_TEAMS list if empty
    with app.app_context():
        db.create_all()  # Create all tables first
        from design_teams import DESIGN_TEAMS
        from models import DesignTeam
        try:
            if DesignTeam.query.count() == 0:
                for team_id, team_name in DESIGN_TEAMS:
                    dt = DesignTeam(id=team_id, name=team_name)
                    db.session.add(dt)
                db.session.commit()
        except Exception as e:
            # If there's an error querying, just proceed (tables may not be created yet)
            pass

    # register blueprints / routes
    from routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error_code=404, error_message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error_code=500, error_message="Internal server error"), 500

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('error.html', error_code=400, error_message="Bad request"), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', error_code=403, error_message="Access forbidden"), 403

    return app
