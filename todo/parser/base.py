import argparse
from abc import ABCMeta, abstractproperty

from pkg_resources import get_distribution

from todo.renderers import RenderHelp


def set_value(value):
    class Action(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            setattr(args, self.dest, value)

    return Action


def set_default_subparser(self, name, args, positional_args):
    for arg in args:
        if arg in ["-h", "--help"]:
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in args:
                    return
                if sp_name == name:  # check existance of default parser
                    args.insert(positional_args, name)
                    return


argparse.ArgumentParser.set_default_subparser = set_default_subparser


class BaseParser:
    __metaclass__ = ABCMeta

    @abstractproperty
    def command(self):
        raise NotImplementedError

    def __init__(self, command=None):
        self.root_parser = argparse.ArgumentParser()
        self.parent.add_argument(
            "--version",
            action="version",
            help=argparse.SUPPRESS,
            version="td version {version} - (C) Darri Steinn Konn Konradsson".format(
                version=get_distribution("td-cli").version
            ),
        )
        if command is None:
            self.parser = self.root_parser
        else:
            self.parser = self.root_parser.add_subparsers().add_parser(command)

    def _add_arguments(self):
        pass

    def _set_defaults(self, args):
        pass

    def print_help(self):
        RenderHelp(self.__doc__).render()

    def parseopts(self, args):
        self._add_arguments()
        self._set_defaults(args)
        parsed_args = self.root_parser.parse_args(args)
        return (getattr(parsed_args, "command", None) or self.command, parsed_args)
