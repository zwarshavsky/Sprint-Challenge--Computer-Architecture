#!/usr/bin/env python3

"""Main."""

import sys
from cpu_2 import *

program_filename = sys.argv[1]

cpu = CPU()

cpu.load(program_filename)
cpu.run()