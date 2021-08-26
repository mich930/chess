# Chess
 This is a simple chess bot written in Python with the help of python-chess. 
 I advise using pypy when running it to speed it up, otherwise it may flag often.
 You can try playing it on lichess.org/@/robocik.

## Features:
 - Negamax algorithm with alpha-beta pruning
 - Piece-Square Tables
 - Move Ordering
 - Capture Search
 - Syzygy Tablebases for 3,4 and 5 pieces
 - Integrated with lichess.org by Berserk

## Hopefully coming soon:
 - Openings Book
 - Zobrist Hashing
 - Transposition Table
 - Iterative Deepening
 - Maybe more...

## How to use?
After installing all the required packages (and preferably pypy) to use this bot you have
to create a BOT account on lichess.org and get yourself a personal API token
(you can get one in "Preferences" on your BOT account) with "Play games with the bot API" permission
and put it into token.txt (make sure its in the first line of the file). After this you're ready to go
and can just start main.py like any standard python script.
In case of any problems open issue or write me directly on m.kostyk22@gmail.com

