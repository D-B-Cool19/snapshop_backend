import os
from flask_migrate import upgrade, migrate, init
from app import create_app

app = create_app()

with app.app_context():
    if not os.path.exists('migrations'):
        print("Initializing migration environment...")
        init()

    print("Generating migration script...")
    migrate(message="Auto migration")

    print("Applying migration to database...")
    upgrade()

    print("Migration complete!")
