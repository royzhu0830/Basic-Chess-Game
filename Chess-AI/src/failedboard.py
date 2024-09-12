from const import *
from square import Square
from piece import *
from move import Move
import copy
class Board:
    
    def __init__(self):
        #create 2d array
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        self.last_move = None

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        #square where piece is located at
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        #pawn promoting
        if isinstance(piece, Pawn):
            self.check_promotion(piece, final)
        
        #king castling
        if isinstance(piece, King):
            if self.castling(initial, final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        #set last move
        self.last_move = move



    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
                            print('penis')
        

        return False
    def calc_moves(self, piece, row, col, bool = True):
        
        def pawn_moves():
            if piece.moved:
                steps = 1
            else:
                steps = 2
            
            #vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1+steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        #create an initial/final move square
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        #create a new move
                        move = Move(initial, final)
                        #check potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    #blocked
                    else:
                        break
                #not in range
                else:
                    break
            #diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        move = Move(initial, final)

                        #append new move
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)


        def knight_moves():
            #8 possible moves
            possible_moves = [(row-2, col + 1), (row-1, col+2), (row+1, col+2), (row+2, col+1), (row+2, col-1), (row+1, col-2), (row-1, col-2), (row-2, col-1)]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        #create new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        #move
                        move = Move(initial, final)
                        #append new valid move 
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                break
                        else:
                            piece.add_move(move)

        def king_moves():
            adj = [(row-1, col), (row -1, col -1), (row -1, col + 1), (row + 1, col), (row + 1, col -1), (row +1, col + 1), (row, col + 1), (row, col -1)]
            for possible_move in adj:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                        if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                            #create new move
                            initial = Square(row, col)
                            final = Square(possible_move_row, possible_move_col)
                            #move
                            move = Move(initial, final)
                            #append new valid move 
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                                else:
                                    break
                            else:
                                piece.add_move(move)

            #castling moves
            if not piece.moved:

            
                #queen castle
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece(): #castling not possible because there's a piece in the way
                                break
                            if c == 3:
                                #adds left rook to king
                                piece.left_rook = left_rook

                                #rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)
                                

                                #king move
                                
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)
                          

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        #append new move to rook
                                        left_rook.add_move(moveR)

                                        #append new move to king
                                        piece.add_move(moveK)
                                    else:
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                #king castle
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece(): #castling not possible because there's a piece in the way
                                break
                            if c == 6:
                                #adds right rook to king
                                piece.right_rook = right_rook

                                #rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)
                              

                                #king move
                                
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        #append new move to rook
                                        right_rook.add_move(moveR)

                                        #append new move to king
                                        piece.add_move(moveK)
                                    else:
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr 

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        
                        #create square of new possible moves
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        #create a possible new move
                        move = Move(initial, final)

                        #empty
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            

                        #has enemy piece
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                                if bool:
                                    if not self.in_check(piece, move):
                                        piece.add_move(move)
                                    else:
                                        piece.add_move(move)
                                    break

                        #has team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                    #not in range
                    else:
                        break
                    #incrementing
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        #Calculates any of the valid moves of a piece
        if isinstance(piece, Pawn):
            pawn_moves()
        
        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Bishop):
            straightline_moves([(-1, 1), (-1, -1), (1, 1), (1, -1)])

        elif isinstance(piece, Rook):
            straightline_moves([(1, 0) , (-1, 0), (0, 1), (0, -1)])

        elif isinstance(piece, Queen):
            straightline_moves([(1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (-1, -1), (1, 1), (1, -1)])

        elif isinstance(piece, King):
            king_moves()
        
    def _create(self):
        #looping 2d array, adding square object instead of the 0s
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col) 
    
    def _add_pieces(self, color):
        row_pawn, row_other = (6,7) if color == 'white' else (1,0)
        #display all pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        
        #display all knights
        self.squares[row_other][1] = Square (row_other, 1, Knight(color))
        self.squares[row_other][6] = Square (row_other, 6, Knight(color))


        #display all bishops
        self.squares[row_other][2] = Square (row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square (row_other, 5, Bishop(color))

      #  self.squares[5][3] = Square (5, 3, King(color))

        #display all rooks
        self.squares[row_other][0] = Square (row_other, 0, Rook(color))
        self.squares[row_other][7] = Square (row_other, 7, Rook(color))

        #display queen
        self.squares[row_other][3] = Square (row_other, 3, Queen(color))
                
        #display king
        self.squares[row_other][4] = Square (row_other, 4, King(color))
