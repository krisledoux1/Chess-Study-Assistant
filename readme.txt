Chess Study Assistant

Chess Study assistant is a slightly different way to analyze your chess games.  It uses Stockfish 17.1.  You open
a PGN file, select the game you want to analyze and the depth to analyze it.  Stockfish will be used to analyze the game.  When all moves have been analyzed the analysis will be saved to your save directory so that you can open it at another time without re-analyzing it.  After saving a display window will open to show you the analysis.  Blunder stats (mild medium and large) blunders will be shown for each player along with points lost and how close to stockfish choices your moves were.

Also displayed are the moves made and Stockfish best 5 suggestions for each move along with the score of the move you made.  A difference column displays how many points were lost on that move compared to Stockfish best selection, which is the first move in the suggested list.  You can click on each move and bring up an interactive chessboard of the position.  This allows you to step through the actual moves of the game, try another move, or recalculate with Stockfish for best move and continuation that can all be viewed dynamically.

Installation

Linux only!  I have not made a Windows version.

Download the repository as a zip (tar) file.  Unzip in the directory of your choice.
After unzipping go to the libs/stockfish_17.1 directory.  Make sure the Stockfish executable has run permissions by right clicking, properties, permissions and check the allow this to run as a program. The Stockfish files included are for Ubuntu.  One for older cpu’s and one for newer cpu’s.  For non Ubuntu Linux systems you will have to either download the appropriate Stockfish for your Linux or set address in script to your systems Stockfish executable.

The location in the scripts for the Stockfish executable file is:
Open the chessclasses.py file in the root directory.
Go to class chess_engine()
in it’s init section is a variable stockfish_location =
Change the right side of the = to the full path of your stockfish executable.
	That variable is currently set to the current working directory +  "/libs/stockfish17_1/stockfish17.1-popcnt"
	This defaults to the older CPU version.  If you have the new CPU then change to that file.
	stockfish-ubuntu-x86-64-avx2

To start script

* open a terminal in the root directory that you placed (unzipped) the project.  
* python3 csa.py

The non standard libraries that are not default in Python are in the libs directory included.  If you already have the libraries installed and it causes interference you can start with the following command.

PYTHONPATH=. python3 -S csa.py


Dependencies

Linux.  This is linux only and not Windows compatible in it's current state. Tested Ubuntu 22.04.1 LTS

The compiled Stockfish included is 17.1 for ubuntu older cpu's without avx2. The Ubuntu with avx2 is included.  If you are not using Ubuntu
you may have to get a compiled Stockfish for your distribution and put it in the folders root/libs/stockfish directory.

Python 3 and it's included libraries.
The other libraries needed are included in the download in the libs directory so do not need to be installed.
The Are,
* python chess
* psutil
* pyautogui
* Stockfish 15.1
* tksheet
* fileexplore
* other libraries that are used by the above libraries.


Abreviated use

The script starts with saved analyzed games listed. The file explorer starting in current directory.  
Double click a .pgn or a .ags file on your system.

PGN file

Opening a pgn file parses the games in the pgn and displays them in a sortable (by names) list. You can change the analysis depth with the pull down if desired.  Low depth is very fast but much less accurate, higher depth is very slow but much more accurate.  This will analyze the whole game.  Time will be dependent on number of moves, depth selected, and CPU speed (and cooling). Time can be 40 seconds to 40 minutes or more. Typically 2 to 10 min. To stop calculations (abort) move mouse to the left of the screen centered from top to bottom.  Hold there until Stockfish finishes next move calculation and stops.
A Stockfish output window will open showing you the progression of the analysis.  When analysis is complete the analysis results window will open.

ags file from saved directory

No analysis will be done.  Immediately opens the analysis results window.

Analysis Results Window

The analysis results window displays the game info and some calculated stats in the top portion.  This includes mild medium and major blunders.  Points lost verses Stockfish moves for the game and for the first ten moves.  The Choice column is an average of your choice vs Stockfish choice.  Lower number is closer to Stockfish with 1.0 being Exactly the same.

The bottom portion of the display is all of the moves of the game.  Your move made.  Stockfish moves recommended with best move first. Diff in score of THAT MOVE from Stockfish best.  Rank of your choice in Stockfish recommendations (6 is out of multipv). Stockfish score of the game after that move.

Clicking of the far left column number will bring up the interactive chessboard with the position at whites move for that selection.

Interactive Chessboard

This board will allow you to view the entire actual continuation of the game from the move selected to the end.  You can move the piece that has the move to any legal square with the mouse.  If the move is different from original continuation, Stockfish will recalculate a continuation. At any time you can have Stockfish recalculate by pressing the new calc button and Stockfish will recalculate a continuation from the current board position.  You can recalculate with any move after that to avoid the Stockfish horizon and be more accurate.  Recalc defaults to depth 25 and multipv of 1 so is reasonably fast.  If the position is complex enough to take a long time you can abort the calculation by moving the mouse to the far left center (top to bottom) of the screen and holding it there until calculation stops. This will only stop calculation when Stockfish get's to the next "depth" so may take a while.
Esc will close board and r will restart interactive board at the move it was started at before.

Reading the whole instructions gives more information but this will get you started.

Note on chess engines
Stockfish, like ANY chess engine is CPU intensive.  CPU intensive use creates HEAT that must be dissipated in some way.  If heat is not dissipated then CPU must be throttled (slowed) to keep from damaging itself.  The operating system does this.  For this reason my desktop PC with a slower CPU (but heat sink and fans) than my laptop analyses the same or faster than my laptop.  Laptop's (not gaming laptop) are built for quiet and slimness so do not have large cpu heat sinks and high airflow fans that make more noise. While the CPU may be faster on paper sustained high CPU intensity tasks tend to slow down.  Chess engines will generally show this.  This will work fine on a laptop but may be slower than expected.

For systems that report CPU temperature (laptops typically do not) I have implemented some CPU protection.  When the CPU temp is greater than 86 C a very short do nothing loop is triggered between each move calculation.  If CPU temp goes above 93 C a several second do nothing kicks in after each move while CPU temp is greater than 93 C.  For systems that do not report CPU temp (most laptops) the script will display 1 C and only the short delay is activated, never the longer delay as operating system must protect CPU.

There debate over whether CPU (chess engines) intensity can damage CPU's with no one truly knowing the definitive answer.  My inclusion of this only slows systems appreciably if temp over 93 C.  On a well cooled system this won't happen often and on a laptop that does not report temperature it will never happen.

End




