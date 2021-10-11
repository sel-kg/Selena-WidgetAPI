import sqlite3
from marshmallow import Schema, fields, validate


class WidgetSchemaValidator(Schema):
    """Complete widget schema"""
    name = fields.Str(
        required=True,
        description="Name of the widget",
        example="The coolest widget",
        validate=validate.Length(min=1, max=64),
    )
    number_of_parts = fields.Int(
        required=True,
        description="How many parts the widget has",
        example=35,
    )
    date_created = fields.DateTime(
        required=False,
        description="The time at which the widget was created in the database",
    )
    date_updated = fields.DateTime(
        required=False,
        description="The time at which the widget was updated in the database",
    )


class SQLiteConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect('widget.db')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()

