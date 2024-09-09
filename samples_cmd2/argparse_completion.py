#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# bxtctl is command line client designed to interact with bxt api
# bxt can be found at https://gitlab.com/anydistro/bxt
#
# bxtctl is free software: you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# bxtctl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public License
# along with bxtctl.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Frede Hundewadt https://github.com/fhdk/bxtctl
#

import argparse
import json
import time

import cmd2
import requests
from cmd2 import Cmd2ArgumentParser, with_argparser
import sys
from Bxt.BxtAcl import BxtAcl
from Bxt.BxtConfig import BxtConfig
from Bxt.BxtSession import BxtSession
import jwt
from pprint import pprint
import os
import argparse
from typing import (
    Dict,
    List,
)

from cmd2 import (
    Cmd,
    Cmd2ArgumentParser,
    CompletionError,
    CompletionItem,
    ansi,
    with_argparser,
)

# Data source for argparse.choices
food_item_strs = ["Pizza", "Ham", "Ham Sandwich", "Potato"]
config = BxtConfig()


class ArgparseCompletion(Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sport_item_strs = ["Bat", "Basket", "Basketball", "Football", "Space Ball"]

    def choices_provider(self) -> List[str]:
        """A choices provider is useful when the choice list is based on instance data of your application"""
        return self.sport_item_strs

    def choices_completion_error(self) -> List[str]:
        """
        CompletionErrors can be raised if an error occurs while tab completing.

        Example use cases
            - Reading a database to retrieve a tab completion data set failed
            - A previous command line argument that determines the data set being completed is invalid
        """
        if self.debug:
            return self.sport_item_strs
        raise CompletionError("debug must be true")

    # noinspection PyMethodMayBeStatic
    def choices_completion_item(self) -> List[CompletionItem]:
        """Return CompletionItem instead of strings. These give more context to what's being tab completed."""
        fancy_item = "These things can\ncontain newlines and\n"
        fancy_item += ansi.style(
            "styled text!!", fg=ansi.Fg.LIGHT_YELLOW, underline=True
        )
        items = {1: "My item", 2: "Another item", 3: "Yet another item", 4: fancy_item}
        return [
            CompletionItem(item_id, description)
            for item_id, description in items.items()
        ]

    # noinspection PyMethodMayBeStatic
    def choices_arg_tokens(self, arg_tokens: Dict[str, List[str]]) -> List[str]:
        """
        If a choices or completer function/method takes a value called arg_tokens, then it will be
        passed a dictionary that maps the command line tokens up through the one being completed
        to their argparse argument name.  All values of the arg_tokens dictionary are lists, even if
        a particular argument expects only 1 token.
        """
        # Check if choices_provider flag has appeared
        values = ["choices_provider", "flag"]
        if "choices_provider" in arg_tokens:
            values.append("is {}".format(arg_tokens["choices_provider"][0]))
        else:
            values.append("not supplied")
        return values

    # Parser for example command
    example_parser = Cmd2ArgumentParser(
        description="Command demonstrating tab completion with argparse\n"
        "Notice even the flags of this command tab complete"
    )

    # Tab complete from a list using argparse choices. Set metavar if you don't
    # want the entire choices list showing in the usage text for this command.
    example_parser.add_argument(
        "--choices",
        choices=food_item_strs,
        metavar="CHOICE",
        help="tab complete using choices",
    )

    # Tab complete from choices provided by a choices_provider
    example_parser.add_argument(
        "--choices_provider",
        choices_provider=choices_provider,
        help="tab complete using a choices_provider",
    )

    # Tab complete using a completer
    example_parser.add_argument(
        "--completer",
        completer=Cmd.path_complete,
        help="tab complete using a completer",
    )

    # Demonstrate raising a CompletionError while tab completing
    example_parser.add_argument(
        "--completion_error",
        choices_provider=choices_completion_error,
        help="raise a CompletionError while tab completing if debug is False",
    )

    # Demonstrate returning CompletionItems instead of strings
    example_parser.add_argument(
        "--completion_item",
        choices_provider=choices_completion_item,
        metavar="ITEM_ID",
        descriptive_header="Description",
        help="demonstrate use of CompletionItems",
    )

    # Demonstrate use of arg_tokens dictionary
    example_parser.add_argument(
        "--arg_tokens",
        choices_provider=choices_arg_tokens,
        help="demonstrate use of arg_tokens dictionary",
    )

    @with_argparser(example_parser)
    def do_example(self, _: argparse.Namespace) -> None:
        """The example command"""
        self.poutput("I do nothing")


if __name__ == "__main__":
    import sys

    app = ArgparseCompletion()
    sys.exit(app.cmdloop())
