from tornado.web import Application, RequestHandler
import tornado.ioloop
import json
from widgets import Widget
from utils import SQLiteConnection, WidgetSchemaValidator
from init_swagger import generate_swagger_file
import swagger_ui

SWAGGER_API_OUTPUT_FILE = "./swagger.json"


class WidgetsAPI(RequestHandler):

    def post(self):
        """Adds new widget into our "database"
        ---
        tags: [AWeber widgets]
        summary: Create a widget
        description: Create a new widget
        requestBody:
            description: New Widget Data
            required: True
            content:
                application/json:
                    schema:
                        WidgetSchemaValidator
        responses:
            201:
                description: Success payload containing newly created widget information
                content:
                    application/json:
                        schema:
                            WidgetSchemaValidator
            400:
                description: Bad request; Attached request body has validation errors
                content:
                    application/json:
                        schema:
                            BadRequestSchema
        """
        api_input = json.loads(self.request.body)
        widget_validator = WidgetSchemaValidator()
        validation_errors = widget_validator.validate(api_input)
        if validation_errors:
            self.set_status(400)
            self.write({"success": False, "errors": validation_errors})
        else:
            widget = Widget(api_input['name'], api_input['number_of_parts'], create=True)
            widget_db = SQLiteConnection()
            with widget_db:
                c = widget_db.connection.cursor()
                c.execute("INSERT INTO Widgets VALUES (:name, :number_of_parts, :date_created, :date_updated)",
                          {'name': widget.name, 'number_of_parts': widget.num_parts,
                           'date_created': widget.date_created, 'date_updated': widget.date_updated})
                self.set_status(201)
                self.write({'success': True, 'Widget': json.dumps(widget, indent=4, sort_keys=True, default=str)})

    def get(self):
        """Returns all widgets from our "database"
        ---
        tags: [AWeber Widgets]
        summary: Get widgets
        description: Get all the widgets
        responses:
            200:
                description: List of widgets
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                WidgetSchemaValidator
        """
        widget_db = SQLiteConnection()
        with widget_db:
            c = widget_db.connection.cursor()
            c.execute("SELECT * FROM Widgets")
            self.set_status(200)
            self.write({'widgets': c.fetchall()})

    def put(self):
        """Updates existing widget in our database
        ---
        tags: [AWeber Widgets]
        summary: Update a widget or create new one
        description: Update a widget if exists or creates a new one
        requestBody:
            description: Update Widget
            required: True
            content:
                application/json:
                    schema:
                        WidgetSchemaValidator
        responses:
            201:
                description: Success payload containing updated widget information
                content:
                    application/json:
                        schema:
                            WidgetSchemaValidator
            400:
                description: Bad request; Check `errors` for any validation errors
                content:
                    application/json:
                        schema:
                            BadRequest
        """
        api_input = json.loads(self.request.body)
        widget_validator = WidgetSchemaValidator()
        validation_errors = widget_validator.validate(api_input)
        if validation_errors:
            self.set_status(400)
            self.write({"success": False, "errors": validation_errors})
        else:
            widget = Widget(api_input['name'], api_input['number_of_parts'], create=False)
            widget_db = SQLiteConnection()
            with widget_db:
                c = widget_db.connection.cursor()
                c.execute("""UPDATE Widgets SET number_of_parts = :number_of_parts, date_updated = :date_updated
                          WHERE name = :name""",
                          {'name': widget.name, 'number_of_parts': widget.num_parts,
                           'date_updated': widget.date_updated})
                self.set_status(201)
                self.write({'success': True, 'Widget_Updated': json.dumps(widget, indent=4, sort_keys=True, default=str)})

    def delete(self):
        """Delete widget from database with specified name and number of parts
        ---
        tags: [AWeber Widgets]
        summary: Delete widget by name and number of parts
        description: Delete widget by name and number of parts
        responses:
            200:
                description: Widget deleted
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                WidgetSchemaValidator
        """
        api_input = json.loads(self.request.body)
        widget_validator = WidgetSchemaValidator()
        validation_errors = widget_validator.validate(api_input)
        if validation_errors:
            self.set_status(400)
            self.write({"success": False, "errors": validation_errors})
        else:
            widget_db = SQLiteConnection()
            with widget_db:
                c = widget_db.connection.cursor()
                c.execute("DELETE from Widgets WHERE name = :name AND number_of_parts = :number_of_parts",
                          {'name': api_input['name'], 'number_of_parts': api_input['number_of_parts']})
                self.set_status(200)
                self.write({'widget_deleted': f'name-{api_input["name"]}, '
                                              f'number_of_parts-{api_input["number_of_parts"]}'})


class WidgetAPI(RequestHandler):

    def get(self, name):
        """Return widgets from database with specified name
        ---
        tags: [AWeber Widgets]
        summary: Get widget by name
        description: Get widgets by name
        responses:
            200:
                description: List of widgets
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                WidgetSchemaValidator
        """
        widget_db = SQLiteConnection()
        with widget_db:
            c = widget_db.connection.cursor()
            c.execute("SELECT * FROM Widgets WHERE name = :name", {'name': name})
            self.set_status(200)
            self.write({'widgets': c.fetchall()})

    def delete(self, name):
        """Delete widget from database with specified name
        ---
        tags: [AWeber Widgets]
        summary: Delete widget by name
        description: Delete widget by name
        responses:
            200:
                description: Widget deleted
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                WidgetSchemaValidator
        """
        widget_db = SQLiteConnection()
        with widget_db:
            c = widget_db.connection.cursor()
            c.execute("DELETE from Widgets WHERE name = :name", {'name': name})
            self.set_status(200)
            self.write({'widget_deleted': name})


def make_app():
    handlers = [
        ("/widget/", WidgetsAPI),
        (r"/widget/([^/]+)?", WidgetAPI)
    ]

    app = Application(handlers, debug=True)

    # Generate a fresh Swagger file
    generate_swagger_file(handlers=handlers, file_location=SWAGGER_API_OUTPUT_FILE)

    # Start the Swagger UI. Automatically generated swagger.json
    swagger_ui.api_doc(
        app,
        config_path=SWAGGER_API_OUTPUT_FILE,
        url_prefix="/swagger/spec.html",
        title="AWeber Widget API",
    )
    return app


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
