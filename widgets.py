from datetime import datetime


class Widget:
    """A Widget class"""

    def __init__(self, name, num_parts, create):
        self.name: str = name
        self.num_parts: int = num_parts
        self.date_created = ''
        self.date_updated = ''
        if create:
            self.date_created = datetime.now()
        else:
            self.date_updated = datetime.now()

    def __repr__(self):
        return "Widget('{}', '{}', {}, {})".format(self.name, self.num_parts, self.date_created, self.date_updated)