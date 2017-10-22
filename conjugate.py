#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
import conjugate_spanish
from conjugate_spanish import Espanol_Dictionary
Espanol_Dictionary.load()
print(sys.argv)
print(Espanol_Dictionary.get(sys.argv[1]))