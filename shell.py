import os
import sys
import shlex
import getpass
import socket
import signal
import subprocess
import platform
import types
import inspect

OS_PLATFORM_WINDOWS = "Windows"
os_platform = platform.system()


class BuiltinCommands:

    def __init__(self):
        self.builtin_commands = {}

        import builtin_commands as builtin_src
        for key in dir(builtin_src):
            func = getattr(builtin_src, key)
            if is_command(func):
                self.builtin_commands[key] = func

    def __iter__(self):
        return iter(self.builtin_commands)

    def call(self, key, args):
        return self.builtin_commands[key](args)


class SignalHandler:

    @staticmethod
    def default_SIGINT(signum, frame):
        Shell.print_prompt()

    @staticmethod
    def override_SIGINT(signum, frame):
        if os_platform != OS_PLATFORM_WINDOWS:
            signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)


def register_signals():
    signal.signal(signal.SIGINT, SignalHandler.default_SIGINT)


def is_command(func):
    return inspect.isfunction(func) and len(inspect.signature(func).parameters) == 1


class Shell:
    def __init__(self):
        self.builtinCommands = BuiltinCommands()
        self.cmd = None
        self.tokens = None

    @staticmethod
    def print_prompt():
        user = getpass.getuser()
        hostname = socket.gethostname()
        cwd = os.getcwd()
        base_dir = os.path.basename(cwd)
        home_dir = os.path.expanduser('~')
        if cwd == home_dir:
            base_dir = '~'
        if os_platform != OS_PLATFORM_WINDOWS:
            sys.stdout.write("[\033[1;33m%s\033[0;0m@%s \033[1;36m%s\033[0;0m] $ " % (user, hostname, base_dir))
        else:
            sys.stdout.write("[%s@%s %s]$ " % (user, hostname, base_dir))
        sys.stdout.flush()

    @staticmethod
    def tokenize(string):
        return shlex.split(string)

    def preprocess(self):
        processed_token = []
        for token in Shell.tokenize(self.tokens):
            if token.startswith('$'):
                processed_token.append(os.getenv(token[1:]))
            else:
                processed_token.append(token)
        self.tokens = processed_token

    def execute(self):
        cmd = self.tokens[0]
        args = self.tokens[1:]
        if cmd in self.builtinCommands:
            return self.builtinCommands.call(cmd, args)
        signal.signal(signal.SIGINT, SignalHandler.override_SIGINT)
        if os_platform == OS_PLATFORM_WINDOWS:
            p = subprocess.Popen(self.tokens)
            p.communicate()
        else:
            os.system(self.cmd)
        return True

    def loop(self):
        running = True
        while running:
            self.print_prompt()
            register_signals()
            try:
                self.cmd = sys.stdin.readline()
                self.preprocess()
                running = self.execute()
            except:
                _, err, _ = sys.exc_info()
                print(err)


if __name__ == '__main__':
    shell = Shell()
    shell.loop()
