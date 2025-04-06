import os
import logging
from flask import Flask

def create_app():
    app = Flask(__name__)

    #  Set the key to use for flash messages
    app.secret_key = "your-secret-key"  # You can customize more complex keys

    #  Set the absolute path of the database
    app.config["DB_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "coursework1", "database", "local_authority_housing.db")
    )

    #  Register Blueprint
    from .routes import main
    app.register_blueprint(main)

    #  Configure logging (only in non-debug mode)
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.info("📦 Flask app started with logging enabled.")

    return app
