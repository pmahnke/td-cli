from todo.constants import COMMANDS
from todo.parser.base import BaseParser


class AddGroupParser(BaseParser):
    """
    usage: td add_group [name]
           td ag [name]

    positional arguments:
      name        the new group's name

    optional arguments:
      -h, --help  show this help message and exit
    """

    command = COMMANDS.ADD_GROUP

    def _add_arguments(self):
        self.parser.add_argument("name", action="store", help="the new group's name")