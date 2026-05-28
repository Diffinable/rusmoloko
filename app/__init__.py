import os
from dotenv import load_dotenv
from flask import Flask
from flasgger import Swagger
from app.routes import stats_bp
from app.db import init_pool

load_dotenv()


def create_app():
    app = Flask(__name__)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
    }
    Swagger(app, config=swagger_config)

    db_config = {
        "dbname": os.getenv("DB_NAME", "farm_db"),
        "user": os.getenv("DB_USER", "user"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", 5432)),
    }
    init_pool(db_config)

    app.register_blueprint(stats_bp)
    return app
