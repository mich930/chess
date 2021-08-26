import time
from collections import namedtuple
import chess
import chess.syzygy
import random

#board = chess.Board('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPB1PPP/R3KB1R w KQkq - 0 1')
board = chess.Board()

MAX_SIZE = 1e6
TIME_LIMIT = 0
EVAL_LIMIT = 20
QS_LIMIT = 219
CHECKMATE = 20000
DRAW = 0
MAX_DEPTH = 3
AI_COLOR = chess.BLACK
ENDGAME_START = 2*1340
CASTLE_VALUE = 25

d = 0
counter = 0
bestMove = None
pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100, "k": 0, "q": -900, "r": -500, "b": -330,
              "n": -320, "p": -100}
hashTable = [[0 for x in range(12)] for y in range(64)]
castlingHash = [0, 0, 0, 0]
enPassantHash = [0, 0, 0, 0, 0, 0, 0, 0]
nextToMoveHash = 0
white,black = [], []
hashedPositions = {}
hash = 0


def init_heat_maps():
    global white, black

    # They have to be flipped cause that's how library works - PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING (middle) #todo - KING(end)

    white = [
        [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, -20, -20, 10, 10, 5,
            5, -5, -10, 0, 0, -10, -5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, 5, 10, 25, 25, 10, 5, 5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ],
        [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ],
        [
            0, 0, 0, 5, 5, 0, 0, 0,
            - 5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            5, 10, 10, 10, 10, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            0, 0, 5, 5, 5, 5, 0, -5,
            -5, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ],
        [
            20, 30, 10, 0, 0, 10, 30, 20,
            20, 20, 0, 0, 0, 0, 20, 20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30
        ]
    ]

    black = [
        [
            0, 0, 0, 0, 0, 0, 0, 0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5, 5, 10, 25, 25, 10, 5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, -5, -10, 0, 0, -10, -5, 5,
            5, 10, 10, -20, -20, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ],
        [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ],
        [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, 10, 10, 10, 10, 5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            0, 0, 0, 5, 5, 0, 0, 0
        ],
        [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -5, 0, 5, 5, 5, 5, 0, -5,
            0, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ],
        [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20, 0, 0, 0, 0, 20, 20,
            20, 30, 10, 0, 0, 10, 30, 20
        ]
    ]


def piece_id(square):
    piece = board.piece_type_at(square)
    if piece is None:
        return None

    if board.color_at(square) == chess.BLACK:
        piece += 6  # black pieces have numbers 6-11, white ones have 0-5

    return piece - 1


def init_hashing():
    global nextToMoveHash, hashTable

    nextToMoveHash = random.randint(0, 2 ** 64 - 1)
    for i in range(64):  # loop over the board
        for j in range(12):  # loop over the pieces
            hashTable[i][j] = random.randint(0, 2 ** 64 - 1)

    for i in range(4):
        castlingHash[i] = random.randint(0, 2 ** 64 - 1)

    for i in range(8):
        enPassantHash[i] = random.randint(0, 2 ** 64 - 1)


def hashing():
    h = 0
    for i in range(64):
        piece = piece_id(i)
        if not (piece is None):
            h = h ^ hashTable[i][piece]

    if board.turn == chess.BLACK:
        h = h ^ nextToMoveHash

    # castling
    if board.has_kingside_castling_rights(chess.WHITE):
        h = h ^ castlingHash[0]
    if board.has_queenside_castling_rights(chess.WHITE):
        h = h ^ castlingHash[1]

    if board.has_kingside_castling_rights(chess.BLACK):
        h = h ^ castlingHash[2]
    if board.has_queenside_castling_rights(chess.BLACK):
        h = h ^ castlingHash[3]

    #todo - en passant

    print(h)
    return h


def hash_move(move):  # cause it uses xor, hash move is basically the same as hash_unmove, pretty nice trick
    global hash
    startingSquare = move.from_square
    endingSquare = move.to_square

    startingSquarePiece = piece_id(startingSquare)
    endingSquarePiece = piece_id(endingSquare)

    hash = hash ^ hashTable[startingSquare][startingSquarePiece]
    hash = hash ^ hashTable[endingSquare][startingSquarePiece]
    hash = hash ^ nextToMoveHash

    if not (endingSquarePiece is None):
        hash = hash ^ hashTable[endingSquare][endingSquarePiece]

    #todo - castling


