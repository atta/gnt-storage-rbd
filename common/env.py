# Copyright (C) 2013
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
Created on 12.02.2013

@author: ajazdzewski
'''

import os
import sys


class Env(object):
    """Read and validate the Enviroment variables."""

    def get(self, name):
        """Wrap os.getenv."""
        value = os.getenv(name)
        if value is None:
            sys.stderr.write('The environment variable ' +
                             name + ' is missing.\n')
            return None
        return value
