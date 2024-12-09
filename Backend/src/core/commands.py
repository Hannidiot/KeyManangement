import click
from flask.cli import with_appcontext
from extensions import db

def register_commands(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Initialized the database.') 