#! /usr/bin/env python3
##############################################################################################
"""
    Chess Stats scripts to create a Chess Study Assistant
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

import time        
import logging
###############################################################################################
#version 1.0.0

class legal_moves():
    """
    Class to take a FEN and a piece at a position (first part of algebra to get square) and return a list of possible moves for that piece.
    It then takes the second part of the Algbra (the to square) and returns if moving that piece to that square would be a legal move.
    Return a reason why it would not be legal if it is not legal.
    EX.     legal, why_not, possible moves = legal_move
    
    """
    def __init__(self):
        self.fen = ""

    def squares_to_fen (self, squares, r_fen):
        #receive squares  (0 to 63 length list of pieces at each square of the board "P" "p" "-" for empthy square)
        #and the right side (not pieces part) of the current FEN
        #return a FEN made up of the squares sent and right side of FEN received      
        fen = ""
        spacecount=0
        for row in range (0, 64, 8):  #read 8 rows
            for x in range (row, row + 8):     #read squares list one row one at a time and place in fen
                if squares [x] == "-":       #if a space update space counter
                    spacecount = spacecount + 1
                else:               # if a piece is at this location
                    if spacecount == 0:
                        fen = fen + squares[x]
                    else:
                        fen = fen + str(spacecount) #put in number of spaces
                        fen = fen + squares [x]     #put in piece position
                        spacecount = 0
            if spacecount > 0:  #last position of row is space handle it
                fen = fen + str(spacecount) #put in number of spaces
                spacecount = 0
            if x < 63:  #add forward slash if not last row add space if it is
                fen = fen + "/"
            else:
                fen = fen + " "  #space added to mark end of field
        fen = fen + r_fen                      
        return fen    

    def display_squares(self, squares):
        for p in range(8):   #show the squares by printing so they can be seen in terminal (temporary)
            x = p * 8
            print(squares [x: x+8]) 
        print("____________________________________________")  
        
    def fen_to_squares(self, lfen):    #set up squares list to represent chess board
        #create squares  (0 to 63 length list of pieces at each square of the board "P" "p" "-" for empthy square) from left side (pieces) of a FEN        
        squares = []     #squares 0 is ALWAYS black rook home position squares 63 is last white rook position       
        for letter in lfen:       #go through the fen and fill squares with piece letter or s for space
            #letter = lfen[p]
            if letter == "/":           # FEN separator / does not go in squares
                pass
            elif letter.isdecimal():    #if a number, put that many "-" spaces in squares list using dash as not upper or lower since check uses case?
                x = int(letter)
                for y in range (x):
                    squares.append("-")
            else:                       #if not a number or a separator then is a piece letter so put in appropriate square
                squares.append(letter)  #draw_piece will remove and re add piece here to work witt drawpiece for all calls                           
        #self.display_squares(squares)
        return squares 
    # end of fen to squares
        
    def get_alg_from_square(self, sq):      #receives a square # and returns alg (ex. e2)
        if sq not in range(0,64):
            logging.error("Square not from 0 to 63 sent to get_alg_from_square")
            return 64               #64 is NOT a square on a chessboard     
        rows = ["8","7","6","5","4","3","2","1"] #rows 0 to 7 indexes.       
        cols = ["none","a","b","c","d","e","f","g","h"]              
        row = 8 - int(sq/ 8)      #row from 1 to 8
        col = int(sq% 8) + 1      #column from 1 to 8 1-8 needed for algebra move    
        col_letter = cols[col] 
        alg = col_letter + str(row)   
        #print("Row col from spos ", row, " ", col, "  ", col_letter)        
        return alg, row, col                                                        
        
    def get_square_from_alg(self,alg):               #alg is half of a long algebra move (ex. a8). Returns the square # of that alg 0 to 63
        cols = ["a","b","c","d","e","f","g","h"]    
        rows = ["8","7","6","5","4","3","2","1"] #rows 0 to 7 indexes.          
        c = alg[:1]
        try:
            col = cols.index(c)
        except:
            logging.error("Bad alg sent to square_from_alg")
            return 64               #64 is NOT a square on a chessboard  
        r = alg[-1]
        if r in rows:
            row = rows.index(r)               #start row   
        else:
            logging.error("Bad alg sent to square_from_alg")
            return 64               #64 is NOT a square on a chessboard                            
        square = (row * 8) + col          #calculate position in squares list
        return square

    def get_move_squares(self, lalg):            #from long algebra move col a-h row 1-8  NO 0
        #move_squares = []                           #square numbers from algebra  a8 is square 0 no matter the rotation of board
        orig = lalg[:2]
        origsqr = self.get_square_from_alg(orig)
        #move_squares.append(origsqr)        
        dest = lalg[2:4]
        destsqr = self.get_square_from_alg(dest)        
        #move_squares.append(destsqr)  
        return origsqr, destsqr     #square number of origin and destination
######################################

    def is_piece_ofcolor(self, spos, spiece, whosemove):
        #makes sure there is a piece of the moving color at the startpos of the move
        valid = False
        if whosemove == "b":                            #blacks move so make sure piece is lowercase (black)
            if spiece.islower():
                valid = True
        else:
            if spiece.isupper():
                valid = True 
        return valid
    #end is_piece_ofcolor

    def getonesquare(self, alg):
        columns = ["a","b","c","d","e","f","g","h"]  # 0 - 7
        rows = ["8","7","6","5","4","3","2","1"] #rows 0 to 7. 
        s = alg[0]
        if s in columns:         #start column = index of columns list set high if not in list to make valid False as > 63
            column = columns.index(s)
        s = alg[1]    
        if s in rows:
            row = rows.index(s)               #start row
        spos = (row * 8) + column          #calculate position in squares list
        return spos
    # end getonesquare  

    def get_pawnmoves(self, squares, spiece, spos, enp):
        #squares (board) spiece (piece to move (case) spos square of piece to move cr is castle rights enp is enpassant
        #determing all possible moves on this board (squares) for a specific pawn.  Returns list of possible squares in (0 to 63)
        moves = []
        alg, piecerow, piececol = self.get_alg_from_square(spos)
        #print(piecerow," col ",piececol)
        if spiece.islower():        #if black pawn is being moved
            #check forward moves
            if squares[spos+8] == "-":      #no piece in front of pawn so pawn not blocked so can move forward (spos + 8 cannot be more than 63 )
                moves.append(spos + 8)      #add spot in front of pawn to list
                if piecerow == 7:           #if pawn in home row then forward two spaces is legal
                    if squares[spos+16] == "-":     #we know one space isn't blocked so check the next one
                        moves.append(spos+16)
            #check normal capture
            if piececol < 8:        #check if capture possible on column to left
                if squares[spos + 9].isupper():     #square has a black piece so capture possible
                    moves.append(spos+9)
            if piececol > 1:        #check if capture possible on right
                if squares[spos + 7].isupper():     #square has a black piece so capture possible
                    moves.append(spos+7)
            #check enpassant capture if available in fen
            if enp != "-":          # - means no enpassant so if not equal then enpassant possible
                if piecerow == 4:           #pawn to be moved must be on row allowing enpassant or done with enpassant check
                    esq = self.getonesquare(enp)
                    alg, erow, ecol = self.get_alg_from_square(esq)
                    if piececol != ecol:            #no enpassant if enpassant column is same
                        if abs(piececol - ecol) < 2:    #within one column so enpassant possible
                           moves.append(esq)
        else:                       #white pawn being moved
            #check forward moves
            if squares[spos-8] == "-":      #no piece in front of pawn so pawn not blocked so can move forward (spos - 8 cannot be less than 0 )
                moves.append(spos - 8)      #add spot in front of pawn to list
                if piecerow == 2:           #if pawn in home row then forward to spaces is legal
                    if squares[spos-16] == "-":     #we know one space isn't blocked so check the next one
                        moves.append(spos-16)
            #check normal capture
            if piececol < 8:        #check if capture possible on column to right
                if squares[spos - 7].islower():     #square has a black piece so capture possible
                    moves.append(spos-7)
            if piececol > 1:        #check if capture possible on left
                if squares[spos - 9].islower():     #square has a black piece so capture possible
                    moves.append(spos-9)
            #check enpassant capture if available in fen
            if enp != "-":          # - means no enpassant so if not equal then enpassant possible
                if piecerow == 5:           #pawn to be moved must be on row allowing enpassant or done with enpassant check
                    esq = self.getonesquare(enp)
                    alg, erow, ecol = self.get_alg_from_square(esq)
                    if piececol != ecol:            #no enpassant if enpassant column is same
                        if abs(piececol - ecol) < 2:    #within one column so enpassant possible
                           moves.append(esq)       
        return moves 
    
    def knightsquares(self, piecepossq):
        #piecepossq is piece position square
        s = [piecepossq-15, piecepossq-6, piecepossq+10, piecepossq+17, piecepossq+15, piecepossq+6, piecepossq-10, piecepossq-17]        #squares a knight could move to
        squares_tocheck = []    #list of squares to check for checking knight based on startrow startcol
        _, _, compare_col = self.get_alg_from_square(piecepossq)
           #make a list of the squares a knight would be initiating check or could move to
        for sq in s:
            if sq in range(0,64):               #no wrap top to bottom, if wrapped column then column difference will be more than 2
                _, _, col = self.get_alg_from_square(sq)
                x = abs(compare_col - col)
                if x < 3:           #if column difference is twoo or less
                    squares_tocheck.append(sq)            
        #print ("knight squares to check ", squares_tocheck)
        return squares_tocheck
    #end knightsquares function        
    
    def get_knightmoves(self, squares, spiece, spos):
        moves = []       
        #squares (board) spiece (piece to move (case) spos square of piece to move cr is castle rights enp is enpassant
        #determing all possible moves on this board (squares) for a specific knight.  Returns list of possible squares in (0 to 63)
        moves_to_check = self.knightsquares(spos)
        for m in moves_to_check:
            if spiece.islower():        #if black knight is being moved 
                if squares[m].isupper():
                    moves.append(m)
                if squares[m] == "-":
                    moves.append(m)                          
            else:                       #white knight
                if squares[m].islower():
                    moves.append(m)
                if squares[m] == "-":
                    moves.append(m)       
        return moves
    #end of get knightmoves

    def onboard(self, sqr):
        onboard = True                  #before checking assumed true
        if sqr not in range(0, 64):
            onboard = False
        return onboard  
    #end onboard function

    def get_bishopmoves(self, squares, spiece, spos):
        #squares (board) spiece (piece to move (case) spos square of piece to move
        #determing all possible moves on this board (squares) for a specific bishop(1/2queen).  Returns list of possible squares in (0 to 63)
        moves = []        
        #check all diagonal to see if bishop can move to these squares
        for diags in range (1, 5):
            _, _, compare_col = self.get_alg_from_square(spos)      #start compare column
            stillonboard = True             #assume square to be checked is onboard
            square_tocheck = spos           #start square is bishops square
            if diags == 1:          #diagonal up and left
                nextdiag = -9
            if diags == 2:          #diagonal up and right
                nextdiag = -7
            if diags == 3:          #diagonal down and left
                nextdiag = 7
            if diags == 4:          #diagonal down and right
                nextdiag = 9 
            while stillonboard:
                square_tocheck += nextdiag            #change to nextdiag to check diagonal
                stillonboard = self.onboard(square_tocheck)               #check if square is on board                  
                if stillonboard:
                    _, _, col = self.get_alg_from_square(square_tocheck)
                    x = abs(compare_col - col)
                    if x > 1:               #if moved more than 1 column then not still in same diagonal
                        stillonboard = False
                    else:
                        compare_col = col        #set so that column is always last one so next can be up to one column apart                    
                if stillonboard:         #if still on board proceed
                    if spiece.islower():           #moving piece is black lowercase
                        if squares[square_tocheck].islower():   #if lowercase then piece is own piece blocking so exit loop
                            break
                        if squares[square_tocheck].isupper():   #white piece is capturable and ends diagonal so break
                            moves.append(square_tocheck)        #add to list as bishop can move here but break since can move no further
                            break                        
                        if squares[square_tocheck] == "-":      #space (no piece) so add move and continue diagonal
                            moves.append(square_tocheck)        #add to list as bishop can move here
                    else:                           #upper means white piece
                        if squares[square_tocheck].isupper():   #if uppercase then piece is own piece blocking so exit loop
                            break
                        if squares[square_tocheck].islower():   #black piece is capturable and ends diagonal so break
                            moves.append(square_tocheck)        #add to list as bishop can move here but break since can move no further
                            break                        
                        if squares[square_tocheck] == "-":      #space (no piece) so add move and continue diagonal
                            moves.append(square_tocheck)        #add to list as bishop can move here
        return moves
    #end of getbishopmoves

    def get_rookmoves(self, squares, spiece, spos):
        #squares (board) spiece (piece to move (case) spos square of piece to move cr is castle rights enp is enpassant
        #determing all possible moves on this board (squares) for a specific rook.  Returns list of possible squares in (0 to 63)
        moves = []
        #check all diagonal to see if rook can move or any own piece blocking check rows and columns 4 total
        for rf in range (1, 5):
            stillonboard = True             #assume square to be checked is onboard
            _, _, compare_col = self.get_alg_from_square(spos)      #start compare column
            square_tocheck = spos           #start square is rooks square
            if rf == 1:          #up
                nextdiag = -8
            if rf == 2:          #down
                nextdiag = 8
            if rf == 3:          #left
                nextdiag = -1
            if rf == 4:          #right
                nextdiag = 1 
            while stillonboard:
                square_tocheck += nextdiag            #change to nextdiag to check row
                stillonboard = self.onboard(square_tocheck)               #check if new row col are onboard
                if stillonboard:
                    _, _, col = self.get_alg_from_square(square_tocheck)
                    x = abs(compare_col - col)
                    if x > 1:               #if moved more than 1 column then not still in same diagonal
                        stillonboard = False
                    else:
                        compare_col = col        #set so that column is always last one so next can be up to one column apart                   
                if stillonboard:         #if still on board proceed
                    if spiece.islower():           #lower means black piece to move
                        if squares[square_tocheck].islower():   #if lowercase then piece is own piece blocking so exit loop
                            break
                        if squares[square_tocheck].isupper():  #white piece can be captured so add square and break loop
                            moves.append(square_tocheck)        #add to list as rook can move here but break since can move no further
                            break
                        if squares[square_tocheck] == "-":      #space (no piece) so add move and continue diagonal
                            moves.append(square_tocheck)        #add to list as rook can move here
                    else:                           #checkpiece upper means black piece possibly checking white king
                        if squares[square_tocheck].isupper():   #if lowercase then piece is own piece blocking so exit loop
                            break
                        if squares[square_tocheck].islower():  #black piece can be captured so add square and break loop
                            moves.append(square_tocheck)        #add to list as rook can move here but break since can move no further
                            break
                        if squares[square_tocheck] == "-":      #space (no piece) so add move and continue diagonal
                            moves.append(square_tocheck)        #add to list as rook can move here
        return moves
    #end get rookmoves function

    def get_queenmoves(self, squares, spiece, spos):
        #squares (board) spiece (piece to move (case) spos square of piece to move cr is castle rights enp is enpassant
        #determing all possible moves on this board (squares) for a specific queen.
        # Queen is bishop moves added to rook moves.  Returns list of possible squares in (0 to 63)
        moves = []
        if spiece.islower():    #if black piece set up bishop and rook fake pieces to run their routines so they can have their results added
            fake_bishop = "b"
            fake_rook = "r"
        else:           #White pieces
            fake_bishop = "B"
            fake_rook = "R"
        moves = self.get_bishopmoves(squares, fake_bishop, spos) 
        rook_moves = self.get_rookmoves(squares, fake_rook, spos)
        for i in rook_moves:        #add rook moves to bishop moves
            moves.append(i)        
        return moves
    #end queenmoves

    def get_kingmoves(self, squares, spiece, spos, castle): 
        #squares (board) spiece (piece to move (case) spos square of piece to move cr is castle rights enp is enpassant
        #determing all possible moves on this board (squares) for a specific king.
        #also check that king does not move next to king.  Returns list of possible squares in (0 to 63)
        full_offsets = [-9, -8, -7, -1, 1, 7, 8, 9]    #offsets from piece position all around piece (king)
        moves = []
        offsets = []
        alg, piecerow, piececol = self.get_alg_from_square(spos)
        check_squares = squares.copy()              #make a copy to check for check at all positions
        check_squares.pop(spos)                     #remove the king (spiece) from the list
        check_squares.insert(spos,"-")              #insert a - at it's place so that you will not have two kings when you move it to check for check
        for i in full_offsets:          #only list squares offset from piece that are still on the board
            postocheck = spos + i
            if postocheck in range(0, 64):     #in squares 0 to 63 of the board means square is on the board      
                offsets.append(spos + i)
        #print("kingmoves  ", offsets)
        if spiece.islower():    #if black piece moving
            #find row and column of opposing king to make sure won't be next to each other
            enemy = squares.index("K")              #find square of enemy king
            alg, e_r, e_c = self.get_alg_from_square(enemy)        #row and column of enemy king
            for i in offsets:
                if squares[i].isupper() or squares[i] == "-":         #possible move or capture unless will result in check or next to other king
                    alg, r, c = self.get_alg_from_square(i)           #check this square row and column to compare to king row and column must be > 0
                    if abs(piececol - c) < 2:
                        moves.append(i)          #add to move list
                    else:
                        continue
                    if abs(r - e_r) < 2 and abs(c - e_c) < 2:         #if abs of both less than 2 then kings too close so remove
                        what = moves.pop()         #taketh away because kings too close (cannot be next to each other)
                    else:           #since not too close to king didn't remove move check for move making you in check and remove if it does
                        was = check_squares.pop(i)
                        check_squares.insert(i, "k")
                        checked, num_checks = self.is_king_checked(check_squares, "b")   #T/F for checked and number of pieces checking player moving
                        if checked:
                            if len(moves)>0:
                                moves.pop()     #take move away because it would be check
                            #print("checked ",i,"numchecks ",num_checks)
                        check_squares.pop(i)        #remove the king placed temporarily for check
                        check_squares.insert(i, was)    #put back what was there before
            #check if castling is legal
            if "k" in castle:                       #castlerights for king side castling so check if legal (not passing through check
                checked, num_checks = self.is_king_checked(squares, "b")   #T/F for checked and number of pieces checking player moving before move
                if not checked:         #king is not in check so may be able to castle
                    if 5 in moves and squares[5] == "-":  #if first space is in moves and empty (already checked king move) castle this side ok so far check next
                        if squares[6] == "-":           #ok but check if it is being checked for king
                            was = check_squares.pop(6)
                            check_squares.insert(6, "k")
                            checked, num_checks = self.is_king_checked(check_squares, "b")   #T/F for checked and number of pieces checking player moving
                            check_squares.pop(6)        #remove the king placed temporarily for check
                            check_squares.insert(6, was)    #put back what was there before
                            if not checked:                 #all squares empty and not checked so castling ok, add to moves
                                moves.append(6)
            if "q" in castle:                       #castlerights for king side castling so check if legal
                checked, num_checks = self.is_king_checked(squares, "b")   #T/F for checked and number of pieces checking player moving
                if not checked:         #king is not in check so may be able to castle        
                    if 3 in moves and squares[3] == "-":  #if first space is in moves and empty (already checked king move) castle this side ok so far check next
                        if squares[2] == "-" and squares[1] == "-":           #ok but check if 3 is being checked for king
                            was = check_squares.pop(2)
                            check_squares.insert(2, "k")
                            checked, num_checks = self.is_king_checked(check_squares, "b")   #T/F for checked and number of pieces checking player moving
                            check_squares.pop(2)        #remove the king placed temporarily for check
                            check_squares.insert(2, was)    #put back what was there before                    
                            if not checked:                 #all squares empty and not checked so castling ok, add to moves
                                moves.append(2)  
            #print("kingmoves  t", moves)                      
        else:           #white piece moving
            #find row and column of opposing king to make sure won't be next to each other
            enemy = squares.index("k")              #find square of enemy king
            alg, e_r, e_c = self.get_alg_from_square(enemy)        #row and column of enemy king
            for i in offsets:
                if squares[i].islower() or squares[i] == "-":         #possible move or capture unless will result in check or next to other king
                    alg, r, c = self.get_alg_from_square(i)           #check this square row and column to compare to king row and column must be > 1
                    if abs(piececol - c) < 2:
                        moves.append(i)          #add to move list
                    else:
                        continue
                    if abs(r - e_r) < 2 and abs(c - e_c) < 2:         #if abs of both less than 2 then kings too close so remove
                        what = moves.pop()         #taketh away because kings too close (cannot be next to each other)
                    else:           #since not too close to king didn't remove move check for move making you in check and remove if it does
                        was = check_squares.pop(i)
                        check_squares.insert(i, "K")
                        checked, num_checks = self.is_king_checked(check_squares, "w")   #T/F for checked and number of pieces checking player moving
                        if checked:
                            if len(moves)>0:
                                moves.pop()     #take move away because it would be check
                        check_squares.pop(i)
                        check_squares.insert(i, was)
            if "K" in castle:                       #castlerights for king side castling so check if legal
                checked, num_checks = self.is_king_checked(squares, "w")   #T/F for checked and number of pieces checking player moving
                if not checked:         #king is not in check so may be able to castle        
                    if 61 in moves and squares[61] == "-":  #if first space is in moves and empty (already checked king move) castle this side ok so far check next
                        if squares[62] == "-":           #ok but check if it is being checked for king
                            was = check_squares.pop(62)
                            check_squares.insert(62, "K")
                            checked, num_checks = self.is_king_checked(check_squares, "w")   #T/F for checked and number of pieces checking player moving
                            check_squares.pop(62)        #remove the king placed temporarily for check
                            check_squares.insert(62, was)    #put back what was there before                    
                            if not checked:                 #all squares empty and not checked so castling ok, add to moves
                                moves.append(62)
            if "Q" in castle:                       #castlerights for king side castling so check if legal
                checked, num_checks = self.is_king_checked(squares, "w")   #T/F for checked and number of pieces checking player moving
                if not checked:         #king is not in check so may be able to castle        
                    if 59 in moves and squares[59] == "-":  #if first space is in moves and empty (already checked king move) castle this side ok so far check next
                        if squares[58] == "-" and squares[57] == "-":           #ok but check if 3 is being checked for king
                            was = check_squares.pop(58)
                            check_squares.insert(58, "K")
                            checked, num_checks = self.is_king_checked(check_squares, "w")   #T/F for checked and number of pieces checking player moving
                            check_squares.pop(58)        #remove the king placed temporarily for check
                            check_squares.insert(58, was)    #put back what was there before                    
                            if not checked:                 #all squares empty and not checked so castling ok, add to moves
                                moves.append(58) 
        x = len(moves)
        #print(" &&&&&  King has ",x," moves available")                                                      
        return moves
    #end kingmoves
    
    def getlistofmoves(self, fen, squares, spiece, spos):  #using board (squares) piece and piece position (spos) get list of possible moves (squares) that can be moved to
        #list is based on piece, color, and position on squares (board), if other pieces block move castle rights and enpassant
        if fen == "":               #FEN is null when not looking for pawn or castle moves when called from king_incheck
            enpassant = "-"
            castleright = "-"
        else:
            r_fen = fen.rsplit(sep=None, maxsplit=5)             #get list of fen parts used to determine castling status of FEN and en passant status
            castleright = r_fen[2]
            enpassant = r_fen[3]
        temppiece = spiece.upper()              #temp string to keep from case changing for every compare in this function
        alg, piecerow, piececol = self.get_alg_from_square(spos)
        if temppiece == "P":                   #compare temp uppercase of spiece to see if it is a P for Pawn
            poss_moves = self.get_pawnmoves(squares, spiece, spos, enpassant)
        if temppiece == "N":
            poss_moves = self.get_knightmoves(squares, spiece, spos)  
        if temppiece == "B":
            poss_moves = self.get_bishopmoves(squares, spiece, spos)  
        if temppiece == "R":
            poss_moves = self.get_rookmoves(squares, spiece, spos)   
        if temppiece == "Q":
            poss_moves = self.get_queenmoves(squares, spiece, spos)
        if temppiece == "K":
            poss_moves = self.get_kingmoves(squares, spiece, spos, castleright)             
        return poss_moves 
        #end getlistofmoves   

    def pawncheck(self, squares, kingsq, king, kingrow, kingcol):       #check if a pawn is checking the king return number of checks
        #squares is board kingsq is kingsquare king is w or b for king being checked for check kingrow is king row kingcol is king column
        checks = 0              #set to 0 until you add checks you find
        if king == "k":         #if black king chpiece is "P"
            chpiece = "P"       #capital P for white pawn    
            if kingrow < 6:      #row 6 and seven cannot check so if less than 6 check if checked
                if kingcol > 0:     #check for pawn on king lesscolumn side
                    if squares[kingsq + 7] == chpiece:      # if square is a pawn "P" then checked
                        checks += 1                         #add a check to total
                if kingcol < 7:     #check for pawn on king lesscolumn side
                    if squares[kingsq + 9] == chpiece:      # if square is a pawn "P" then checked
                        checks += 1                         #add a check to total
            else:
                return 0        #king in row 6 or 7 cannot be checked by a pawn so return 0 checks
        else:                   #if white king chpiece is "p"
            chpiece = "p"
            if kingrow > 1:      #row 0 and 1 cannot check so if more than 1 check if checked
                if kingcol > 0:     #check for pawn on king lesscolumn side
                    if squares[kingsq - 9] == chpiece:      # if square is a pawn "p" then checked
                        checks += 1                         #add a check to total
                if kingcol < 7:     #check for pawn on king lesscolumn side
                    if squares[kingsq - 7] == chpiece:      # if square is a pawn "p" then checked
                        checks += 1                         #add a check to total
            else:
                return 0        #king in row 0 or 1 cannot be checked by a pawn so return 0 checks    
        return checks
    # end of pawn check function

    def is_king_checked(self, squares, kingcolor):    #see if the king of color has their king in check (position, not move check) squares reflect position being checked
    #    determine what king to see if it is in check and put it in king variable
        checked = False
        num_checks = 0              #set to 0 until you add checks you find
        ck = 0
        if kingcolor == "b":        #if checking black king for check
            king = "k"              #black king is lowercase
        else:
            king = "K"              #white king is uppercase        
        kingsq = squares.index(king)    #get the square of the king 0 to 63 (king HAS to be in fen to be legal fen
        alg, kingrow, kingcol = self.get_alg_from_square(kingsq)
        numberofchecks = 0           #set number of checks to 0 then look for checks
        #pawn check cannot be determined by can enemy piece move to the kings square since pawn attack is different
        ck = self.pawncheck(squares, kingsq, king, kingrow, kingcol)
        num_checks = num_checks + ck    #add number of checks found to total checks num_checks 
        if kingcolor == "b":            #check all uppercase pieces not K or P to see if attacking kingsq (if in move list for that piece)
            squarepos = 0
            for i in squares:
                if i == "R" or i == "N" or i == "B" or i == "Q":
                    posmoves = self.getlistofmoves("", squares, i, squarepos) 
                    if kingsq in posmoves:
                        num_checks = num_checks + 1
                squarepos += 1
        else:
            squarepos = 0
            for i in squares:
                if i == "r" or i == "n" or i == "b" or i == "q":
                    posmoves = self.getlistofmoves("", squares, i, squarepos) 
                    if kingsq in posmoves:
                        num_checks = num_checks + 1
                squarepos += 1                
        if num_checks > 0:              #if any checks then checked is true
            checked = True
        return checked, num_checks
    # end of is_king_checked function

    def check_tpos_forcheck(self, squares, spos, tpos, whosemove):      #see if piece being moved results in check of moving side (moving pinned etc)
        #change squares copy to squares after new possible move is attempted
        chsquares = squares.copy()          #copy the squares of existing
        original = chsquares[spos]              #get the piece at the start position
        chsquares[spos] = "-"                       #change start position to a - or empty
        chsquares[tpos] = original              #change the to position to the piece that was at the start position
        checked, _ = self.is_king_checked(chsquares, whosemove)   #T/F for checked and number of pieces checking player moving     chsquares is new postition  
        return checked

    def algmovelist(self, spos, poss_moves):  #convert squares in list to algebra chess list of moves
        algebralist = []
        alg1,_,_ = self.get_alg_from_square(spos)
        for i in poss_moves:
            alg2,_,_ = self.get_alg_from_square(i)
            lalg = alg1 + alg2
            algebralist.append(lalg)
        return algebralist
    #end alg move list

    def legal_move(self, fen, move):  #take a FEN and a algebraic "f7f6" move and determine if move would be legal and return True / False and basic string why not legal
        # if move is only two characters then only getting list of squares that piece could move to (for highlighting?) not checking legal
        listonly = False
        x = len(move)
        if x == 2:
            listonly = True                 #listonly does not check for to position of move, just makes a list of possible to positions.  Doesn't care about legal of to position
            move = move + "a8"          #just random;y picked a square so that get squares won't choke 0 seems good
        move_legal = True                               #assume move is legal till proven otherwise
        poss_moves = []                                 #list of possible moves for selected piece
        reason = ""                                     #string for reason why move is illegal
        lfen, _, r_fen = fen.partition(" ")             #get pieces part of fen and save the rest as right side r_fen in case used later
        whosemove, _, _ = r_fen.partition(" ")          #get letter of whose move "b" or "w" from fen
        squares = self.fen_to_squares(lfen)                  #create squares list and fill from fen
        spos, tpos = self.get_move_squares(move)            #get squares from and to number of move being tested and make sure they are on board
        valid = True
        if spos not in range(0,64): Valid = False
        if tpos not in range(0,64): Valid = False
        if not valid:                                   #move positions didn't parse meaning algebra move is bad
            reason = "Algebra move cannot be parsed properly"
            move_legal = False
            return move_legal, reason, poss_moves
        #make sure there is a piece of whosemove color at spos square or move invalid 
        spiece = squares[spos]                          #piece at that location to be moved
        valid = self.is_piece_ofcolor(spos, spiece, whosemove)
        if not valid:                                   #move positions didn't parse meaning algebra move is bad
            reason = "No piece of proper color at move start"
            move_legal = False
            return move_legal, reason, poss_moves
        poss_moves = self.getlistofmoves(fen, squares, spiece, spos)#using board (squares) piece and piece position (spos) get list of possible moves (squares) to move to
        #narrow list of possible moves by checking if any of the possible moves cause check for all current list of possible moves
        new_list_poss = []              #empty list to add legal moves to
        for to_pos in poss_moves:           #go through list and check if move causes check or fails to stop check of moving persons King
            checked = self.check_tpos_forcheck(squares, spos, to_pos, whosemove)    
            if not checked:             #result of move does not put your king in check
                new_list_poss.append(to_pos)  #since not checked keep that move by adding to list
        #print("newlist t", new_list_poss)
        poss_moves = new_list_poss
        """
        #this is to display the squares that CAN be moved to in this list with an *
        #just for test purposes  
        copysquares = []
        for i in squares:
            copysquares.append(i) 
        for i in poss_moves:
            x = int(i)
            copysquares.pop(x)
            copysquares.insert(x, "@")
        #print("Updated with list\n")
        #self.display_squares(copysquares) 
        ######################    
        """     
        if listonly: 
            #print("List only")
            return move_legal, reason, poss_moves           
        #if move had a to square check the rest and return algebra list of moves
        #create a list of algebra (chess) moves to return
        alge_movelist = self.algmovelist(spos, poss_moves)  #convert squares in list to algebra chess list of moves
        #do the whole move checking move to position and returning complete legalmove including if THAT move causes check
        #make move in copy of squares and check if moving piece to destination will result in check
        csquares = squares.copy()
        original = csquares[spos]
        csquares[spos] = "-"
        csquares[tpos] = original          
        checked, num_checks = self.is_king_checked(csquares, whosemove)   #T/F for checked and number of pieces checking player moving
        if checked:             #result of move puts your king in check 
            #print ("Checks  ", checked, "  ",num_checks)
            move_legal = False
            reason = "Your King in check"
            logging.info(reason)            
            return move_legal, reason, alge_movelist 
        #check if destination is in poss_moves.  If it is not move is no good and return with reason         
        if tpos not in poss_moves:          #if destination is not in possible moves for that piece move is illegal
            reason = "Can't move to that square"
            move_legal = False
            logging.info(reason)            
            return move_legal, reason, alge_movelist                  
        #modfen = squares_to_fen(squares, r_fen)         #if want to return changed fen??? like fen after move if legal?? might do this           
        #print(modfen)

        return move_legal, reason, alge_movelist        

    def is_there_move(self, fen):
        #examine fen
        #check to see if player to move in fen has a move possible
        #if there are no moves see if he is in check
        #if in check then he is checkmated       return status checkmate
        #if not in check and no moves then stalemate         return status as stalemate        
        game_over = True                              #game from fen is over until a move found
        status = "continue"                                     #string for reason why move is illegal
        columns = ["a","b","c","d","e","f","g","h"] 
        rows = ["8","7","6","5","4","3","2","1"]
        mlist = [] 
        lfen, _, r_fen = fen.partition(" ")             #get pieces part of fen and save the rest as right side r_fen in case used later
        whosemove, _, _ = r_fen.partition(" ")          #get letter of whose move "b" or "w" from fen
        squares = self.fen_to_squares(lfen)                  #create squares list and fill from fen
        #squares is list with - for no piece and letter for piece.  Upper case for white Lower case for black 0 to 63 0 is black home pos a8
        psquare = -1            #squares is 0 to 63 so start at -1 so immediate increment makes 0
        for piece in squares:       #check all pieces to see if they can move if any can game_over stays False
            psquare += 1
            if piece == "-":
                continue
            alg_1, row, col = self.get_alg_from_square(psquare)
            if whosemove == "w" and piece.isupper():     #See if piece can move
                _, _, mlist = self.legal_move(fen, alg_1)
            if whosemove == "b" and piece.islower():     #See if piece can move
                _, _, mlist = self.legal_move(fen, alg_1)
            if len(mlist)>0:
                #print("xy ",xy," piece ",piece," ",mlist)
                game_over = False        #there are moves so game is not over
                break
        if game_over:
            checked, num = self.is_king_checked(squares, whosemove)
            if checked:
                status = "Checkmate!"
            else:
                status = "Stalemated!"
        #print("gameover ",game_over," status ",status)
        return game_over, status

if __name__ == '__main__':  
    l_m = legal_moves()     #create a instance of class legal moves
    start = time.time()
    fen = "4k3/2r4b/1R6/6R1/4B2b/4p3/2N4B/2K5 w - - 0 19"
    #fen = "r3k2r/ppqbbppp/4p3/1bpp2B1/8/3BPN1P/PPQB1PP1/RN2K2R w KQkq - 0 9"
    move = "e4f3"
    legal, why_not, mlist = l_m.legal_move(fen, move)
    print (legal, why_not, "  ", move, mlist)
    start2 = time.time()
    secs = start2 - start
    print ("took ", secs, " seconds to run")