def evaluation():
    global counter
    counter += 1
    value = 0
    if board.is_checkmate():
        return CHECKMATE - MAX_DEPTH

    pieces = board.piece_map()
    castling = board.castling_rights

    if castling & chess.BB_H1:
        value += CASTLE_VALUE
    if castling & chess.BB_A1:
        value += CASTLE_VALUE

    if castling & chess.BB_H8:
        value -= CASTLE_VALUE
    if castling & chess.BB_A8:
        value -= CASTLE_VALUE

    if len(pieces) <= 5:
        with chess.syzygy.open_tablebase("3-4-5piecesSyzygy/3-4-5") as tablebase:
            wdl = tablebase.get_wdl(board)
            dtz = tablebase.get_dtz(board)
            if wdl == 2 and dtz <= (50 - board.halfmove_clock) * 2:
                return CHECKMATE - dtz
            if wdl == 1 or (wdl == 2 and dtz > (50 - board.halfmove_clock) * 2):
                return CHECKMATE / 2 - dtz
            if wdl == 0:
                return DRAW
            if wdl == -1 or (wdl == -2 and -dtz > (50 - board.halfmove_clock) * 2):
                return -CHECKMATE / 2 + dtz
            if wdl == -2 and -dtz <= (50 - board.halfmove_clock) * 2:
                return -CHECKMATE + dtz

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return DRAW

    totalMaterialWithoutPawns = 0

    for square in pieces:

        piece = board.piece_at(square)
        pieceID = piece.piece_type-1
        if pieceID > 1:
            totalMaterialWithoutPawns += pieceScore[pieceID]

        if piece.color == chess.WHITE:
            value += white[pieceID][square]
            value += pieceScore[pieceID]
        else:
            value -= black[pieceID][square]
            value -= pieceScore[pieceID]

    if totalMaterialWithoutPawns < ENDGAME_START:

        for square in pieces:

            piece = board.piece_at(square)
            pieceID = piece.piece_type - 1
            if pieceID < 5:
                continue

            multiplier = (ENDGAME_START-totalMaterialWithoutPawns)/1000

            if piece.color == chess.WHITE:
                value += white[6][square]*multiplier #adding endgame value
                value -= white[5][square]*multiplier #substracting middlegame value
            else:
                value -= black[6][square]*multiplier
                value += black[5][square]*multiplier

    if board.turn == chess.WHITE:
        return value
    else:
        return -value


def pre_evaluation(move):

    fromSquare = move.from_square
    toSquare = move.to_square
    fromPiece = (board.piece_type_at(fromSquare))-1
    toPiece = (board.piece_type_at(toSquare))

    movePreEval = 0

    if board.turn == chess.WHITE:
        movePreEval = white[fromPiece][toSquare] - white[fromPiece][fromSquare]
    if board.turn == chess.BLACK:
        movePreEval = black[fromPiece][toSquare] - black[fromPiece][fromSquare]
    #movePreEval = 0

    if toPiece is not None:
        toPiece = toPiece-1
        movePreEval += 10 * pieceScore[toPiece] - pieceScore[fromPiece]  # captures are good (10?)

    if move.promotion is not None:
        movePreEval += 800  # promotions are good

    #if board.is_attacked_by(not board.turn, toSquare):
        #movePreEval -= pieceScore[fromPiece]  # attacked squares are bad

    return movePreEval


def capture_search(alpha, beta):
    eval = evaluation()

    if eval >= beta:
        return beta

    if eval > alpha:
        alpha = eval

    newMoves = board.legal_moves
    captureMoves = []

    for move in newMoves:
        if board.is_capture(move) or board.gives_check(move) or board.is_check():
            captureMoves.append((pre_evaluation(move), move.uci()))

    captureMoves.sort(reverse=True)

    for captureMove in captureMoves:
        move = chess.Move.from_uci(captureMove[1])

        board.push(move)
        eval = -capture_search(-beta, -alpha)
        board.pop()

        if eval >= beta:
            return beta

        if eval > alpha:
            alpha = eval

    return alpha


def find_move(depth, alpha, beta):
    global bestMove,bestEval,d
    #bestMoveInPosition = {}
    #fen = board.fen()

    if not hashedPositions.get(hash) is None and hashedPositions[hash][1] >= depth:
        return hashedPositions[hash][0]

    if board.is_checkmate():
        hashedPositions[hash] = (-(CHECKMATE - (MAX_DEPTH - depth)), depth, '')
        return -(CHECKMATE - (MAX_DEPTH - depth))

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        hashedPositions[hash] = (DRAW, depth, '')
        return DRAW

    if depth == 0:
        return capture_search(alpha, beta)

    newMoves = board.legal_moves
    orderedMoves = []

    for move in newMoves:
        orderedMoves.append((pre_evaluation(move), move.uci()))

    orderedMoves.sort(reverse=True)

    for orderedMove in orderedMoves:
        move = chess.Move.from_uci(orderedMove[1])
        board.push(move)
        eval = -find_move(depth - 1, -beta, -alpha)

        board.pop()

        if eval == CHECKMATE and depth == MAX_DEPTH:
            bestMove = move
            bestEval = eval
            return

        if eval >= beta:
            hashedPositions[hash] = (beta, depth, '')
            return beta

        if eval > alpha:
            alpha = eval
            bestMoveInPosition = move
            if depth == MAX_DEPTH:
                bestMove = move
                bestEval = eval

    hashedPositions[hash] = (alpha, depth, bestMoveInPosition)
    return alpha

init_heat_maps()

#find_move(MAX_DEPTH, -CHECKMATE, CHECKMATE)

while not (board.is_checkmate() or board.is_stalemate() or board.can_claim_draw() or board.is_insufficient_material()):
    legalMoves = board.legal_moves

    print(board)

    if board.turn != AI_COLOR:
        counter = 0
        moveString = input("Podaj ruch:")
        move = chess.Move.from_uci(moveString)

        while not (move in legalMoves):
            moveString = input("Podaj ruch:")
            move = chess.Move.from_uci(moveString)

        board.push_san(moveString)

    if board.turn == AI_COLOR:
        find_move(MAX_DEPTH, -CHECKMATE, CHECKMATE)
        print(bestMove)
        board.push(bestMove)

    print(counter)

if board.is_checkmate():
    print("Game over")
    print(not(board.turn))
else:
    print("Draw")
