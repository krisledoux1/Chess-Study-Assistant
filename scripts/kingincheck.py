##############################################################################################
"""
    Chess Stats scripts to create a graphic user interface for OBD2 control using python-OBD
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
import sys
import logging
logger = logging.getLogger(__name__)
import scripts.sys_hook

logger = logging.getLogger(__name__)
def getrowcol(pospiece):
    row = 0
    col = 0
    #rows = [8,7,6,5,4,3,2,1,0] #rows 0 to 7.  col 0 to 7 added for space to reduce math calculation
    if pospiece > 7:
        remain = pospiece % 8
        col = remain
        x = (pospiece - remain) / 8
        row = int(x)
    else:           #pospiece 7 or less so it's the col
        row = 0
        col = pospiece
    return row, col

#end getrowcol function

def knightsquares(piecepossq, startrow, startcol):
    #piecepossq is piece square piece row and piece column
    s = [piecepossq-15, piecepossq-6, piecepossq+10, piecepossq+17, piecepossq+15, piecepossq+6, piecepossq-10, piecepossq-17]        #squares a knight could move to or check from in check routine
    squares_tocheck = []    #list of squares to check for checking knight based on startrow startcol
    #make a list of the squares a knight would be initiating check or could move to
    if startrow == 0:        #if piece in row 0 this is the list
        if startcol == 0:
            squares_tocheck = [s[2],s[3]]
        if startcol == 1:
            squares_tocheck = [s[2], s[3], s[4]]
        if startcol > 1 and startcol < 6:
            squares_tocheck = [s[2], s[3], s[4], s[5]]
        if startcol == 6:
            squares_tocheck = [s[3], s[4], s[5]]
        if startcol == 7:   #startcol = 7
            squares_tocheck = [s[4], s[5]]
    if startrow == 1:        #if king in row 1 this is the list
        if startcol == 0:
            squares_tocheck = [s[1],s[2],s[3]]
        if startcol == 1:
            squares_tocheck = [s[1], s[2], s[3], s[4]]
        if startcol > 1 and startcol < 6:
            squares_tocheck = [s[1], s[2], s[3], s[4], s[5], s[6]]
        if startcol == 6:
            squares_tocheck = [s[3], s[4], s[5], s[6]]
        if startcol == 7:   #startcol = 7
            squares_tocheck = [s[4], s[5], s[6]]
    if startrow > 1 and startrow < 6:        #if king in row 2-5 this is the list
        if startcol == 0:
            squares_tocheck = [s[0],s[1],s[2],s[3]]
        if startcol == 1:
            squares_tocheck = [s[7], s[0], s[1], s[2], s[3], s[4]]
        if startcol > 1 and startcol < 6:
            squares_tocheck = [s[7], s[0], s[1], s[2], s[3], s[4], s[5], s[6]]
        if startcol == 6:
            squares_tocheck = [s[7], s[0], s[3], s[4], s[5], s[6]]
        if startcol == 7:   #startcol = 7
            squares_tocheck = [s[7], s[4], s[5], s[6]]  
    if startrow == 6:        #if king in row 6 this is the list
        if startcol == 0:
            squares_tocheck = [s[0], s[1], s[2]]
        if startcol == 1:
            squares_tocheck = [s[7], s[0], s[1], s[2]]
        if startcol > 1 and startcol < 6:
            squares_tocheck = [s[7], s[0], s[1], s[2], s[5], s[6]]
        if startcol == 6:
            squares_tocheck = [s[7], s[0], s[5], s[6]]
        if startcol == 7:   #startcol = 7
            squares_tocheck = [s[7], s[5], s[6]]            
    if startrow == 7:        #if king in row 7 this is the list
        if startcol == 0:
            squares_tocheck = [s[0], s[1]]
        if startcol == 1:
            squares_tocheck = [s[7], s[0], s[1]]
        if startcol > 1 and startcol < 6:
            squares_tocheck = [s[7], s[0], s[1], s[6]]
        if startcol == 6:
            squares_tocheck = [s[7], s[0], s[6]]
        if startcol == 7:   #startcol = 7
            squares_tocheck = [s[7], s[6]]
    #print ("knight squares to check ", squares_tocheck)
    return squares_tocheck

#end knightsquares function

def generate_checkposlist(kingpos):     #make four lists of spaces to be checked for discovered or active check
                                                    #two list for diagonal two for row col. two each from piece start
                                                    #position and two from each end move position
    done = False                                                    
    step = 0
    angle = 8           # angles 0 to 7  8 means no angle attack
    kingrow, kingcol = getrowcol(kingpos)       #row and col 1- 8 of pieces
    #spiecerow, spiececol = getrowcol(spos)      
    #tospotrow, tospotcol = getrowcol(tpos)  

    diaglist = []     #list of the squares to examine around the king for discovered check
    diaglist.clear()
    rowcollist = []     #list of the squares to examine around the king for active direct check
    rowcollist.clear()


#if angle == 0:
    x = kingpos
    start = kingrow
    end = 0
    for y in range (start, end, -1):
        x -= 8
        if x > -1:
            rowcollist.append(x) 
    rowcollist.append("z")                       
#if angle == 1:
    x = kingpos
    start = kingcol
    end = 7
    for y in range (start, end):
        x -= 7
        if x > 0:
            diaglist.append(x)
    diaglist.append("z")            
#if angle == 2:
    x = kingpos
    start = kingcol
    end = 7
    for y in range (start, end):
        x += 1
        if x < 64:
            rowcollist.append(x) 
    rowcollist.append("z")             
#if angle == 3:
    x = kingpos
    start = kingcol
    end = 7
    for y in range (start, end):
        x += 9
        if x < 64:
            diaglist.append(x) 
    diaglist.append("z")               
#if angle == 4:
    x = kingpos
    start = kingrow
    end = 8
    for y in range (start, end):
        x += 8
        if x < 64:
            rowcollist.append(x)
    rowcollist.append("z")                       
#if angle == 5:
    x = kingpos
    start = kingcol
    end = 0
    for y in range (start, end, -1):
        x += 7
        if x < 64:
            diaglist.append(x) 
    diaglist.append("z")             
#if angle == 6:
    x = kingpos
    start = kingcol
    end = 0
    for y in range (start, end, -1):
        x -= 1
        if x > -1:
            rowcollist.append(x) 
    rowcollist.append("z")                           
#if angle == 7:
    x = kingpos
    start = kingcol
    end = 0
    for y in range (start, end, -1):
        x -= 9
        if x > -1:
            diaglist.append(x)
    diaglist.append("z")              
            

            
    return diaglist, rowcollist
    
#end generate_checkposlist function

def check_fromlist(dlist, rlist, kingpos, color_tocheck, tempsquares):
#checks to see if the king is in check using diaglist(dlist) rowcollist(rlist) and then knight check possibilities
#diagonal checks are checked for bishop or queen rowcol are checked for rook or queen pawn, knight checked separately
    checked = False
    ldlist = len(dlist)
    lrlist = len(rlist)
    #print (tempsquares)
    if color_tocheck.isupper():
        #king of player with move is white so see if white pieces (lowercase) are checking black king
        useupper = True
    else:
        useupper = False     #use upper case for black pieces checking white king
    

    counter = 0         #counter through list
    zcount = 0          #count the z's in the list  Should be 4  One for each diagonal
    pcounter = 0        #reset to 0 for pawn check at each z to check next diagonal
    done = False
    while not done:
        if done:
            break
        else:       #check dlist
            diagpiece = dlist[counter]  #spot in squares that piece is located number index 0 to 63  black always lower (0)
            if diagpiece == "z":    #end of one diagonal so move on to next unless done with all
                zcount += 1
                pcounter = -1
                if zcount == 4:
                    done = True         #checked angles 1 3 5 7 or 0 to 3
            else:
                if useupper:   #see if white (upper case pieces are checking black king used if whites turn else for blacks tun
                    piece_list_spot = tempsquares[diagpiece]
                    if piece_list_spot.islower() and piece_list_spot != "s":
                                   #lower case piece is black and blocks checking from that angle so stop checking angle "s" space
                        counter = dlist.index("z", counter) -1   #lower case (black) piece in path blocks check from that angle
                    if piece_list_spot == "Q" or piece_list_spot == "B":
                        checked = True
                        return checked
                    if piece_list_spot == "N" or piece_list_spot == "R":    #rook or knight blocks check  on diagonal
                        counter = dlist.index("z", counter) -1
                    if piece_list_spot == "P":      #if a white pawn check if close and at correct angle to check
                        if pcounter == 0:     #first diagonal in list is next to king 0 is first in list
                            if diagpiece > kingpos:     #pawn is in higher spot at angle so can check black king
                                checked = True
                                return checked
                        else:
                            counter = dlist.index("z", counter) -1        #pawn isnt at check angle so done as it will block all other check from that angle    
                else:               #see if black (lower case pieces are checking white king
                    piece_list_spot = tempsquares[diagpiece]
                    if piece_list_spot.isupper() and piece_list_spot != "s":
                                   #upper case piece is white and blocks checking from that angle so stop checking angle "s" space
                        counter = dlist.index("z", counter) -1     #upper case (white) piece in path blocks check from that angle
                    if piece_list_spot == "q" or piece_list_spot == "b":
                        checked = True
                        return checked
                    if piece_list_spot == "n" or piece_list_spot == "r":    #rook or knight blocks check  on diagonal
                        counter = dlist.index("z", counter) -1
                    if piece_list_spot == "p":      #if a black pawn check if close and at correct angle to check
                        if pcounter == 0:     #first diagonal in list is next to king 0 is first in list
                            if diagpiece < kingpos:     #pawn is in lower spot at angle so can check white king
                                checked = True
                                return checked
                        else:
                            counter = dlist.index("z", counter) -1  #pawn isnt at check angle so done as it will block all other check from that angle    
            counter += 1
            pcounter += 1


    counter = 0         #counter through list
    zcount = 0          #count the z's in the list  Should be 4  One for each diagonal
    done = False
    #print("Second half")
    while not done:
        if done:
            break
        else:       #check rlist
            diagpiece = rlist[counter]  #spot in squares that piece is located number index 0 to 63  black always lower (0)
            if diagpiece == "z":    #end of one diagonal so move on to next unless done with all
                zcount += 1
                pcounter = 0
                if zcount == 4:
                    done = True         #checked angles 1 3 5 7 or 0 to 3    
            else:        
                if useupper:        #see if white (upper case pieces are checking black king used if whites turn else for blacks tun
                    piece_list_spot = tempsquares[diagpiece]
                    if piece_list_spot.islower() and piece_list_spot != "s":
                                   #lower case piece is black and blocks checking from that angle so stop checking angle "s" space
                        counter = rlist.index("z", counter) -1  #lower case (black) piece in path blocks check from that angle
                    if piece_list_spot == "Q" or piece_list_spot == "R":
                        checked = True
                        return checked
                    if piece_list_spot == "B" or piece_list_spot == "N":    #rook or knight blocks check  on diagonal
                        counter = rlist.index("z", counter) -1
                    if piece_list_spot == "P":      #if a white pawn
                        counter = rlist.index("z", counter) -1
                else:               #see if black (lower case pieces are checking white king
                    piece_list_spot = tempsquares[diagpiece]
                    if piece_list_spot.isupper() and piece_list_spot != "s":
                                   #upper case piece is white and blocks checking from that angle so stop checking angle "s" space
                        counter = rlist.index("z", counter) -1         #upper case (white) piece in path blocks check from that angle
                    if piece_list_spot == "q" or piece_list_spot == "r":
                        checked = True
                        return checked
                    if piece_list_spot == "b" or piece_list_spot == "n":    #rook or knight blocks check  on diagonal
                        counter = rlist.index("z", counter) -1
                    if piece_list_spot == "p":      #if a black pawn
                        counter = rlist.index("z", counter) -1
            counter += 1

    #print("knight!")                     
    #check if a nasty ass knight is checking!!!     
    rowk,colk = getrowcol(kingpos)
    knight_spots = knightsquares(kingpos, rowk, colk)
    #print(rowk,colk,"Knightsquares ",knight_spots)
    zz = len (knight_spots)
    #if moved_piece == "N" and useupper:      #White pieces checking the black King and piece moved is knight
    if useupper:
        for x in range (0, zz):
            #print("kspot ",tempsquares[knight_spots[x]])
            if tempsquares[knight_spots[x]] == "N":
                checked = True
                return checked
    else:
        for x in range (0, zz):
            #print("kspot ",tempsquares[knight_spots[x]])
            if tempsquares[knight_spots[x]] == "n":
                checked = True
                return checked        
    return checked
    
#end check_fromlist function                         

def is_king_incheck(spos, tpos, squares, whosemove):   #checking to see if suggested move will result in check or discovered check
                                            #assume not in check before move as that would be a bad move
                                            #and should never happen if chess gui not buggy
    #row and column are 1 to 8 and 1 to 8  no letters just numbers                                        
    #    if spos > 64 then looking for check to see if fen is legal since if opponent is in check asking for your move is
    # illegal and will mess up engine
    #x = 10 / 0
    check = False
    kinfen = str (squares)
    if "k" in kinfen and "K" in kinfen: #make sure there are two kings in fen or its a bad fen
        tempsquares = squares.copy()   #to make sure squares doesn't get changed
        #print("temp1 ",tempsquares,"spos ",spos, " tpos ",tpos)
        if spos < 65:           # checking a suggested move if spos set to 66 for checking if king already in check
       
            #change tempsquares to reflect suggested move so that it can be tested for check
            spiece = tempsquares[spos]    #get piece at first square of move (always a piece)
            tospot = tempsquares[tpos]    #piece at object square or if it is a space (could be space or piece 
            tempsquares[spos] = "s"     #make start position vacated square an s for space
            tempsquares[tpos] = spiece  #tempsquares now reflect squares with suggested move made 
            if whosemove == "w":        #if whites move check white pieces to see if white will be checking 
                color_tocheck = "K"
                #ncolor = "N"
                kingpos = tempsquares.index("k")
            else:
                color_tocheck = "k"     #if blacks move check black pieces to see if black wil be checking 
                #ncolor = "n"
                kingpos = tempsquares.index("K")             
            #here we are checking for suggested move will opponent be in check   
            #print("temp ",tempsquares)
        else:
        #here we are checking to see if opposing king is in check before requesting a move from engine.  If in check
            #request would be illegal fen so we need to tell gui not to send request
            if whosemove == "w":        
                color_tocheck = "K"
                kingpos = tempsquares.index("k")
                #ncolor = "N"
            else:
                color_tocheck = "k"     
                kingpos = tempsquares.index("K")
                #ncolor = "n"             
        dlist, rlist = generate_checkposlist(kingpos)
        
        #print (dlist,"\n",rlist, "\n")
        #print ("King",color_tocheck, "  ",kingpos) 
        check = check_fromlist(dlist, rlist, kingpos, color_tocheck, tempsquares) 
        #print ("check state ", check) 
        if check:
            #print("Checked")
            return check
    else:
        check = True
        
    return check
#end is_king_incheck function

#whosemove = "w"
#squares = ['r', 'n', 'b', 'q', 's', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'N', 'P', 'p', 'p', 's', 's', 's', 's', 's', 's', 's', 's', 'k', 's', 's', 's', 's', 's', 's', 's', 'q', 's', 'K', 's', 's', 's', 's', 's', 's', 's', 's', 's', 's', 's', 's', 's', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'R', 'N', 'B', 'Q', 's', 'B', 'N', 'R']
#spo = 66
#tpo = 18
#incheck = is_king_incheck( spo, tpo, squares, whosemove)
#if incheck:
#    print ("check!!!!!")
#else:
#    print ("not checked")    


