import chess
import chess.syzygy
import random
import berserk
import threading
import time
#import cProfile

#board = chess.Board('r3k2r/p1ppqpb1/Bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPB1PPP/R3K2R b KQkq - 0 1') #perf test
#board = chess.Board('1k1r4/ppp1pp2/7p/8/8/8/2qNKPb1/8 w - - 2 36') #checkmate test
#board = chess.Board('8/1pp2p1k/5n2/1B4p1/4p3/1P2P1P1/3K1P2/8 w - - 1 52') #endgame test
#board = chess.Board('r1q2k1r/pp3ppp/4bn2/1B6/1P1Bp3/P3P1P1/1Q3P2/3RK1R1 b - - 10 27') #eval test
board = chess.Board()

SESSION = berserk.TokenSession('QKIVKEgX1DLKLybP')
CLIENT = berserk.Client(session=SESSION)
CHECKMATE = 20000
DRAW = 0
MAX_DEPTH = 4
AI_COLOR = chess.BLACK
ENDGAME_START = 2*1340
CASTLE_VALUE = 50

d = 0
counter = 0
bestMove = None
bestEval = 0
pieceScore = [100,320,330,500,900,0]
hashTable = [[0 for x in range(12)] for y in range(64)]
castlingHash = [0, 0, 0, 0]
enPassantHash = [0, 0, 0, 0, 0, 0, 0, 0]
nextToMoveHash = 0
hashedPositions = {}
white,black = [], []
colors = {}


def init_heat_maps():
    global white, black

    # They have to be flipped cause that's how library works - PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING (middle), KING (end)

    white = [
        [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, -35, -35, 10, 10, 5,
            10, -5, -10, 0, 0, -10, -5, 10,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, 5, 10, 25, 25, 10, 5, 5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 70, 70, 70, 70, 50, 50,
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
            20, 40, 30, 0, 0, 10, 40, 20,
            20, 20, 0, 0, 0, 0, 20, 20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30
        ],
        [
            -50, -30, -30, -30, -30, -30, -30, -50,
            - 30, -20, 0, 0, 0, 0, -20, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -20, -10, 0, 0, -10, -20, -30,
            -50, -40, -30, -20, -20, -30, -40, -50

        ]
    ]

    black = [
        [
            0, 0, 0, 0, 0, 0, 0, 0,
            50, 50, 70, 70, 70, 70, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5, 5, 10, 25, 25, 10, 5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            10, -5, -10, 0, 0, -10, -5, 10,
            5, 10, 10, -35, -35, 10, 10, 5,
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
            20, 40, 10, 0, 0, 30, 40, 20
        ],
        [
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10, 0, 0, -10, -20, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -20, 0, 0, 0, 0, -30, -20,
            -50, -30, -30, -30, -30, -30, -30, -50
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

    if board.is_checkmate():
        return -(CHECKMATE - (MAX_DEPTH - depth))

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
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

        if beta <= eval:
            return beta

        if eval > alpha:
            alpha = eval
            #bestMoveInPosition = move
            if depth == MAX_DEPTH:
                bestMove = move
                bestEval = eval

    #hashedPositions[fen] = (alpha, depth, bestMoveInPosition)
    return alpha

#init_hashing()
init_heat_maps()

#hash = hashing()
#cProfile.run(find_move(MAX_DEPTH, -CHECKMATE, CHECKMATE))

#find_move(MAX_DEPTH, -CHECKMATE, CHECKMATE)

class Game(threading.Thread):
    def __init__(self, client, color, game_id, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self.client = client
        self.stream = client.bots.stream_game_state(game_id)
        self.current_state = next(self.stream)
        self.totalTime = 0

        if color == 'white':
            self.ai_turn = chess.BLACK
        else:
            self.ai_turn = chess.WHITE


    def run(self):
        if self.ai_turn == chess.WHITE:
            CLIENT.bots.make_move(self.game_id, 'e2e4')
        for event in self.stream:
            print(event)
             if event['type'] == 'gameState':
                 self.handle_state_change(event)
             elif event['type'] == 'chatLine':
                self.handle_chat_line(event)

    def handle_state_change(self, game_state):
        moveCount = game_state['moves'].count(' ')
        moveString = game_state['moves'].split(' ')[moveCount]
        move = chess.Move.from_uci(moveString)
        board.push(move)

        if (moveCount%2 == 1 and self.ai_turn == chess.BLACK) or (moveCount%2 == 0 and self.ai_turn == chess.WHITE):
            pass
        else:
            startTime = time.time()
            #counter = 0

            find_move(MAX_DEPTH, -CHECKMATE, CHECKMATE)
            CLIENT.bots.make_move(self.game_id, bestMove)

            usedTime = time.time() - startTime
            self.totalTime += usedTime
            #print(str(counter) + " nodes evaluated. Time used: " + str(usedTime))
            #print("Position evaluation: " + str(bestEval / 100))

    def handle_chat_line(self, chat_line):
        pass



while True:
    print('Bot is online')
    for event in CLIENT.bots.stream_incoming_events():
        print(event)
        if event['type'] == 'challenge':
            if not event['challenge']['color'] == 'random' and event['challenge']['variant']['key'] == 'standard' and event['challenge']['timeControl']['limit'] >= 600:
                CLIENT.bots.accept_challenge(event['challenge']['id'])
                colors[event['challenge']['id']] = event['challenge']['color']
            else:
                CLIENT.bots.decline_challenge(event['challenge']['id'])

        elif event['type'] == 'gameStart':
            print(colors)
            board = chess.Board() #temp fix - todo multithreading
            game = Game(CLIENT, colors[event['game']['id']], event['game']['id'])
            game.start()