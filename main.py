import chess
import chess.syzygy
import chess.polyglot
import berserk
import threading

f = open("token.txt", "r")
TOKEN = f.readline()
SESSION = berserk.TokenSession(TOKEN)
CLIENT = berserk.Client(session=SESSION)
CHECKMATE = 20000
DRAW = 0
MAX_DEPTH = 5
ENDGAME_START = 2*1340
CASTLE_VALUE = 25
MINIMUM_TIME = 300

bestMove = None
bestEval = 0
pieceScore = [100,320,330,500,900,0]
white,black = [], []


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
            50, 80, 10, 0, 0, 70, 80, 50,
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
            50, 80, 10, 0, 0, 70, 80, 50
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


def evaluation(board):
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

    if len(pieces) <= 5: #endgame table
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


def pre_evaluation(board, move):

    fromSquare = move.from_square
    toSquare = move.to_square
    fromPiece = (board.piece_type_at(fromSquare))-1
    toPiece = (board.piece_type_at(toSquare))

    movePreEval = 0

    if board.turn == chess.WHITE:
        movePreEval = white[fromPiece][toSquare] - white[fromPiece][fromSquare]
    if board.turn == chess.BLACK:
        movePreEval = black[fromPiece][toSquare] - black[fromPiece][fromSquare]

    if toPiece is not None:
        toPiece = toPiece-1
        movePreEval += 10 * pieceScore[toPiece] - pieceScore[fromPiece]  # captures are good

    if move.promotion is not None:
        movePreEval += 800  # promotions are good

    return movePreEval


def capture_search(board, alpha, beta):
    eval = evaluation(board)

    if eval >= beta:
        return beta

    if eval > alpha:
        alpha = eval

    newMoves = board.legal_moves
    captureMoves = []

    for move in newMoves:
        if board.is_capture(move) or board.gives_check(move) or board.is_check():
            captureMoves.append((pre_evaluation(board,move), move.uci()))

    captureMoves.sort(reverse=True)

    for captureMove in captureMoves:
        move = chess.Move.from_uci(captureMove[1])

        board.push(move)
        eval = -capture_search(board, -beta, -alpha)
        board.pop()

        if eval >= beta:
            return beta

        if eval > alpha:
            alpha = eval

    return alpha


def seconds(t):
    return t.timestamp()


class Game(threading.Thread):
    def __init__(self, client, game_id, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self.client = client
        self.stream = client.bots.stream_game_state(game_id)
        self.current_state = next(self.stream)
        self.totalTime = 0
        self.board = chess.Board()
        self.ai_turn = chess.WHITE
        self.ai_time = 0
        self.bestMove = None
        self.bestEval = 0
        self.depth = MAX_DEPTH

    def find_move(self, board, depth, alpha, beta):

        if depth == self.depth:
            try:
                self.bestMove = book.weighted_choice(board).move
                return
            except IndexError:
                pass

        if board.is_checkmate():
            return -(CHECKMATE - (MAX_DEPTH - depth))

        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return DRAW

        if depth == 0:
            return capture_search(board, alpha, beta)

        newMoves = board.legal_moves
        orderedMoves = []

        for move in newMoves:
            orderedMoves.append((pre_evaluation(board, move), move.uci()))

        orderedMoves.sort(reverse=True)

        for orderedMove in orderedMoves:
            move = chess.Move.from_uci(orderedMove[1])
            board.push(move)
            eval = -self.find_move(board, depth - 1, -beta, -alpha)

            board.pop()

            if eval == CHECKMATE and depth == MAX_DEPTH:
                self.bestMove = move
                self.bestEval = eval
                return

            if beta <= eval:
                return beta

            if eval > alpha:
                alpha = eval
                if depth == self.depth:
                    self.bestMove = move
                    self.bestEval = eval

        return alpha

    def run(self):
        try:
            CLIENT.bots.make_move(self.game_id, book.weighted_choice(self.board).move)
            self.ai_turn = chess.WHITE
        except BaseException as e:
            print(e)
            self.ai_turn = chess.BLACK

        for event in self.stream:
            if event['type'] == 'gameState' and event['status'] == 'started':
                self.handle_state_change(event)
            elif event['type'] == 'chatLine':
                self.handle_chat_line(event)

    def handle_state_change(self, game_state):
        moveCount = game_state['moves'].count(' ')
        moveString = game_state['moves'].split(' ')[moveCount]
        try:
            move = chess.Move.from_uci(moveString)
            self.board.push(move)
        except ValueError as e:
            print(e)

        if (moveCount % 2 == 1 and self.ai_turn == chess.BLACK) or (moveCount % 2 == 0 and self.ai_turn == chess.WHITE) or game_state['status'] == 'aborted':
            pass
        else:

            if self.ai_turn == chess.WHITE:
                self.ai_time = seconds(game_state['wtime'])
            else:
                self.ai_time = seconds(game_state['btime'])

            if self.ai_time < 360:
                self.depth = 4
            if self.ai_time < 150:
                self.depth = 3
            if self.ai_time < 60:
                self.depth = 2

            self.find_move(self.board, self.depth, -CHECKMATE, CHECKMATE)
            CLIENT.bots.make_move(self.game_id, self.bestMove)

    def handle_chat_line(self, chat_line):
        pass


print('Bot is online')
init_heat_maps()
book = chess.polyglot.MemoryMappedReader("baronbook30/baron30.bin")
tablebase = chess.syzygy.open_tablebase("3-4-5piecesSyzygy/3-4-5")

for event in CLIENT.bots.stream_incoming_events():
    if event['type'] == 'challenge':
        if event['challenge']['variant']['key'] == 'standard' and (event['challenge']['perf']['name'] == 'Correspondence' or event['challenge']['timeControl']['limit'] >= MINIMUM_TIME):
            CLIENT.bots.accept_challenge(event['challenge']['id'])
        else:
            CLIENT.bots.decline_challenge(event['challenge']['id'])

    elif event['type'] == 'gameStart':
        print("Bot has started a game")
        game = Game(CLIENT, event['game']['id'])
        game.start()
