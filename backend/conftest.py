import pytest
from app import app as main_app, db

from dotenv import load_dotenv  # <-- ADD THIS
import os                       # <-- ADD THIS

load_dotenv()

@pytest.fixture(scope='module')
def app():
    # Set test config
    main_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"mysql+mysqlconnector://root:{os.environ.get('DB_PASSWORD')}@127.0.0.1/test_project_management_tool"
    })

    # --- IMPORTANT ---
    # Make sure to change the password above ("Gudu%402005") 
    # to your URL-encoded MySQL password, just like in your app.py
    # ---

    # Create tables
    with main_app.app_context():
        db.create_all()

    yield main_app

    # Drop tables
    with main_app.app_context():
        db.drop_all()

# This fixture is provided by pytest-flask and uses the 'app' fixture above
@pytest.fixture(scope='module')
def client(app):
    return app.test_client()