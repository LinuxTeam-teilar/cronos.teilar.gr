#!/usr/bin/env python
# manage.py script of cronos

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cronos.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
