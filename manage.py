#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import re
import sys


def load_env():
    try:
        with open('./envs/.env') as f:
            content = f.read()
    except IOError:
        content = ''
    for line in content.splitlines():
        n = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if n:
            key, val = n.group(1), n.group(2)
            os.environ.setdefault(key, val)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitnes_tracker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
