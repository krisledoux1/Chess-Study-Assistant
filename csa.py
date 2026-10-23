#! /usr/bin/env python3
##############################################################################################
"""
    Chess Study Assistant scripts to create a graphic study environment for chess
    Copyright (C) 2026  Kristen K LeDoux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
###############################################################################################
#version 1.0.0

import logging
import sys
from logging.handlers import RotatingFileHandler

# 1. Configure the logging layout and storage
logfilename = "csa.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
format = logging.Formatter(fmt="[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
fileHandler = logging.FileHandler(logfilename)
fileHandler = RotatingFileHandler(logfilename, maxBytes=50000, backupCount=5)
fileHandler.setFormatter(format)
logger.addHandler(fileHandler)
# 2. Define a module-level logger
#logger = logging.getLogger(__name__)
# Open log file (buffering=1 forces lines to write immediately)
sys.stderr = open("csa.log", "a", buffering=1)

import tkinter as tk
#from fileexplore import file_is
from chessclasses import pgn_game_lister


if __name__ == "__main__":
    window = tk.Tk()
    app = pgn_game_lister(window)
    window.mainloop()


