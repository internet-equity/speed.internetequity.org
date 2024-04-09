"""local development commands"""
import os
import pathlib
import stat
import tempfile
import urllib.request
import sys
import zipfile

import argcmdr
from descriptors import cachedproperty

from .. import Project, ROOT_PATH


@Project.register
class Dev(argcmdr.Local):
    """local development commands"""

    local_bin = ROOT_PATH / '.bin'
    local_lib = ROOT_PATH / '.lib'

    public_path = ROOT_PATH / 'public'
    sam_path = ROOT_PATH / 'sam.yaml'

    sam_package_url = ('https://github.com/aws/aws-sam-cli/releases/latest/download/'
                       'aws-sam-cli-linux-x86_64.zip')

    @staticmethod
    def installation_paths():
        """set of paths on PATH to which this user might install a new executable"""
        return {pathlib.Path(path).absolute()
                for path in os.getenv('PATH').split(':')
                if os.access(path, os.W_OK)}

    @classmethod
    def lib_path(cls, bin_path, lib_name):
        """given a `bin_path` to which an executable will be installed,
        select an appropriate path to which to install its libraries,
        with the (long) name `lib_name`

        """
        if bin_path == cls.local_bin:
            return cls.local_lib / lib_name

        home = pathlib.Path.home()
        home_lib = home / '.local'

        if bin_path.is_relative_to(home_lib):
            return home_lib / 'lib' / lib_name

        if bin_path.is_relative_to(home):
            return home / f'.{lib_name}'

        return pathlib.Path('/usr/local/lib/') / lib_name

    @staticmethod
    def prompt_select(options):
        """prompt the user to select an option from the given sequence.

        returns the index of the selected option or `None` if no valid
        response was given.

        """
        value = input(f'Enter an option above (1-{len(options)}): ')

        try:
            option = int(value)
        except ValueError:
            pass
        else:
            if 1 <= option <= len(options):
                return option - 1

        return None

    @classmethod
    def select_path(cls, lib_name):
        """prompt user to select a suggested installation path or
        confirm a singular such path.

        in addition to system-detected paths, a hidden directory under
        the current directory is suggested. (but utility-dedicated paths
        -- namely those of Pyenv -- are not suggested.)

        """
        executables = sorted(path for path in cls.installation_paths()
                             if '.pyenv' not in path.parts)

        if cls.local_bin not in executables:
            executables.append(cls.local_bin)

        paths = [(bin_path, cls.lib_path(bin_path, lib_name)) for bin_path in executables]

        if len(paths) == 1:
            print('The following installation paths have been automatically selected:', end='\n\n')

            ((bin_path, lib_path),) = paths

            print('  ', bin_path, sep='')
            print('  ', lib_path, sep='', end='\n\n')

            input('Press <enter> to install to the above paths ... ')

            return (bin_path, lib_path)

        print('Select a set of installation paths from the following detected options:',
              end='\n\n')

        for (option, (bin_path, lib_path)) in enumerate(paths, 1):
            print(f'  {option: >{len(paths) // 10 + 1}})', bin_path, '->', lib_path)

        print()

        while (selection := cls.prompt_select(paths)) is None:
            pass

        return paths[selection]

    def install_sam(self):
        """install AWS SAM CLI to a user-selected path"""
        (sam_bin, sam_lib) = self.select_path('aws-sam-cli')

        sam_installed = sam_bin / 'sam'

        if self.args.execute_commands:
            with tempfile.TemporaryDirectory() as staging:
                (package, _headers) = urllib.request.urlretrieve(self.sam_package_url)

                with zipfile.ZipFile(package) as zipd:
                    # NOTE: extractall() fails to preserve file permissions
                    # https://bugs.python.org/issue15795
                    zipd.extractall(staging)

                installer = pathlib.Path(staging) / 'install'

                # NOTE: see above
                sam_dist = pathlib.Path(staging) / 'dist' / 'sam'
                for package_path in (installer, sam_dist):
                    os.chmod(package_path, os.stat(package_path).st_mode | stat.S_IEXEC)

                self.local[installer](
                    '--bin-dir', sam_bin,
                    '--install-dir', sam_lib,
                )

        return sam_installed

    @cachedproperty
    def sam(self):
        """LocalCommand for AWS SAM CLI.

        This library is installed, with user confirmation, if necessary.

        """
        sam_local = self.local_bin.joinpath('sam')
        if sam_local.exists():
            return self.local[sam_local]

        try:
            return self.local['sam']
        except self.local.CommandNotFound:
            pass

        print('= AWS SAM CLI (sam) not found =', end='\n\n')

        sam_installed = self.install_sam()

        print('\n= AWS SAM CLI (sam) now installed =', end='\n\n')

        if not self.args.execute_commands:
            # not actually installed so don't go through PATH
            return self.local[sam_installed]

        # installed so sure as heck should work this time
        return self.sam

    @cachedproperty
    def ampersand(self):
        """LocalCommand background modifier operating like '&' in shell"""
        return self.local.BG(
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    @argcmdr.localmethod
    def serve(self):
        """serve app's api & public/static assets"""
        future = yield self.ampersand, self.sam[
            'local',
            'start-api',
            '--warm-containers', 'eager',
            '--template', self.sam_path,
        ]

        print('app index will be available at:', end='\n\n')
        print('  http://127.0.0.1:3000/index.html?apiUri=http://127.0.0.1:3000/speedtest/',
              end='\n\n')

        print('results will be available within the Docker container at:', end='\n\n')
        print('  /tmp/speedtest/', end='\n\n')

        if future and future != (None, None, None):
            # https://github.com/dssg/argcmdr/issues/33
            future.wait()

        #
        # Note: We can quite easily serve static assets, even in-process, via Python.
        #
        # However: So can SAM (and it does so by default for the public/ directory).
        #
        #     import http.server
        #
        #     os.chdir(self.public_path)
        #
        #     http.server.test(
        #         HandlerClass=http.server.SimpleHTTPRequestHandler,
        #     )
