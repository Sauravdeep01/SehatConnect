"""
WSGI config for sehatconnect_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sehatconnect_project.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

# If running in Vercel serverless environment and using SQLite, ensure /tmp/db.sqlite3 is initialized
if 'VERCEL' in os.environ and ('DATABASE_URL' not in os.environ or not os.environ['DATABASE_URL']):
    tmp_db = Path('/tmp/db.sqlite3')
    src_db = BASE_DIR / 'db.sqlite3'
    try:
        if not tmp_db.exists() and src_db.exists():
            shutil.copyfile(src_db, tmp_db)
        elif not tmp_db.exists():
            # If src_db doesn't exist, create tables and seed data
            import django
            django.setup()
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            call_command('seed_data')
    except Exception as e:
        print("Vercel DB initialization error:", e)

application = get_wsgi_application()
app = application
