"""cloud environment management commands"""
import argcmdr
from descriptors import cachedproperty

from .. import Project, ROOT_PATH


@Project.register
class Env(argcmdr.Local):
    """cloud environment management commands"""

    environments = {path.name: path for path in ROOT_PATH.joinpath('environment').iterdir()}

    def __init__(self, parser):
        parser.add_argument(
            'env',
            choices=sorted(self.environments),
            help='environment to target',
        )

    @cachedproperty
    def terraform(self):
        try:
            return self.local['terraform'][
                f'-chdir={self.environments[self.args.env]}',
            ]
        except self.local.CommandNotFound:
            parser = self.args.__parser__
            parser.exit(127, f"{parser.prog}: error: command 'terraform' required: "
                             "see https://www.terraform.io/\n")

    @argcmdr.localmethod
    def init(self):
        """(re)-initialize terraform environment"""
        yield self.terraform['init']

    @argcmdr.localmethod
    def plan(self):
        """generate terraform plan"""
        yield self.terraform['plan']

    @argcmdr.localmethod('-y', '--yes', '-auto-approve', action='store_true',
                         help='skip interactive approval of plan before applying')
    def apply(self, args):
        """apply terraform changes"""
        yield self.terraform['apply'][
            ('-auto-approve',) if args.yes else (),
        ]
