#! /usr/bin/env python3

##############################################################################################
"""
    Chess Board scripts to create a chess analysis program using Stockfish as an engine
    Used in Chess Study Assistant
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
#logging setup
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import csv

###############################################################################################
#version 1.0.0

from scripts.promo import promo
import tkinter as tk
from tkinter.filedialog import asksaveasfile
from tkinter import messagebox
import copy
import time
import libs.chess as chess
import libs.chess.pgn
from scripts.legalmove import legal_moves
from scripts.pgn import get_headers
import libs.pyautogui as pyautogui


class board_control():
    def __init__(self, root, engine, contwin = False, anadata = "", s_move = 1, asheet = ""):
        self.root = root                            #link to the main window
        self.engine = engine                    #connector to engine   
        self.asheetref = asheet                 #reference to the table asheet so it can be syncronized  
        self.anadata = anadata                  #keep for reset
        self.s_move = s_move
        self.contwin = contwin              #if a continue window rather than a board window
        self.calc_score = []                    #list of calculated scores from anadata if wanted
        self.calc_diff = []                         #list of the differences between calculated best move and actual move score
        self.target_row = 1                      #target row of asheet table that is selected.  Calculate from s_move and then self.currentmove 
        self.orig_continu = True                #change to false if new continuation is calculated
        self.ds_color = "#4476e2"           #color of canvas dark squares
        self.ls_color = "#95c7ed"           #color of canvas light squares  
        self.board_closed = False           #on close tell caller that window closed
        self.calculating = False                #True when assistant is calculating moves
        self.assist = tk.IntVar(value=0)        #variable to turn on or off analysis        
        self.fen = ""                                       #fen of current position shown on board  
        self.l_m = legal_moves()         #instance of legalmoves class  
        self.opening = open_find("all.tsv")     #create a opening object with a searchable dictionary
        self.opening_name = "Chess Window"  #original setting of opening name as will be used as window title
        if self.contwin == False:    
            self.orig_continu = False            
            self.chess_window()                     #open a window to control and display a chess board
        else:                   #if this is a continuation window set up so that window will be correct when called
            self.gd = game_data()           #create the game_data object to hold game information    
            self.setup_gd(anadata)   
            self.assist.set(1)              #set a default of assist on when continuing so that new move will calculate
            self.continue_window()

    def chess_window(self):  
        logging.info("Opening chess window")                   
        self.chessw = tk.Toplevel(self.root, bg= self.ds_color)#, takefocus=True)         
        #wtitle = "Chess Window"
        self.chessw.title(self.opening_name)
        self.chessw.geometry("+1240+350")       #position of window
        self.chessw.attributes('-topmost', 'true')
        #self.chessw.wait_visibility()  # Wait until visible to ensure grab works smoothly   
        #self.chessw.grab_set()
        self.chessw.focus_set()
        colors = []    
        colors.append("#4476e2")           #color of canvas dark squares
        colors.append("#95c7ed")           #color of canvas light squares            
        fbcolor = colors[0]
        bbgcolor = colors[1]
        mv_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame at bottom of window
        mv_frm.pack(fill="x", side=tk.BOTTOM)    
        save_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Save PGN",
            width = 9,
            command=self.save_as_pgn
        )   
        filename = "pieces_image/"
        img = tk.PhotoImage(file="pieces_image/rotate.png")       
        rotate_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            #text = "R",
            image=img,
            cursor='hand2',
            width = 32,
            command=self.rotate
        )            
        bak_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Prev",
            width = 5,
            command=self.step_back
        )            
        fwd_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Next",
            width = 5,
            command=self.step_forward
        )  
        self.info_lbl = tk.Label(
            master = mv_frm,
            bg = fbcolor,
            text = "Original Board",
            width = 26,
            anchor='w'
        )  
        save_button.pack(side=tk.LEFT)        
        self.info_lbl.pack(side=tk.LEFT, padx = 15)
        rotate_button.pack(padx=31, side=tk.LEFT)
        bak_button.pack(side=tk.LEFT, padx = 5)
        fwd_button.pack(side=tk.LEFT, padx = 5)     
        botname_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        botname_frm.pack(fill="x", side=tk.BOTTOM)  
        self.botname= tk.StringVar(value="WNN")  
        botname_ent = tk.Entry(botname_frm, textvariable=self.botname, width = 63, bg = bbgcolor) 
        botname_ent.pack(fill="x", side=tk.RIGHT, padx = 8, pady = 4)   
        canvas_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        canvas_frm.pack(fill="both", side=tk.BOTTOM)                                
        score_frm = tk.Frame(self.chessw, bg = fbcolor)    
        score_frm.pack(fill="x", side=tk.TOP)           
        on_image = tk.PhotoImage(width=48, height=24)
        off_image = tk.PhotoImage(width=48, height=24)
        on_image.put(("green",), to=(0, 0, 48,48))
        off_image.put(("red",), to=(0, 0, 48, 48))    
        self.assist.trace("w", self.assistchange)            
        cb1 = tk.Checkbutton(score_frm, image=off_image, selectimage=on_image, indicatoron=False, border=2,
                             onvalue=1, offvalue=0, variable=self.assist)
        #cb1.pack(padx=20, pady=10) 
        cb1.pack(side=tk.LEFT)       
        self.engine_assist_btn = tk.Button(
            master = score_frm,
            bg = bbgcolor,
            text = "Engine",
            width = 6,
            font = ("Arial", 12, "bold"),
            anchor = "c",
            command = self.calc_move
        )
        self.engine_assist_btn.pack(side=tk.LEFT, padx = 3) 
         
        self.assist_lbl = tk.Label(
            master = score_frm,
            bg = bbgcolor,
            text = str("Scoring"),
            width = 42,
            font=("Arial", 12, "bold"),
            anchor='c'
        )  
        self.assist_lbl.pack(side=tk.LEFT) 
        topname_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        topname_frm.pack(fill="x", side=tk.TOP) 
        self.topname= tk.StringVar(value="BNN")            
        topname_ent = tk.Entry(topname_frm, textvariable=self.topname, width = 63, bg = bbgcolor) 
        topname_ent.pack(fill="x", side=tk.RIGHT, padx = 8, pady = 4)             
        
        self.chessw.bind("<Right>", lambda event: self.step_forward())  #step forward
        self.chessw.bind("<Left>", lambda event: self.step_back())          #step back
        self.chessw.bind("<Escape>", lambda event: self.on_close())         #close window
        self.chessw.bind("b", lambda event: self.restart())   #beginning       
        self.chessw.bind("r", lambda event: self.rotate())   #rotate display          
        self.gd = game_data()           #create the game_data object to hold game information                        
        self.cb = chessboard(canvas_frm, self.root, self, self.gd, self.l_m, colors)                           #create the canvas of the chess board        
        self.chessw.protocol("WM_DELETE_WINDOW",  self.on_close)
        self.root.wait_window(self.chessw)

    def continue_window(self):  

        logging.info("Opening chess window")                   
        self.chessw = tk.Toplevel(self.root, bg= self.ds_color)#, takefocus=True)         
        wtitle = "Chess Window"
        self.chessw.title(wtitle)
        self.chessw.geometry("+1240+350")       #position of window
        self.chessw.attributes('-topmost', 'true')
        #self.chessw.wait_visibility()  # Wait until visible to ensure grab works smoothly   
        #self.chessw.grab_set()
        self.chessw.focus_set()
        colors = []          
        colors.append("#b78c47")           #color of canvas dark squares
        colors.append("#e8dcc9")           #color of canvas light squares            
        fbcolor = colors[0]
        bbgcolor = colors[1]
        mv_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame at bottom of window
        mv_frm.pack(fill="x", side=tk.BOTTOM)    
        save_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Save PGN",
            width = 9,
            command=self.save_as_pgn
        )   
        filename = "pieces_image/"
        img = tk.PhotoImage(file="pieces_image/rotate.png")       
        rotate_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            #text = "R",
            image=img,
            cursor='hand2',
            width = 32,
            command=self.rotate
        )            
        bak_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Prev",
            width = 5,
            command=self.step_back
        )            
        fwd_button = tk.Button(
            master = mv_frm,
            bg = bbgcolor,
            text = "Next",
            width = 5,
            command=self.step_forward
        )  
        self.info_lbl = tk.Label(
            master = mv_frm,
            bg = fbcolor,
            text = "Original Board",
            width = 26,
            anchor='w'
        )  
        save_button.pack(side=tk.LEFT)        
        self.info_lbl.pack(side=tk.LEFT, padx = 15)
        rotate_button.pack(padx=31, side=tk.LEFT)
        bak_button.pack(side=tk.LEFT, padx = 5)
        fwd_button.pack(side=tk.LEFT, padx = 5)     
        botname_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        botname_frm.pack(fill="x", side=tk.BOTTOM)  
        self.botname= tk.StringVar(value="WNN")  
        botname_ent = tk.Entry(botname_frm, textvariable=self.botname, width = 63, bg = bbgcolor) 
        botname_ent.pack(fill="x", side=tk.RIGHT, padx = 8, pady = 4)   
        canvas_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        canvas_frm.pack(fill="both", side=tk.BOTTOM)                                
        score_frm = tk.Frame(self.chessw, bg = fbcolor)    
        score_frm.pack(fill="x", side=tk.TOP)           
        on_image = tk.PhotoImage(width=48, height=24)
        off_image = tk.PhotoImage(width=48, height=24)
        on_image.put(("green",), to=(0, 0, 48,48))
        off_image.put(("red",), to=(0, 0, 48, 48)) 
        self.assist.trace("w", self.assistchange)                         
        cb1 = tk.Checkbutton(score_frm, image=off_image, selectimage=on_image, indicatoron=False, border=2,
                             onvalue=1, offvalue=0, variable=self.assist)
        cb1.pack(side=tk.LEFT)       
        self.engine_assist_btn = tk.Button(
            master = score_frm,
            bg = bbgcolor,
            text = "Engine",
            width = 6,
            font = ("Arial", 12, "bold"),
            anchor = "c",
            command = self.calc_move
        )
        self.engine_assist_btn.pack(side=tk.LEFT, padx = 3) 
        self.s_lbl = tk.Label(
            master = score_frm,
            bg = bbgcolor,
            text = str("Scores"),
            width = 6,
            font=("Arial", 12, "bold"),
            anchor='c'
        )  
        self.s_lbl.pack(side=tk.LEFT)          
        self.assist_lbl = tk.Label(
            master = score_frm,
            bg = bbgcolor,
            text = str("Scoring"),
            width = 35,
            font=("Arial", 12, "bold"),
            anchor='c'
        )  
        self.assist_lbl.pack(side=tk.LEFT) 
        spacer = tk.Frame(master = score_frm, bg = fbcolor, width = 9, height = 3)
        spacer.pack(side = tk.RIGHT)                
        self.diff_lbl = tk.Label(
            master = score_frm,
            bg = bbgcolor,
            text = str(""),
            width = 5,
            font=("Arial", 12, "bold"),
            anchor='c'
        )  
        self.diff_lbl.pack(side=tk.RIGHT)           
        self.d_lbl = tk.Label(
            master = score_frm,
            bg = bbgcolor,
            text = str("Diff"),
            width = 3,
            font=("Arial", 12, "bold"),
            anchor='w'
        )  
        self.d_lbl.pack(side=tk.RIGHT)                
        topname_frm = tk.Frame(self.chessw, bg = fbcolor)    #frame for bottom name
        topname_frm.pack(fill="x", side=tk.TOP) 
        self.topname= tk.StringVar(value="BNN")            
        topname_ent = tk.Entry(topname_frm, textvariable=self.topname, width = 63, bg = bbgcolor) 
        topname_ent.pack(fill="x", side=tk.RIGHT, padx = 8, pady = 4)                     
        self.chessw.bind("<Right>", lambda event: self.step_forward())
        self.chessw.bind("<Left>", lambda event: self.step_back()) 
        self.chessw.bind("<Escape>", lambda event: self.on_close()) 
        self.chessw.bind("b", lambda event: self.continu_restart())      #beginning    
        self.chessw.bind("r", lambda event: self.rotate())   #rotate display                                        
        self.cb = chessboard(canvas_frm, self.root, self, self.gd, self.l_m, colors)                           #create the canvas of the chess board        
        self.chessw.protocol("WM_DELETE_WINDOW",  self.on_close)
        self.chessw.after(300, self.continue_first)
        self.root.wait_window(self.chessw)

    def setup_gd(self, anadata):  
        self.calc_score = []
        self.calc_diff = [] 
        #smove number of halfmoves that have occurred with 1 as a base not 0
        #so move 1 white would be 1 move 1 black would be two 2 white would be 3
        for x in self.anadata.list_oflists:              #go through lists and get scores and differences for each move
            self.calc_diff.append(x[3])                 #add white calculated diff
            self.calc_score.append(x[5])                #add white calculated score
            self.calc_diff.append(x[8])                     #add black calculated diff
            self.calc_score.append(x[10])                 #add black calculated score
        self.calc_diff.pop(0)                               #get rid of non integer first in list
        self.calc_score.pop(0)
        if self.calc_diff[-1] == "":
            self.calc_diff.pop()
        self.calc_diff.append(0.0)
        self.calc_diff.append(0.0)              #making sure not to get an index out of range            
        if self.calc_score[-1] == "":
            self.calc_score.pop()
        self.calc_score.append(0.0)    
        self.calc_score.append(0.0)                    
        self.gd.currentmove_set(self.s_move)
        self.target_row = (self.s_move-1)//2        #integer division returns rounded down whole number halfmoves should be accurate now
        self.gd.white_p = anadata.lbldict["namew"]
        self.gd.black_p = anadata.lbldict["nameb"]
        squares = []     
        #get lists from anadata (analyzed data object)
        fens = anadata.getfens()
        long_alg = anadata.getlongalg()
        #sans = anadata.getsans()
        b_moves = anadata.getbestmoves()
        b_scores = anadata.getbestscores()
        #put anadata lists into game data format
        tot_moves = len(long_alg)
        self.gd.totalmoves_set(tot_moves)
        self.gd.fenlist.pop()           #get rid of initial fen in game data since continue starts with a fen of the continuation
        self.gd.squares.pop()       #same as above
        self.gd.bestmoves_pop(0)     #when showing continuation bestmoves [0] is not "", "", ""
        self.gd.bestscores_pop(0)
        for x in range(tot_moves):
            self.gd.fenlist_append(fens[x])
            squares = self.gd.fen_to_squares(fens[x])
            self.gd.squares_append(squares)
            self.gd.movelist_append(long_alg[x])
            self.gd.bestmoves_append(b_moves[x])
            self.gd.bestscores_append(b_scores[x])
            #self.gd.san_moves_append(sans[x])
           
    def continue_first(self):           #set up before first move but after gd created and updated    
        def do_castling(pname):
            castle = self.gd.castle_get()
            if pname.isupper():        #white king has been moved    
                if "Q" in castle: castle = castle.replace("Q", "")
                if "K" in castle: castle = castle.replace("K", "")
            else:                       #black king was moved            
                if "q" in castle: castle = castle.replace("q", "")
                if "k" in castle: castle = castle.replace("k", "")
            self.gd.castle_set(castle)                 
        def check_castling(scol, pname):           #check movements and update castling to reflect move scol original column int
            castle = self.gd.castle_get()
            if pname.isupper():        #white piece has been moved
                if pname == "K":       #remove all castling for white
                    if "Q" in castle: castle = castle.replace("Q", "")
                    if "K" in castle: castle = castle.replace("K", "")
                if pname == "R":       #white rook was moved
                    if scol == 1:    #queens rook so change queenside for white if it was available
                        if "Q" in castle:
                            castle = castle.replace("Q", "") #if castling to that side was good then change it so that it is not any more
                    if scol == 8:    #kings rook so change kingside for white if it was available
                        if "K" in castle:
                            castle = castle.replace("K", "")                               
            else:                       #piece moved is black                      
                if pname == "k":       #remove all castling for black
                    if "q" in castle: castle = castle.replace("q", "")
                    if "k" in castle: castle = castle.replace("k", "") 
                if pname == "r":       #white rook was moved
                    if scol == 1:    #queens rook so change queenside for white if it was available
                        if "q" in castle:
                            castle = castle.replace("q", "") #if castling to that side was good then change it so that it is not any more
                    if scol == 8:    #kings rook so change kingside for white if it was available
                        if "k" in castle:
                            castle = castle.replace("k", "")                                                    
            if castle == "": castle = "-"         #castle can never be a null ""            
            self.gd.castle_set(castle)      
        #since analysis does not have the fen or squares after the last move they must be added here to allow last move to be simulated made
        tot_moves = self.gd.totalmoves_get()        
        self.gd.bestmoves_append(["","",""])        #replace popped to keep len of list consistant
        self.gd.bestscores_append(["","",""])
        castled = False
        fullalg = self.gd.movelist_get(tot_moves)
        currsquares = self.gd.squares_get(tot_moves-1)      #-1 because the lenght of these are shorter than the others from pop
        currentfen = self.gd.fenlist_get(tot_moves-1)
        fen_list = currentfen.split(" ")                #splits the fen into a list of items that were separated by a space   
        self.gd.whosemove_set(fen_list[1])
        self.gd.castle_set(fen_list[2])                 #set gd castling to reflect condition of previous fen
        self.gd.passant_set(fen_list[3])                #set passant from prev fen
        self.gd.pawnorcapture_set(int(fen_list[4]))
        self.gd.fenmove_set(fen_list[5])
        fromto = self.cb.get_move_squares(fullalg)      #returns the squares of the move
        place1 = fromto[0]
        place2 = fromto[1]            
        pname = currsquares[place1]
        upiece = pname.upper()     #make piece uppercase for easier checking for king or rook 
        numcolsmoved = 0
        cols = ["none","a","b","c","d","e","f","g","h"]        
        scol = cols.index(fullalg[0])  #get original column by integer
        col = cols.index(fullalg[2])  #get move to column by integer        
        if upiece == "K":               #if it's a king move see how many columns moved, if greater than 1 it's a castle move
            numcolsmoved = abs(col - scol)       #used to determine if king moves more than one column meaning castle 
        if numcolsmoved > 1:               #piece moved was a king and more than 1                                        
            do_castling()               #moves both pieces moved in a castle move
            castled = True
        if upiece == "K" or upiece == "R":      #if king or rook move affects castling
            check_castling(scol, pname)       #scol is the origination column number
        newsquares = self.cb.newsquares(currsquares, fullalg, castled)      #castled means was move a castle True False            
        lfen = self.cb.squares_to_fenfront (newsquares)     #get the left side of the new fen from squares    
        mn = self.gd.fenmove_get()            
        w_m = self.gd.whosemove_get()
        if w_m == "b":          #if black moved then increment movenum (fenmove)
            self.gd.fenmove_increment()
        self.gd.whosemove_toggle()      #set other side to move at next move for new FEN    
        w_m = self.gd.whosemove_get()                                  
        sp = " " 
        poc = str(self.gd.pawnorcapture_get())
        mn = self.gd.fenmove_get()
        castle = self.gd.castle_get()
        passant = self.gd.passant_get()
        cfen = lfen + w_m + sp + castle + sp + passant +  sp + poc + sp + mn 
        self.gd.fenlist_append(cfen)        #replace popped to keep len of list consistant
        self.gd.squares_append(newsquares)        #replace popped to keep len of list consistant        
        self.continue_second()                      #now that gself.gd is correct set up board

    def continue_second(self):    #set board to initial position        
        self.cb.highlight_clear()       #clear all highlights on board
        #delete pieces from the board so they can be replaced on canvas
        for x in range(64):
            squaretag = "z" + str(x)                    #this is the tag the piece on that square has if there is a piece there
            self.cb.canvas.delete(squaretag)       #deletes the piece with that tag from the board    
        #delete pieces from the capture board so they can be replaced on capcanvas
        for x in range(32):   
            tag = "z" + str(x)
            self.cb.capcanvas.delete(tag)       #deletes the piece with that tag from the capture canvas                                     
        nextmove = self.gd.currentmove_get()
        #set names
        self.topname.set(self.gd.black_p)   
        self.botname.set(self.gd.white_p)              
        fen = self.gd.fenlist_get(nextmove-1)   #get fen from last move or original fen
        self.gd.parse_fen(fen)                      #set fen variables to next move                           
        nextsquares = self.gd.squares_get(nextmove-1)#        
        move = self.gd.movelist_get(nextmove)    
        self.tksee()           
        #get any capture info for the move True is direct_f True
        cap_change = self.capture_calc(True, self.cb.blankboard, nextsquares)
        #update parameters of game that need changing
        if cap_change != "":
            self.gd.captured_add(cap_change)        
        self.cb.update_bd(self.cb.blankboard, nextsquares)              
        #self.gd.currentmove_set(nextmove +1)       #update current move            
        #change board to reflect previous move   
        hlsquares = self.cb.get_move_squares(move)
        self.cb.highlight_squares(hlsquares, "white")
        self.label_update(new_move = False)       

    def assistchange(self, *args):
        x = self.assist.get()
        outstr = "Assist button toggled, currently " + str(x)
        logging.info(outstr)

    def tksee(self):         #tksheet make sure row is visible on sheet
        if self.orig_continu:           #if no new calculation of a continuation has been done
            # Get total number of visible rows
            s, e = self.asheetref.visible_rows
            visible_rows = e - s 
            #print("Target row ",target_row) 
            #print("high vis ",e)
            #print("low vis ",s) 
            # Calculate target row (ensure it doesn't go below 0)
            if self.target_row < s + 5:
                center_row = max(0, s - 5)     
            else:
                center_row = max(0, self.target_row + 5)   
            #print("Center row ",center_row)
            max_row = self.asheetref.get_total_rows() - 1
            if center_row > max_row:  
                center_row = max_row  
            self.asheetref.see(row=center_row, column=0)
            #set then move (white or black)
            if self.gd.whosemove_get() == "w":
                #if halfmoves > 0:
                self.asheetref.select_cell(self.target_row,1)            
            else:
                self.asheetref.select_cell(self.target_row,6)          
            #self.asheetref.refresh() 

    def on_close(self):
        self.board_closed = True           #variable to tell caller that pgn window is closed
        self.chessw.destroy()

    def rotate(self):
        self.cb.rotate_board()
        #rotate names from top to bottom when board rotated  Get
        wname = self.botname.get()
        bname = self.topname.get()
        #change
        self.topname.set(wname)
        self.botname.set(bname)           

    def save_as_pgn(self):
        if self.calculating:
            outstr = "Not saving because calculation is in progress"
            logging.info(outstr)
            return          #calculation in progress so not performing click function
        if self.cb.white_on_bottom:
            wname = self.botname.get()
            bname = self.topname.get()
        else:
            wname = self.topname.get()
            bname = self.botname.get()                        
        saveanalyze, headers = get_headers(self.chessw, wname, bname)
        #print(saveanalyze, " ", headers)
        if saveanalyze == 0:
            return
        game = chess.pgn.Game()
        game.headers["Event"] = headers[0]
        game.headers["Site"] = headers[1]
        game.headers["Date"] = headers[2]       
        game.headers["Round"] = headers[3]
        game.headers["White"] = headers[4]
        game.headers["Black"] = headers[5]
        game.headers["Result"] = headers[6]
        game.headers["Comment"] = headers[7]        
        if self.gd.totalmoves_get() > 1:
            node = game.add_variation(chess.Move.from_uci(self.gd.movelist_get(1)))
            x = 0
            for i in self.gd.movelist:
                if x > 1:
                    node = node.add_variation(chess.Move.from_uci(i))
                x +=1
        #node.comment = "Comment"   
        file_types = [('PGN files', '*.pgn'), ('All files', '*.*')]
        file = asksaveasfile(
            mode='a',
            confirmoverwrite = False,
            filetypes=file_types,
            defaultextension='.pgn',
            title="Save your PGN to a file"
        )
        gamestr = str(game)
        if file:
            file.write(gamestr)
            file.write("\n\n")
            file.close()
            logging.info("File saved successfully!")
        else:
            logging.info("Save operation cancelled")
        self.chessw.destroy()
        self.cb = ""
        self.gd = ""

    def capture_calc(self, direct_f, prevsquares, currsquares):
        main_list = []
        wpieces = ["Q", "B", "N", "R", "P"]
        bpieces = ["q", "b", "n", "r", "p"]
        w_m = self.gd.whosemove_get()
        listcount1 = []
        listcount2 = [] 
        if not direct_f:             #stepping direct_f
            if w_m == "b":
                checkcolor = wpieces
            else:
                checkcolor = bpieces  
        else:                      #stepping backward
            if w_m == "b":
                checkcolor = bpieces
            else:
                checkcolor = wpieces              
        for i in checkcolor:
            x = currsquares.count(i)
            listcount1.append(i + str(x))
            y = prevsquares.count(i)
            listcount2.append(i + str(y))
        #gives you what is different in the second list
        cap_list = [b for a, b in zip(listcount1, listcount2) if a!= b]  
        cap = ""
        if len(cap_list) > 0:
            cap = cap_list[0]
            cap = cap[0]                
        return cap    

    def continu_restart(self):
        logging.info("Continu begin again pressed")
        self.chessw.destroy()
        self.gd = game_data()           #create the game_data object to hold game information    
        self.setup_gd(self.anadata)  
        self.orig_continu = True 
        self.assist.set(1)              #set a default of assist on when continuing so that new move will calculate
        self.continue_window()                

    def restart(self):
        logging.info("Entry board begin again pressed")    
        self.gd.currentmove_set(1)       #update current move to the first move 
        self.gd.fenmove_set(1)         
        self.cb.highlight_clear()       #clear all highlights on board
        #delete pieces from the board so they can be replaced on canvas
        for x in range(64):
            squaretag = "z" + str(x)                    #this is the tag the piece on that square has if there is a piece there
            self.cb.canvas.delete(squaretag)       #deletes the piece with that tag from the board            
        csquares = self.gd.squares_get(0)
        self.cb.cfen = self.gd.fenlist_get(0)
        outstr = ""
        self.info_lbl['text'] = outstr          
        self.cb.update_bd(self.cb.blankboard,csquares)              #original board had nothing on it so empty list of -    
        self.cb.calc_capture_display(csquares) 
        self.step_forward()             
        self.step_back()
             
    def step_forward(self):
        if self.calculating:
            outstr = "Not stepping forward because calculation is in progress"
            logging.info(outstr)
            return          #calculation in progress so not performing click function        
        direct_f = True
        nextmove = self.gd.currentmove_get()

        if nextmove <= self.gd.totalmoves_get():
            self.cb.highlight_clear()       #clear all highlights on board
            fen = self.gd.fenlist_get(nextmove)
            self.gd.parse_fen(fen)                      #set fen variables to next move                        
            nextsquares = self.gd.squares_get(nextmove)
            currsquares = self.gd.squares_get(nextmove -1)
            move = self.gd.movelist_get(nextmove)        
            #get any capture info for the move
            cap_change = self.capture_calc(direct_f, currsquares, nextsquares)
            #update parameters of game that need changing
            if cap_change != "":
                self.gd.captured_add(cap_change)
            self.gd.currentmove_set(nextmove +1)       #update current move   
            self.target_row = (nextmove)//2        #integer division returns rounded down whole number halfmoves should be accurate now 
            if nextmove < self.gd.totalmoves_get():
                self.tksee()                    #sync tksheet row and move                
            #change board to reflect previous move   
            hlsquares = self.cb.get_move_squares(move)
            self.cb.highlight_squares(hlsquares, "white")
            self.cb.update_bd(currsquares, nextsquares)
            self.label_update(new_move = False) 
            outstr = "Next move " + str(nextmove) + " of " + str(self.gd.totalmoves_get()) + " " + move
            logging.info(outstr) 
            game_over, status = self.l_m.is_there_move(self.gd.fenlist_get(nextmove)) 
            if game_over:
                self.chessw.attributes('-topmost', False)
                outstr = "Game is over!  Result is " + status
                messagebox.showinfo("Game Over", outstr)
                self.chessw.attributes('-topmost', True)  
                self.chessw.update()              
                logging.info(outstr)              
        #print(self.gd.bestmoves)               

    def step_back(self):#
        if self.calculating:
            outstr = "Not stepping back because calculation is in progress"
            logging.info(outstr)
            return          #calculation in progress so not performing click function    
        direct_f = False
        lastmove = self.gd.currentmove_get() -1     #get the number of the previous move     
        if lastmove > 0:
            self.cb.highlight_clear()       #clear all highlights on board
            fen = self.gd.fenlist_get(lastmove-1)           #get FEN from lastmove
            self.gd.parse_fen(fen)                      #set fen variables to last move        
            prevsquares = self.gd.squares_get(lastmove-1)   #get squares from before lastmove          
            currsquares = self.gd.squares_get(lastmove)        #get squares as they are               
            prevmove = self.gd.movelist_get(lastmove)           #get the long algebra of lastmove
            #get any capture info for the move
            cap_change = self.capture_calc(direct_f, prevsquares, currsquares)
            #update parameters of game that need changing
            if cap_change != "":
                self.gd.captured_delete(cap_change)
            self.gd.currentmove_set(lastmove)       #update current move to the last move            
            curr = self.gd.currentmove_get()                        
            self.target_row = (curr-1)//2        #integer division returns rounded down whole number halfmoves should be accurate now 
            self.tksee()                    #sync tksheet row and move                 
            #change board to reflect previous move   
            hlsquares = self.cb.get_move_squares(prevmove)
            self.cb.highlight_squares(hlsquares, "white")
            self.cb.update_bd(currsquares, prevsquares)
            self.label_update(new_move = False)
            outstr = "Prev move " + str(lastmove) + " of " + str(self.gd.totalmoves_get()) + " " + prevmove
            logging.info(outstr)               
    
    def algebra_to_san(self, alg, squares_cont):            #change algebraic long to san Short alg notation
                                        #squares 0 is always a8 br home
                                        #squares is a 0 to 63 designation of piece or space "-"
                                        #on the chessboard from 8a to h1
        #self.l_m.display_squares(squares_cont) 
        first = ""                                   
        columns = ["a","b","c","d","e","f","g","h"]  # 0 - 7
        rows = ["8","7","6","5","4","3","2","1","0"] #rows 0 to 7.  8 added for space to reduce math calculation
        san2 = ""
        san5 = ""
        if len(alg) < 4:
            return ""                  #bad algebra move
        #print("thisisalg ",alg)
        if len(alg) > 4:        #if alg is longer than 4 digits then a promotion is place 4
            san4 = alg[4]      #if a promotion then a fifth letter of promotion piece recomended
        else:
            san4 = ""
        alg1 = alg[0:2]
        alg2 = alg[2:4]
        first = alg[0]      #first char of alg
        col1 = columns.index(first) #place in list is value needed for col
        second = alg[1]     #second char of alg
        row1 = rows.index(second)   #place in list is value needed for row
        place1 = (row1 * 8) + col1 #calculate position in squares_cont list
        third = alg[2]      #third char of alg is first of second half of move
        col2 = columns.index(third)
        fourth = (alg[3])                                  
        row2 = rows.index(fourth)    #place in list is value needed for row
        place2 = (row2 * 8) + col2  #calculate position in squares_cont list
        san3 = third + fourth  #second half of algebraic will be used for san
        tospot = squares_cont[place2]    #piece at object square or if it is a space (could be space or piece 
        spiece = squares_cont[place1]    #get piece at first square of move (always a piece)
        if spiece.isupper():    #if originating piece is uppercase it is whites move so check opposite for check (reversed here) to show in SAN
            whosemove = "b"
        else:
            whosemove = "w"        
        u_spiece = spiece.upper()   #uppercase piece letter  
        if u_spiece == "P":     #san1 is first half of san string.  If a pawn
            san1 = first    #if a pawn san only uses column unless a capture is made on move
            if tospot == "-":
                san1 = ""   #if a pawn is moved to a space then only second part of move is san
            if tospot == "-" and col2 != col1:    #en_passant move
                san1 = first + "x"   #mark that pawn taken en passant
        else:
            san1 = u_spiece #if a piece san uses capitalized piece letter
        if tospot != "-":       #if move to spot is a piece and not a space
            san2 = "x"          #if not a space then move is a capture so add "x"
        incheck = self.l_m.check_tpos_forcheck(squares_cont, place1, place2, whosemove)
        #print("this is from algtosan. incheck is ", incheck)
        if incheck:
            san5 = "+" 
        san = san1 + san2 + san3 + san4 + san5   #san1 first half of move san2 if takes san3 second half san4
                                                 # if promotion san5 if check first is first column when needed
        #print("san ",san,"  san2  ",san2)
        if alg1 == "e1" and spiece == "K": #check if white king move is a castle
            if alg2 == "g1":    #castle so chang SAN to short castle
                san = "0-0"
            if alg2 == "c1":    #long castle
                san = "0-0-0"
        if alg1 == "e8" and spiece == "k": #check if black king move is a castle
            if alg2 == "g8":    #castle so chang SAN to short castle
                san = "0-0"
            if alg2 == "c8":    #long castle
                san = "0-0-0" 
        p_at = ""                                             
        if u_spiece == "R" or u_spiece == "N" or u_spiece == "Q":      #add column/row if rook or knight or Queen move
            x = squares_cont.count(spiece)       
            if x > 1:       #if more than one of that piece on the board
                p_at = "-" + first + second
        san = san + p_at        
        return san
        
    def label_update(self, new_move):#, fen, moves, currmove):    #
    #temporary as most probably not neede
        san1 = ""
        sp = " "        
        currmove = self.gd.currentmove_get() 
        prevfen = self.gd.fenlist_get(currmove-2)       #get the last fen to display the correct move number
        #since the FEN always is 1/2 move ahead on move number 
        fen_list = prevfen.split(" ")                #splits the fen into a list of items that were separated by a space
        move = fen_list[5]                    #set move number from previous fen, mainly for display so string 
        fen_list = self.gd.fenlist_get(currmove-1).split(" ")                #splits the fen into a list of items that were separated by a space        
        if currmove < 16:           #update opening name if less than MOVE 8 16 halfmoves
            self.chessw.title(self.opening_name) 
            epd = fen_list[0] + sp + fen_list[1] + sp  + fen_list[2] + sp + "-"
            currtitle = self.opening.search_dict(epd)                
            if currtitle == "":
                if "(" not in self.opening_name:  
                    self.opening_name = "(" + self.opening_name + ")"        
            else: 
                self.opening_name = currtitle             
            self.chessw.title(self.opening_name)                         
        w_m = self.gd.whosemove_get()
        if w_m == "b":           #reversed here since currently NEXT move
            rdots = ""
            dots = "..."
        else:      
            rdots = "..." 
            dots = ""    
        lalg = self.gd.movelist_get(currmove-1)
        squares = self.gd.squares_get(currmove-2)
        nm_squares = self.gd.squares_get(currmove-1)
        if lalg != "init":
            san1 = self.algebra_to_san(lalg, squares)             
        lalg = rdots + lalg
        try:
            nm = self.gd.movelist_get(currmove)
            nm = self.algebra_to_san(nm, nm_squares)
            nm = dots + nm
        except:
            nm = dots + "  end" 
        if lalg == "...init":
            lalg = ""
            move = "1"  
        outstr = "Move " + move + sp + rdots + san1 + "   Next " + nm
        self.info_lbl['text'] = outstr  
        #since label get's updated every move regardless of how move occurs if analysis then do
        assist = self.assist.get()  
        if assist != 0 and new_move:         #if assistance is on AND a new_move then call assistant
            self.assist_lbl['bg'] = "red"          
            moves, scores = self.assistant()
            self.assist_lbl['bg'] = self.ls_color
            self.gd.bestmoves_append(moves)
            self.gd.bestscores_append(scores) 
        try:            #if there is already a list of bestmoves this will work
            moves = self.gd.bestmoves_get(currmove-1)
        except:             #if it fails add bestmoves that are "" so that bestmoves and bestscores always have an entry
            self.gd.bestmoves_append(["","",""])
            self.gd.bestscores_append(["","",""])                            
        moves = self.gd.bestmoves_get(currmove-1)
        scores = self.gd.bestscores_get(currmove-1)                               
        outstr = ""
        spl = "     "        
        counter = 0
        for i in moves:
            #print("assist")
            san1 = self.algebra_to_san(i, nm_squares)
            #print("san1 ",san1," counter ",counter)
            outstr = outstr + san1 + sp + scores[counter] + spl
            counter += 1
        #logging.info(outstr)
        self.cb.highlight_clear()
        self.show_next()        
        self.highlight_best(moves, scores)        
        self.assist_lbl['text'] = outstr 
        print("scores ",self.calc_score)
        if self.contwin:            #if this is a continue window    
            if self.orig_continu:             #no scores to display if new moves  
                outstr = "S " + str(self.calc_score[currmove])
                diff = float(self.calc_diff[currmove])            
            else:  
                outstr = "N"
                diff = 0
            self.s_lbl['text'] = outstr      
            # Apply your conditional formatting logic here
            if diff > 3.9:        #big blunder
                # Color of Label assigned a color name
                self.diff_lbl.config(bg="#a80747")
                #sheet.highlight_cells(row=row_idx, column=target_col, bg="#a80747", fg="black")                    
            elif diff > 1.8:       #medium blunder
                self.diff_lbl.config(bg="#e66eb2")
                #sheet.highlight_cells(row=row_idx, column=target_col, bg="#e66eb2", fg="black")                                   
            elif diff > .8:       #mild blunder
                #sheet.highlight_cells(row=row_idx, column=target_col, bg="#e8dd3c", fg="black")                 
                self.diff_lbl.config(bg="#e8dd3c")
            else:
                self.diff_lbl.config(bg="#e8dcc9")
            self.diff_lbl['text'] = diff      
            
    def assistant(self):        #use stockfish engine to get up to three best moves within x (.7) points  
        self.calculating = True    
        currmove = self.gd.currentmove_get() 
        fenstring = self.gd.fenlist_get(currmove-1)       #get the fen of the current position   
        #fenstring is fen 24 is depth 3 is multipv last is timeout in seconds  
        moves, scores, _ = self.engine.getmoves(fenstring, 24, 3, 20)  
        limit = 0         #limit list length to actual moves only keep moves, not "" as a move holder
        for i in moves:
            if i == "":
                break
            limit += 1
        l_len = len(moves)           #used when extra non moves and scores need to be popped off of list
        while limit < l_len:
            moves.pop()
            scores.pop()
            l_len -= 1
        outstr = "Assisted "
        for i in range(len(scores)):
            outstr = outstr + str(moves[i]) + "  " + str(scores[i]) + " "
        logging.info(outstr)   
        #processing any clicks of keypresses that occure DURING calculation
        self.chessw.update_idletasks()
        self.chessw.update()
        #This keeps keypresses and clicks to forward back or save from being executed immediately after calculating
        #If the above is not done then if you hit buttons during calculation they can queue up and drag system waiting for calculation after calculation
        self.calculating = False                                                
        return moves, scores        #print("Moves\n", moves, "Scores\n",scores)    
        
    def calc_move(self):                #called when button pressed for engine calculation
        if self.calculating:
            outstr = "Not calculating because calculation is in progress"
            logging.info(outstr)
            return          #calculation in progress so not performing click function 
        logging.info("Engine button pressed")   
        self.orig_continu = False             #when recalculation the original continuation is lost    
        sp = " "
        currmove = self.gd.currentmove_get()         
        nm_squares = self.gd.squares_get(currmove-1)     
        self.engine_assist_btn.config(state=tk.DISABLED)    
        spl = "     "
        self.assist_lbl['bg'] = "red"
        moves, scores = self.assistant()
        self.gd.bestmoves_pop(currmove-1)
        self.gd.bestmoves_insert(currmove-1, moves)   
        self.gd.bestscores_pop(currmove-1)
        self.gd.bestscores_insert(currmove-1, scores) 
        self.cb.highlight_clear()
        self.show_next()           
        self.highlight_best(moves, scores)             
        self.assist_lbl['bg'] = self.ls_color           
        outstr = ""
        counter = 0
        for i in moves:
            #print("assist")
            san1 = self.algebra_to_san(i, nm_squares)
            outstr = outstr + san1 + sp + scores[counter] + spl
            counter += 1
        #logging.info(outstr)
        self.assist_lbl['text'] = outstr
        self.engine_assist_btn.config(state=tk.NORMAL)  

    def show_next(self):
        #draw line of next move if there is one already
        currmove = self.gd.currentmove_get()  
        lalg = self.gd.movelist_get(currmove)  
        if len(lalg) > 3:       #if there is a NEXT move
            hlsquares = self.cb.get_move_squares(lalg)
            x0, y0 = self.cb.center_ofsquare(hlsquares[0])
            x1, y1 = self.cb.center_ofsquare(hlsquares[1])            
            self.cb.drawline(x0,y0,x1,y1)        #make a thick highlight that won't be completely covered by "best" 
                    
    def highlight_best(self, moves, scores):
        #remove any "" strings from moves or scores
        while "" in moves:    
            moves.pop(moves.index(""))
        while "" in scores:     
            scores.pop(scores.index(""))        
        if len(scores)<1:       #if no scores to highlight then leave
            return
        #only highlight moves that are within . 7 points
        if "mate" in scores[0]:             #get the bestscore to set as a baseline  if it is not a score then return as cannot highlight
            bestscore = 500
        else:
            try:
                bestscore = float(scores[0])
            except:
                return              #first "best" score is not usable
        #doing highlighting backwards so that the best move green will be highlighed on two squares even if same square as other
        #fc050d
        movecolor = ["#fc050d", "#ede621", "#62fc03"]    #orange b55b1b 3 yellow ede621 2 green 62fc03 1 reversed
        rmoves = moves[::-1]        #copy of the list in reverse so that it can be easily iterated backwards 
        rscores = scores[::-1]
        counter = 0
        for i in rmoves:
            if "mate" in rscores[counter]:
                movescore = 500
            else:
                #print(rscores[counter],"This is to be floated")
                movescore = float(rscores[counter])
            if abs(movescore - bestscore) < .71:
                hsquares = self.cb.get_move_squares(i)
                self.cb.highlight_squares(hsquares, movecolor[counter], 5)  
            counter += 1                        
        #print()                    
                 
class chessboard():
    def __init__(self, parent, root, bc, gd, l_m, colors):
        #self.p = p                                     #output for stockfish out
        self.root = root                            #root tkinter window
        self.parent = parent                            #link to (toplevel window) container of canvas (board)
        self.bc = bc                                #link to board control object giving access to it
        self.gd = gd                                #game data object
        self.l_m = l_m                       #link to instance of legalmoves class  
        self.white_on_bottom = True        #orientation of the board and square tag numbers    
        self.whitelist = []                         #lists to be displayed of capture advantage (if you have two bishops and opp has one)
        self.blacklist = []                         #list of pieces your opp does NOT have that you have
        self.ds_color = colors[0]           #color of canvas dark squares
        self.ls_color = colors[1]           #color of canvas light squares        

        self.csquares = []                          #squares of current board position
        self.cfen = ""                                 #fen of current board position  
        self.lcurrentmove = 1                    #lcurrentmove # (0 is init) white black moves or halfmoves made in this object         
        self.images = {}                          #Dictionary of piece images referenced by letter Q white queen q black queen
        self.blankboard = []                    #blank board of 0 to 63 just -
        for i in range(0,64):
            self.blankboard.append("-")      
        self.load_piece_templates()         #load the images of pieces for display on the board
        self.init_canvas()
        self.init_board()                           #initialize the chess board
    
    def init_canvas(self):              #create the canvas to display the board on    
        logging.info("Creating canvas") 
        #captured pieces canvas 
        capcanvas_width = 1 * 64
        capcanvas_height = 8 * 64
        self.capcanvas = tk.Canvas(self.parent, width=capcanvas_width, height=capcanvas_height)    
        self.capcanvas.pack(side = tk.LEFT, padx=8)#, pady=8)            
        #board canvas to show squares and pieces                      
        canvas_width = 8 * 64
        canvas_height = 8 * 64
        self.canvas = tk.Canvas(self.parent, width=canvas_width, height=canvas_height)    
        self.canvas.pack(side = tk.LEFT, padx=8)#, pady=8)            
        self.canvas.bind("<Button-1>", lambda event: self.pdragstart(event)) 
        self.canvas.bind("<B1-Motion>", lambda event: self.pdrag(event))
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.pdragstop(event))                                   

    def init_board(self):
        logging.info("Setting up pieces and both canvas")    
        def changecolor(color):
                if color == self.ls_color:
                    color = self.ds_color
                else:
                    color = self.ls_color
                return color 
        color = self.ls_color           
        counter = 0             # 0 to 32 for 32 squares of the capture canvas
        for row in range(16):
            for col in range(2):
                x1 = (col * 32)
                y1 = (row * 32)
                x2 = x1 + 32
                y2 = y1 + 32
                square = "b"+str(counter)   #semi permanent tag for the square only to be changed on board rotation
                self.capcanvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             width = 0,   
                                             tags= square)
                #print(square,"  ")                 squares are from top left to bottom right strings a0 to a63
                new_tag = "c"+str(counter)      #reference tag of the square
                self.capcanvas.addtag(new_tag, 'withtag', square)         #add a tag with the square number inverted               
                counter +=1                                        
        color = self.ls_color           
        counter = 0             # 0 to 63 for 64 squares of the board
        for row in range(8):
            for col in range(8):
                x1 = (col * 64)
                y1 = (row * 64)
                x2 = x1 + 64
                y2 = y1 + 64
                square = "a"+str(counter)           #semi permanent tag for the square only to be changed on board rotation
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                             width = 0,   
                                             tags= square)
                #print(square,"  ")                 squares are from top left to bottom right strings a0 to a63
                new_tag = "s"+str(counter)
                self.canvas.addtag(new_tag, 'withtag', square)         #add a tag with the square number inverted
                color = changecolor(color)       #change the square color to alternate colors
                counter +=1
            color = changecolor(color)       #change the square color to alternate colors for row alternation          
        self.csquares = self.gd.squares_get(0)
        self.cfen = self.gd.fenlist_get(0)
        self.update_bd(self.blankboard,self.csquares)              #original board had nothing on it so empty list of -            

    def rotate_board(self):     #invert square tags.  Normal WOB top left corner s0 to s63 Normal Black on bottom s63 to s0
        #delete pieces from the board so they can be replaced on canvas
        for x in range(64):
            squaretag = "z" + str(x)                    #this is the tag the piece on that square has if there is a piece there
            self.canvas.delete(squaretag)       #deletes the piece with that tag from the board          
        if self.white_on_bottom:
            dncount = 63             
            for x in range(64):
                tag = "a"+str(x)
                curr_tag = "s"+str(x)
                new_tag = "s"+str(dncount)                
                self.canvas.dtag(tag, curr_tag)                              #take away the original tag so only the new square order is there     
                self.canvas.addtag(new_tag, 'withtag', tag)         #add a tag with the square number inverted    
                dncount -= 1                                          
        else:
            upcount = 0 
            for x in range(63, -1, -1):
                tag = "a"+str(x)
                curr_tag = "s"+str(upcount)
                new_tag = "s"+str(x)                
                self.canvas.dtag(tag, curr_tag)                              #take away the original tag so only the new square order is there     
                self.canvas.addtag(new_tag, 'withtag', tag)         #add a tag with the square number inverted    
                upcount += 1         
        #delete pieces from the capture board so they can be replaced on capcanvas
        for x in range(32):   
            tag = "z" + str(x)
            self.capcanvas.delete(tag)       #deletes the piece with that tag from the capture canvas       
        if self.white_on_bottom:
            dncount = 31             
            for x in range(32):
                tag = "b"+str(x)
                curr_tag = "c"+str(x)
                new_tag = "c"+str(dncount)              
                self.capcanvas.dtag(tag, curr_tag)                              #take away the original tag so only the new square order is there     
                self.capcanvas.addtag(new_tag, 'withtag', tag)         #add a tag with the square number inverted    
                dncount -= 1                                          
            self.white_on_bottom = False
        else:
            upcount = 0 
            for x in range(31, -1, -1):
                tag = "b"+str(x)
                curr_tag = "c"+str(upcount)
                new_tag = "c"+str(x)                
                self.capcanvas.dtag(tag, curr_tag)                              #take away the original tag so only the new square order is there     
                self.capcanvas.addtag(new_tag, 'withtag', tag)         #add a tag with the square number inverted    
                upcount += 1         
            self.white_on_bottom = True            
        currmove = (self.gd.currentmove_get() -1) 
        self.csquares = self.gd.squares_get(currmove)                           
        self.update_bd(self.blankboard, self.csquares) 
        self.bc.label_update(new_move = False) 
        logging.info("Board rotated")        
                           
    def load_piece_templates(self):
        #load piece images from file into a dictionary reference letter to image stored.  Read on initialization
        filename = "pieces_image/"
        self.images["R"] = tk.PhotoImage(file=filename+"rwhite.png")    
        self.images["r"] = tk.PhotoImage(file=filename+"rblack.png")
        self.images["N"] = tk.PhotoImage(file=filename+"nwhite.png")
        self.images["n"] = tk.PhotoImage(file=filename+"nblack.png")
        self.images["B"] = tk.PhotoImage(file=filename+"bwhite.png")
        self.images["b"] = tk.PhotoImage(file=filename+"bblack.png")
        self.images["Q"] = tk.PhotoImage(file=filename+"qwhite.png")
        self.images["q"] = tk.PhotoImage(file=filename+"qblack.png")
        self.images["K"] = tk.PhotoImage(file=filename+"kwhite.png")
        self.images["k"] = tk.PhotoImage(file=filename+"kblack.png")
        self.images["P"] = tk.PhotoImage(file=filename+"pwhite.png")
        self.images["p"] = tk.PhotoImage(file=filename+"pblack.png") 
          
        self.images["Rc"] = tk.PhotoImage(file=filename+"rwcap.png")    
        self.images["rc"] = tk.PhotoImage(file=filename+"rbcap.png")
        self.images["Nc"] = tk.PhotoImage(file=filename+"nwcap.png")
        self.images["nc"] = tk.PhotoImage(file=filename+"nbcap.png")
        self.images["Bc"] = tk.PhotoImage(file=filename+"bwcap.png")
        self.images["bc"] = tk.PhotoImage(file=filename+"bbcap.png")
        self.images["Qc"] = tk.PhotoImage(file=filename+"qwcap.png")
        self.images["qc"] = tk.PhotoImage(file=filename+"qbcap.png")
        self.images["Pc"] = tk.PhotoImage(file=filename+"pwcap.png")
        self.images["pc"] = tk.PhotoImage(file=filename+"pbcap.png")           

    def compare_cap(self, allpieces, piece):
        upiece = piece.upper()
        x = allpieces.count(piece)         #get the number of pieces on the board
        y = allpieces.count(upiece)         #get the number of pieces on the board
        if x < y:           #if x is lower then white has more pawns so show number of white pawns
            for z in range(x,y):
                self.display_cap.append(upiece)
        if x > y:           #if x is larger then black has more pawns
            for z in range(y,x):
                self.display_cap.append(piece)     
        
    def calc_capture_display(self, currsquares):      #calculate piece advantage to display in capture canvas `
        self.display_cap = []               #list that will be displayed      
        self.compare_cap(currsquares, "p")     #calc and add pawn advantage
        self.compare_cap(currsquares, "q")     #calc and add queen advantage          
        self.compare_cap(currsquares, "r")     #calc and add rook advantage
        self.compare_cap(currsquares, "n")     #calc and add knight advantage
        self.compare_cap(currsquares, "b")     #calc and add bishop advantage
        #clear captured canvas of pieces
        for x in range(32):   
            tag = "z" + str(x)
            self.capcanvas.delete(tag)       #deletes the piece with that tag from the capture canvas
        #place the  self.display_cap list in the captured canvas 0 to 15 black 16 to 31 white 
        wpieces = 16               #starting squares  evens are for pieces 
        wpawns = 17               #odds are for pawns
        bpieces = 0
        bpawns = 1
        #logging.info(self.display_cap)
        for i in self.display_cap:
            if i.isupper():          #if piece to draw is white
                if i == "P":
                    squaretodraw = wpawns
                    wpawns +=2
                else:
                    squaretodraw = wpieces
                    wpieces += 2
            else:                       #if piece to draw is black
                if i == "p":
                    squaretodraw = bpawns
                    bpawns +=2
                else:
                    squaretodraw = bpieces
                    bpieces += 2                        
            squaretag = "z" + str(squaretodraw)                    #this is the tag the piece on that square has if there is a piece there
            piece = i + "c"
            self.draw_cappiece(piece, squaretodraw, squaretag)
        
    def draw_cappiece(self, piece, i, squaretag):      #piece , square number, tag
        #numbers are used in here to center the piece properly so ARE rotationally different
        x = int(i / 2)       #row from 0 to 31         #getting row and column from square number
        y = int(i % 2)       #column from 0 to 1
        #print("x ",x," Y ",y)
        self.capcanvas.create_image(0, 0, image=self.images[piece],
                                 tags=(squaretag),
                                 anchor="c")
        #self.white_on_bottom = True
        if not self.white_on_bottom:    #orientation == 1:    #Black on the bottom of board   
            x0 = ((15 - x) * 32) + (32 / 2)           
            y0 = ((1- y) * 32) + (32 / 2)
        else:   #White on the bottom of board
            x0 = (x * 32) + (32 / 2)          
            y0 = (y * 32) + (32 / 2)                            
        self.capcanvas.coords(squaretag, y0, x0)                                                       

    def get_col(self, cr):          #cr is half of a long algebra move. col a-h row 1-8  NO 0
        cols = ["none","a","b","c","d","e","f","g","h"]
        c = cr[:1]
        col = cols.index(c)     
        return col   #integers of column
        
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
        return alg                                                        
        
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
        move_squares = []                           #square numbers from algebra  a8 is square 0 no matter the rotation of board
        orig = lalg[:2]
        origsqr = self.get_square_from_alg(orig)
        move_squares.append(origsqr)        
        dest = lalg[2:4]
        destsqr = self.get_square_from_alg(dest)        
        move_squares.append(destsqr)  
        return move_squares         #list of squares start of move square and move to square

    def highlight_clear(self):
        self.canvas.itemconfigure("highlight", width = 0)    #remove all highlights
        self.canvas.dtag("highlight","highlight") 
        try:
            self.canvas.delete(self.line_1)
        except:
            pass
                
    def highlight_squares(self, squares, color, thick = 3):
        for i in squares:
            hsquare = "s" + str((i))
            self.canvas.itemconfigure(hsquare,outline=color, width = thick)
            self.canvas.addtag_withtag("highlight",hsquare)    

    def drawline(self, x0, y0, x1, y1):
        self.line_1 = self.canvas.create_line(x0, y0, x1, y1, fill='white', width=3, arrow=tk.LAST)

    def center_ofsquare(self, square):
        y = int(square / 8)       #row from 0 to 7
        x = int(square % 8)       #column from 0 to 7    
        if not self.white_on_bottom:    #orientation == 1:    #Black on the bottom of board   
            x0 = ((7 - x) * 64) + (64 / 2)           
            y0 = ((7- y) * 64) + (64 / 2)
        else:   #White on the bottom of board
            x0 = (x * 64) + (64 / 2)          
            y0 = (y * 64) + (64 / 2)    
        return x0, y0        
     
    def squares_to_fenfront (self, sqrs):
        #takes the squares (0 to 63 piece positions) and makes the positional left side of FEN and returns it  even if rotated  
        fen = ""
        spacecount=0
        for row in range (0, 64, 8):  #read 8 rows
            for x in range (row, row + 8):     #read squares list one row one at a time and place in fen
                if sqrs [x] == "-":       #if a space update space counter
                    spacecount = spacecount + 1
                else:               # if a piece is at this location
                    if spacecount == 0:
                        fen = fen + sqrs[x]
                    else:
                        fen = fen + str(spacecount) #put in number of spaces
                        fen = fen + sqrs [x]     #put in piece position
                        spacecount = 0
            if spacecount > 0:  #last position of row is space handle it
                fen = fen + str(spacecount) #put in number of spaces
                spacecount = 0
            if x < 63:  #add forward slash if not last row add space if it is
                fen = fen + "/"
            else:
                fen = fen + " "  #space added to mark end of field
        #this creates the left side (Position) of fen                         
        return fen  
    
    def fen_to_squares(self):    #set up squares list to represent chess board        
        squares = []     #squares 0 is ALWAYS black rook home position squares 63 is last white rook position  even if rotated this stays true
        lfen, _, _ = self.fen.partition(" ")      
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
        return squares
    # end of fen to squares          

    def draw_piece(self, piece, i, squaretag):      #piece , square number, tag
        #numbers are used in here to center the piece properly so ARE rotationally different
        x0, y0 = self.center_ofsquare(i)
        self.canvas.create_image(0, 0, image=self.images[piece],
                                 tags=(squaretag),
                                 anchor="c")           
        self.canvas.coords(squaretag, x0, y0)
    
    def update_bd(self, lsquares, currsquares):
        #compare lastsquares (lsquares can be last move or next move or empty if no moves have been made)
        #   to currsquares and only update squares that are different on the canvas
        changed = []
        for i in range(0,64):
            if lsquares[i] != currsquares[i]:       #get list of squares that are different from last move
                changed.append(i) 
        #print(changed)
        numchanged = len(changed)
        for i in changed:              #go through list of changed squares and update as needed         
            squaretag = "z" + str(i)                    #this is the tag the piece on that square has if there is a piece there
            if lsquares[i] != "-":                          #if a piece was on the square last move remove it as there is a new piece or a space there now
                self.canvas.delete(squaretag)       #deletes the piece with that tag from the board
            if currsquares[i] != "-":                       #if the new square designation is not a space
                self.draw_piece(currsquares[i], i, squaretag)
        self.calc_capture_display(currsquares)  #send the updated squares to the capture advantage

    def newsquares(self, cursquares, lalg, castled):  
        #copy current squares and change based on algmove and enpassant rules
        en_pass = False             #not en passant
        capture = False
        pawnmove = False
        first = lalg[0]      #first char of lalg column  
        third = lalg[2]      #third char of lalg is first of second half of move column
        fourth = (lalg[3])  #fourth char (row)
        alg2 = lalg[2:4]     #second half of move (ex. e4)
        col2 = self.get_col(alg2)       #needed for en passant column if en passant move                    
        fromto = self.get_move_squares(lalg)
        place1 = fromto[0]
        place2 = fromto[1]                              
        newsquares = copy.deepcopy(cursquares)        
        piecemoved = newsquares[place1]    #piece at moved from square 
        tospotpiece = newsquares[place2]    #piece at object square or if it is a space - (could be space - or piece)
        if tospotpiece != "-":
            capture = True
            self.gd.captured_add(tospotpiece)         #add to list of captured pieces
            outstr = tospotpiece + " Captured"
            logging.info(outstr)
        newsquares.pop(place1)     #remove piece
        newsquares.insert(place1, "-") #replace with - for space
        promotion = self.gd.promotion_get()
        if promotion:              #if move resulted in a promotion (tested in pdragstop)
            try:
                piecemoved = lalg[4]     #there should be a fifth character if promotion 
            except:
                logging.error("There should be a fifth letter on a promotion, none was found")
        newsquares.pop(place2)
        newsquares.insert(place2, piecemoved)
        if castled:                 #if a castle was performed then move rook
            if place2 == 62:        #white short castle
                newsquares.pop(63)          #remove rook
                newsquares.insert(63, "-")  #replace with a -
                newsquares.pop(61)          #remove the - at 61
                newsquares.insert(61, "R")  #replace with a rook
            if place2 == 58:        #long white castle
                newsquares.pop(56)
                newsquares.insert(56, "-")  #replace with a -
                newsquares.pop(59)          #remove the -                                
                newsquares.insert(59, "R")            
            if place2 == 6:         #black short castle
                newsquares.pop(7)
                newsquares.insert(7, "-")  #replace with a -
                newsquares.pop(5)          #remove the -                     
                newsquares.insert(5, "r")            
            if place2 == 2:         #black long castle
                newsquares.pop(0)
                newsquares.insert(0, "-")  #replace with a -
                newsquares.pop(3)          #remove the -                     
                newsquares.insert(3, "r")                     
        #test if is an en passant capture
        u_piece = piecemoved.upper()   #uppercase piece letter   
        if u_piece == "P":          #if a pawn see if column matches as pawn only changes column on a capture 
            pawnmove = True             
            if first != third:          #if not equal then a capture so check further
                if tospotpiece == "-":              #if a dash then no piece was on that square so it IS EN PASSANT CAPTURE
                    en_pass = True
                    logging.info("En Passant Capture")
        if en_pass:                     #if an en passant move remove pawn captured that is not on the to square as en passant
            if int(fourth) > 4:              #greater than 4 then move is capuring black pawn on col row 5
                row3 = 3         #en passant row of pawn captured always the same even rotated - 2 for math
            else:
                row3 = 4
            #row3 is lower because chess uses rows 1 - 8 and column 1 - 8 yet the squares start a 0 as the FEN does too.  Pain
            place3 = (row3 * 8) + col2 - 1  #calculate position in squares list of captured pawn based on which column en passant occurred
            outstr = alg2 + " enpassant captured from row col " + str(row3) + " " + str(col2) +"  " + str(place3)
            logging.info(outstr)            
            x =  newsquares[place3]         #place piece was captured at
            self.gd.captured_add(x)         #add to list of captured pieces
            outstr = x + " Captured"
            logging.info(outstr)            
            newsquares.pop(place3)     #remove pawn on en passant capture square
            newsquares.insert(place3, "-") #replace with - for space 
        if pawnmove or capture:             #reset string halfmove counter (50 move)
            self.gd.pawnorcapture_reset()               #set to 0 as pawn move or capture
        else:
            self.gd.pawnorcapture_increment()         #increment counter  
        #self.l_m.display_squares(newsquares)    
        return newsquares
#                  
    def new_move_update(self, fullalg, castled):# Make a new FEN and update variables based on move
        #truncate if needed and update movelist  Needed if new move is earlier in movelist so continuation is void 
        #also truncate fenlist and squares as the ones after this move no longer exist
        self.gd.truncate_lists(self.lcurrentmove)
        #make a new squares list to add to squares reflecting new move
        newsquares = self.newsquares(self.csquares, fullalg, castled)                                       
        self.update_bd(self.csquares, newsquares)
        lfen = self.squares_to_fenfront (newsquares)            
        mn = self.gd.fenmove_get()      
        outstr = "New move made. Fenmove is " + mn        
        w_m = self.gd.whosemove_get()
        if w_m == "b":          #if black moved then increment movenum (fenmove)
            self.gd.fenmove_increment()
        self.gd.whosemove_toggle()      #set other side to move at next move for new FEN    
        w_m = self.gd.whosemove_get()               
        logging.info(outstr)                     
        self.lcurrentmove += 1                   #add a halfmove to keep lcurrentmove accurate 
        self.gd.currentmove_increment()
        sp = " " 
        poc = str(self.gd.pawnorcapture_get())
        mn = self.gd.fenmove_get()
        castle = self.gd.castle_get()
        passant = self.gd.passant_get()
        self.cfen = lfen + w_m + sp + castle + sp + passant +  sp + poc + sp + mn 
        #add new move to movelist    
        self.gd.movelist_append(fullalg)
        self.gd.totalmoves_set(len(self.gd.movelist)-1)     #-1 because move 0 is "init"      
        self.gd.fenlist_append(self.cfen)  
        self.gd.squares_append(newsquares)      
        #update board control object that a new move was made
        new_move = True
        self.bc.orig_continu = False
        self.bc.label_update(new_move)#True for forward direction
        outstr = "New Fen " + self.cfen
        logging.info(outstr) 
        game_over, status = self.l_m.is_there_move(self.cfen) 
        if game_over:
            self.chessw.attributes('-topmost', False)
            outstr = "Game is over!  Result is " + status
            messagebox.showinfo("Game Over", outstr)
            self.chessw.attributes('-topmost', True)  
            self.chessw.update()              
            logging.info(outstr)                             
         
    def pdragstart(self, event):
        #select piece in that square and highlight squares that are legitimate moves
        self.lcurrentmove = self.gd.currentmove_get()
        self.csquares = self.gd.squares_get(self.lcurrentmove-1)    #need position before move so -1
        self.cfen = self.gd.fenlist_get(self.lcurrentmove-1)          
        self.gd.parse_fen(self.cfen)        #updates fen move to current move  
        self.xc, self.yc = event.x, event.y         #used in other drags   
        self.cc1 = int(event.x /64)*64+31
        self.cr1 = int(event.y /64)*64+31    
        #print ("cc1 ", self.cc1, " cr1 ", self.cr1)
        self.canvas.itemconfigure("highlight", width = 0)
        self.canvas.dtag("highlight","highlight")  
        item = self.canvas.find_closest(event.x, event.y)
        alltags = self.canvas.gettags(item)
        self.tag = ""
        for i in alltags:
            if "z" in i:
                self.tag = i
        #get squares column and row (ex. e3) from self.tag to highlight and check possible moves and legal move later
        if self.tag:
            sqr = self.tag[1:]       #drop off the z to get square from the piece tag
            self.spos= int(sqr)
            self.pname = self.csquares[self.spos]
            w_m = self.gd.whosemove_get()
            #print (self.tag, "tags ", self.pname)
            if self.pname.isupper() and w_m == "w" or self.pname.islower() and w_m == "b":
                #use square number (pos) to get row and column of square
                #row, col, colletter = self.getrow_column_ofsquare(self.spos) 
                self.alg_1 = self.get_alg_from_square(self.spos)               
                #self.alg_1 = colletter + str(row)  #two letter algebra move of piece 
                #print("r ",row, " c ",col,"  alg", self.alg_1)
                self.hsquare = "s" + sqr
                self.canvas.itemconfigure(self.hsquare,outline="white", width = 3)
                self.canvas.addtag_withtag("highlight",self.hsquare) 
                #print("last one ",newfen)
                _, _, mlist = self.l_m.legal_move(self.cfen, self.alg_1)
                for i in mlist:
                    hsquare = "s" + str((i))
                    self.canvas.itemconfigure(hsquare,outline="white", width = 3)
                    self.canvas.addtag_withtag("highlight",hsquare)               
            else:
                self.tag = ""  
        return                
                
    def pdrag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self.xc
        delta_y = event.y - self.yc    
        self.canvas.move(self.tag, delta_x, delta_y)
        self.xc = event.x
        self.yc = event.y 
        return  
        
    def pdragstop(self, event):
        cols = ["none","a","b","c","d","e","f","g","h"]
        col = 0
        row = 0
        newmove1 = False   
        cc2 = int(event.x /64)*64+31        #position of nearest center row col
        cr2 = int(event.y /64)*64+31                
        self.canvas.itemconfigure("highlight", width = 0)    #remove all highlights
        self.canvas.dtag("highlight","highlight") 
        if self.tag:         #if there is a tag then a piece of the right color was selected in dragstart
            self.cfen = self.gd.fenlist_get(self.lcurrentmove-1)            
            self.canvas.coords(self.tag, cc2, cr2)    #center tagged piece in the nearsest square to drop point
            #find out what row and column that piece was dropped in from canvas coordinates.  Board rotation matters
            if self.white_on_bottom:
                col = int((cc2 + 33)/64)     #column number
                row = int(9-((cr2 + 33)/64))     #row number 
            else:       #black on the bottom
                col = int(9-((cc2 + 33)/64))     #column number
                row = int((cr2 + 33)/64)     #row number             
            if col not in range(1,9):            #dropping piece off canvase or someplace weird
                col = 0      #set col to 0 so that column will be s and legal move will catch it    
            if row not in range(1,9):
                col = 0      #set col to 0 so that column will be s and legal move will catch it 
            if col != 0:        #the drag stop was on a valid square
                colletter = cols[col]
                alg_2 = colletter + str(row)  #two letter second part of algebra move of piece
                fullalg = self.alg_1 + alg_2    
                fromto = self.get_move_squares(fullalg)                                        
                self.tpos = fromto[1]
                hsquare2 = "s" + str(self.tpos)                                   
                legal, reason, _ = self.l_m.legal_move(self.cfen, fullalg)
                #print("is move legal? ",legal,"move ", move,reason)
            else:
                legal = False
                reason = "piece dropped off of board"
                logging.error(reason)
                fullalg = self.alg_1 + "i0" 
            if not legal:           #put piece back in original position      
                self.canvas.coords(self.tag, self.cc1, self.cr1)    #center tagged piece at origin 
                message = "Not legal manual move attempted " + fullalg
                logging.info(message) 
                logging.info(reason)                                   
            else:                   #if move was legal
                self.gd.promotion_false()
                promotion = self.gd.promotion_get()
                self.gd.passant_set("-")
                passant = self.gd.passant_get()
                castled = False
                message = "Manual move " + fullalg
                logging.info(message)                
               #promotion needs to be checked here as if they promote to a different piece would be a new move
               #self.passant needs to be updated if white pawn moved to row 4 or black to row 5 as passant available
                srow = self.alg_1[1]      #get original move start row which is second place of self.alg1       
                if self.pname == "p":
                    if row == 1: promotion = True  #pawn to row 8 or 1 is promotion
                    if row == 5 and srow == "7": passant = colletter + "6"     #passant available on next move
                if self.pname == "P":
                    if row == 8: promotion = True                   
                    if row == 4 and srow == "2": passant = colletter + "3"     #passant available on next move  
                self.gd.passant_set(passant)                            
                #if promotion change fullalg to reflect it             
                if promotion:                      #only happens if pawn move was to enemy home row
                    self.gd.promotion_true()
                    promoted_to = promo(self.root)          #call window to get promoted piece
                    outstr = "Piece promoted to " + promoted_to
                    logging.info(outstr)
                    if self.pname.isupper():     #promote
                        fullalg = fullalg + promoted_to.upper()
                    else:
                        fullalg = fullalg + promoted_to                        
                if self.lcurrentmove > self.gd.totalmoves_get():                #must be new move if curr > total
                    newmove1 = True
                else:
                    try:
                        cmove = self.gd.movelist_get(self.lcurrentmove)  #if self.lcurrentmove is out of range
                    except:
                        print("cmove index out of range")
                        cmove = ""                  #set to null ass there was no existing lcurrentmove  
                    if cmove == fullalg:        #if manual move and list move align then not new move 
                        newmove1 = False
                    else:
                        newmove1 = True
                if not newmove1:                                #not a new move
                    #logging.info("not new move")        #so just increment self.lcurrentmove
                    #and send squareslast and squares current to update board.  no need to change squares or movelist as move already done
                     #do step forward like if button was pressed or right arrow was pressed  
                    self.bc.step_forward()                                  
                else:                                       #move is a new move
                    #logging.info("new move")  #done in new move update?
                    #highlight to and from squares
                    self.canvas.itemconfigure(self.hsquare,outline="white", width = 3)
                    self.canvas.addtag_withtag("highlight",self.hsquare) 
                    self.canvas.itemconfigure(hsquare2,outline="white", width = 3)
                    self.canvas.addtag_withtag("highlight",hsquare2)
                    w_m = self.gd.whosemove_get()
                    is_checked = self.l_m.check_tpos_forcheck(self.csquares, self.spos, self.tpos, w_m)
                    #is_checked = is_king_incheck(self.spos, self.tpos, self.csquares, w_m)
                    if is_checked:
                        self.gd.checked_true()
                        logging.info("King is checked")
                    if self.gd.castle_get() != "-":   #check if castling matters first and do nothing if no castling available  
                        scol = cols.index(self.alg_1[0])  #get original column by integer
                        numcolsmoved = abs(col - scol)       #used to determine if king moves more than one column meaning castle 
                        upiece = self.pname.upper()     #make piece uppercase for easier checking for king or rook
                        if upiece == "K" and numcolsmoved > 1:               #piece moved was a king and more than 1                                        
                            self.do_castling()
                            castled = True
                        if upiece == "K" or upiece == "R":      #if king or rook move affects castling
                            self.check_castling(scol)       #scol is the origination column number
                    self.new_move_update(fullalg, castled)      #update variables and board with new move  (squares and fenlist and fen ...)                              
        return               

    def do_castling(self):
        castle = self.gd.castle_get()
        if self.pname.isupper():        #white king has been moved    
            if "Q" in castle: castle = castle.replace("Q", "")
            if "K" in castle: castle = castle.replace("K", "")
        else:                       #black king was moved            
            if "q" in castle: castle = castle.replace("q", "")
            if "k" in castle: castle = castle.replace("k", "")
        self.gd.castle_set(castle) 
            
    def check_castling(self, scol):           #check movements and update castling to reflect move scol original column int
        castle = self.gd.castle_get()
        if self.pname.isupper():        #white piece has been moved
            if self.pname == "K":       #remove all castling for white
                if "Q" in castle: castle = castle.replace("Q", "")
                if "K" in castle: castle = castle.replace("K", "")
            if self.pname == "R":       #white rook was moved
                if scol == 1:    #queens rook so change queenside for white if it was available
                    if "Q" in castle:
                        castle = castle.replace("Q", "") #if castling to that side was good then change it so that it is not any more
                if scol == 8:    #kings rook so change kingside for white if it was available
                    if "K" in castle:
                        castle = castle.replace("K", "")                               
        else:                       #piece moved is black                      
            if self.pname == "k":       #remove all castling for black
                if "q" in castle: castle = castle.replace("q", "")
                if "k" in castle: castle = castle.replace("k", "") 
            if self.pname == "r":       #white rook was moved
                if scol == 1:    #queens rook so change queenside for white if it was available
                    if "q" in castle:
                        castle = castle.replace("q", "") #if castling to that side was good then change it so that it is not any more
                if scol == 8:    #kings rook so change kingside for white if it was available
                    if "k" in castle:
                        castle = castle.replace("k", "")                                                    
        if castle == "": castle = "-"         #castle can never be a null ""            
        self.gd.castle_set(castle)
        
############################################################################       
class game_data():
    
    def __init__ (self, starting_fen = "default"):
        self.squares = []       #list of lists, each sublist is 0 to 63 square string values for each piece and position of every move
        self.movelist = []                         #list of moves in games so far full algebra
        self.bestmoves = []                          #list of lists containing three best moves (full alg) so far, will be "" "" "" for not analyzed
        self.bestscores = []                    #list of lists containing three bes scores
        self.san_moves = []                     #list of moves in games so far short algebra
        self.fenlist = [] #list of lists, each sublist is string FEN of each move         
        if starting_fen == "default":           #self.fen is always current board FEN
            self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"    #fen with white at bottom of board
        else:
            self.fen = starting_fen   
        #self.initialmoves = 0  # starting number of initializing FEN in halfmoves so that you can not go before it     
        self.fenmove = "1"                        #current move number of NEXT move to be made in FEN really for display mainly as game is clocked by halfmoves
        self.white_p = "WNN"                    #player names
        self.black_p = "BNN"
        self.currentmove = 1                    #currentmove (0 is init) white black moves or halfmoves made in this object 
        self.totalmoves = 0                      #total number of moves that have been recorded in halfmoves           
        self.whosesmove = "w"                #w if whitesmove b if blacksmove
        self.castle = ""                          #string representing castling "KQkq"
        self.is_checked = False             #is king in check
        self.passant = "-"                          #If en passant was trigered on last move
        self.pawnorcapture = 0                 #number of halfmoves since pawn advance or capture used for 50 move rule (100 halfmoves) 
        self.promotion = False                  #if promotion is happening      
        self.captured_pieces = []             #string of captured pieces caps for white lower for black KQBBNNRRPkqbbnnrrp        
        self.parse_fen(self.fen)                #set variables from fen
        self.initialize_lists()                     #set initial fen, squares, move, sanmove (moves to keep list lengths =)

    def parse_fen(self, fen): 
        #separate the fen to get board position whosemove castle enpassant moves since capture or pawn and fenmoveber and halfmoves
        fen_list = fen.split(" ")                #splits the fen into a list of items that were separated by a space
        if len(fen_list) != 6:
            logging.error("Bad FEN so changing to default.  Fen must have six parts")
            outstr = "FEN " + self.fen
            logging.error(outstr)   #default fen with white at bottom of board
            self.fen_set("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")    
            fen_list = self.fen.split(" ")         #splits the fen into a list of items that were separated by a space
        lfen = fen_list[0]                            #first split is position "rnbqk..."
        self.whosemove_set(fen_list[1])      #set color to move whosemove and the rest
        self.castle_set(fen_list[2])               #set castle string "KQkq"   
        self.passant_set(fen_list[3])               #set en passant square if exists 
        self.pawnorcapture_set(int(fen_list[4]))        #set halfmoves since pawn move or capture
        #print("fenlist -- ",fen_list[5])
        self.fenmove_set(fen_list[5])                    #set fenmove number , mainly for display so string

    def initialize_lists(self):
        self.movelist_append("init")        #movelist 0 is init to keep = with fen and squares
        self.bestmoves_append(["","",""])
        self.bestscores_append(["","",""])
        self.san_moves_append("init")       #san_moves 0 is init to keep = with fen and squares        
        origsquares = self.fen_to_squares(self.fen)
        self.squares_append(origsquares)        #initial squares (0 to 63 piece positions) original squares from orig FEN
        self.fenlist_append(self.fen)           #initial FEN to original
        
    def truncate_lists(self, limit):            #truncate all lists to limit, never less than 1 as 0 is initial position
        if limit < 1: limit = 1
        self.squares_truncate(limit)
        self.movelist_truncate(limit)
        self.bestmoves_truncate(limit)
        self.bestscores_truncate(limit)        
        #self.san_moves_truncate(limit)
        self.fenlist_truncate(limit)        

    def squares_append(self, squares):
        self.squares.append(squares)
        
    def squares_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.squares)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.squares.pop()
            l_len -= 1
        
    def squares_get(self, index):
        squares = self.squares[index]
        return squares

    def movelist_append(self, move):
        self.movelist.append(move)
        
    def movelist_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.movelist)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.movelist.pop()
            l_len -= 1
            
    def movelist_get(self, index):
        try:
            move = self.movelist[index]
        except:
            return ""
        return move

    def bestmoves_append(self, moves):  #moves is a list of THREE best moves in order. correct if not three
        l_len = len(moves)                  # get length and make SURE three
        while l_len < 3:
            moves.append("")
            l_len += 1
        while l_len > 3:
            moves.pop()
            l_len -= 1
        self.bestmoves.append(moves)
        
    def bestmoves_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.bestmoves)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.bestmoves.pop()
            l_len -= 1
            
    def bestmoves_get(self, index):
        moves = self.bestmoves[index]
        return moves

    def bestscores_append(self, scores):  #scores is a list of THREE best move scores in order. correct if not three
        l_len = len(scores)                  # get length and make SURE three
        while l_len < 3:
            scores.append("")
            l_len += 1
        while l_len > 3:
            scores.pop()
            l_len -= 1
        self.bestscores.append(scores)
        
    def bestmoves_pop(self, index):
        self.bestmoves.pop(index)
    
    def bestmoves_insert(self, index, moves):
        self.bestmoves.insert(index, moves)

    def bestscores_pop(self, index):
        self.bestscores.pop(index)
    
    def bestscores_insert(self, index, moves):
        self.bestscores.insert(index, moves)
                
    def bestscores_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.bestscores)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.bestscores.pop()
            l_len -= 1
            
    def bestscores_get(self, index):
        scores = self.bestscores[index]
        return scores

    def san_moves_append(self, san):
        self.san_moves.append(san)
        
    def san_moves_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.san_moves)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.san_moves.pop()
            l_len -= 1
            
    def san_moves_get(self, index):
        fen = self.san_moves[index]
        return san

    def fenlist_append(self, fen):
        self.fenlist.append(fen)
        
    def fenlist_truncate(self, limit):        #remove members in list greater than limit 
        if limit < 1: limit = 1
        l_len = len(self.fenlist)           #used when a new move makes lists after move disposable
        while limit < l_len:
            self.fenlist.pop()
            l_len -= 1
            
    def fenlist_get(self, index):
        fen = self.fenlist[index]
        return fen

    def fenmove_increment (self):
        x = int(self.fenmove)
        x += 1
        self.fenmove = str(x)
        
    def fenmove_decrement (self):
        x = int(self.fenmove)
        x -= 1
        if x == 0: x = 1
        self.fenmove = str(x)
        
    def fenmove_set (self, strnumber):
        self.fenmove = strnumber 
        
    def fenmove_get(self):
        return self.fenmove   

    def currentmove_increment (self):
        self.currentmove += 1
    
    def currentmove_decrement (self):
        self.currentmove -= 1
        
    def currentmove_set (self, number):
        self.currentmove = number 
        
    def currentmove_get(self):
        return self.currentmove   

    def totalmoves_increment (self):
        self.totalmoves +=1
        
    def totalmoves_decrement (self):
        self.totalmoves -= 1
        
    def totalmoves_set (self, number):
        self.totalmoves = number
        
    def totalmoves_get(self):
        return self.totalmoves

    def whosemove_toggle (self):
        if self.whosemove == "w": #each step back toggle whosemove
            self.whosemove_set("b")      
        else:
            self.whosemove_set("w")  
            
    def whosemove_set (self, who):
        self.whosemove = who 
        
    def whosemove_get(self):
        return self.whosemove      

    def castle_set (self, newcastle):
        self.castle = newcastle
        
    def castle_get(self):
        return self.castle

    def checked_false(self):
        self.is_checked = False
        
    def checked_true(self):
        self.is_checked = True
        
    def checked_get(self):
        return self.is_checked

    def passant_set (self, passant_string):
        self.passant = passant_string
        
    def passant_get(self):
        return self.passant

    def pawnorcapture_reset (self):     #reset 50 move count
        self.pawnorcapture = 0
        
    def pawnorcapture_increment (self):     #increment 50 move count of no pawn move or capture
        self.pawnorcapture +=1
        
    def pawnorcapture_set (self, number):
        self.pawnorcapture = (number)
        
    def pawnorcapture_get(self):
        return self.pawnorcapture

    def promotion_false(self):
        self.promotion = False
        
    def promotion_true(self):
        self.promotion = True
        
    def promotion_get(self):
        return self.promotion

    def captured_add (self, piece):
        self.captured_pieces.append(piece)      #adds piece letter to the captured pieces list
        
    def captured_delete (self, piece):
        try:
            i = self.captured_pieces.index(piece)       #removes piece from captured pieces list if it is there
        except Exception as e:
            outstr = "Piece not in captured pieces  Exception " + str(type(e))
            logging.error(outstr)
            return         
        self.captured_pieces.pop(i)
            
    def captured_get(self):
        return self.captured_pieces

    def fen_to_squares(self, fen):    #set up squares list to represent chess board        
        squares = []     #squares 0 is ALWAYS black rook home position squares 63 is last white rook position  
        lfen, _, _ = fen.partition(" ")      
        for letter in lfen:       #go through the fen and fill squares with piece letter or s for space
            if letter == "/":           # FEN separator / does not go in squares
                pass
            elif letter.isdecimal():    #if a number, put that many "-" spaces in squares list using dash as not upper or lower since check uses case?
                x = int(letter)
                for y in range (x):
                    squares.append("-")
            else:                       #if not a number or a separator then is a piece letter so put in appropriate square
                squares.append(letter)  #draw_piece will remove and re add piece here to work witt drawpiece for all calls              
        return squares
    # end of fen to squares 


class open_find():

    def __init__(self, tsv_file):
        self.tsv_file = tsv_file                #filename of tab separated values dictionary file of openings from creative commons
                                                         # (https://creativecommons.org/publicdomain/zero/1.0/)
        self.open_dict = dict()               #name of the dictionary that will be loaded into memory
        self.read_dict()

    def read_dict(self):     #if disctionary file exists open and read return dictionary or None
        """ layout of tsv file from creative commons
            for row in reader:
                eco = row['eco']
                name = row['name']
                pgn = row['pgn']
                uci = row['uci']
                epd = row['epd']
        """
        m_dict = dict()         #create local dictinary
        if os.path.exists(self.tsv_file):        #make sure path to dictionary file exists
            if os.path.isfile(self.tsv_file):    #make sure it's a file
                with open(self.tsv_file, newline='') as efile:   #open the dictfile newline needed for windows and doesn't matter #for linux
                    ereader = csv.reader(efile, delimiter='\t')     #create a reader object for csv file reading
                    edata = list(ereader)           #read a chunk of it into local edata csv object
                for line in edata:          #go through all of the lines               
                    key = line[4]           #epd is fen without move number or EPD  FEN including to en passant but no more
                    if key in self.open_dict:       #if key in dict then a duplicate so don't write it (shouldn't happen)
                        # implement your duplicate line handling here
                        pass
                    #lyric = line[1].encode()    #local lyric value is dictionary value
                    #s = zlib.compress(lyric, -1)    #use zlib to compress value.  Long strings take space in 
                                                    #dictionary that is held in memory.  Compressed allows bigger
                                                    #dictionary to be used before memory problems.  only values are 
                                                    #compressed, but file will be kept uncompressed as disk space is
                                                    #not a problem and reading csv and uncompressing difficult as
                                                    #csv read returns a string and compression wants it in bytes value
                    self.open_dict[key] = line[1]     #assign value to key  Name of opening
                efile.close ()    #close file
                return self.open_dict   #return local m_dict if from read file
        return self.open_dict  #no file found so return empty dictionary m_dict   

    def search_dict(self, open_key): #check my_dict for song @ artist key and return lyrics and boolian if found
        
        in_dict = False     #local variable for set to not in dictionary
        opening_str = ""     #local string initialized to null
        val = self.open_dict.get(open_key, "")  #look in dict for key, if not found return ""
        #this can be used for compression to make a smaller dictionary in memory, may use later if needed
        """
        if val != "":       # if dictionary returned a value
            in_dict = True          #set indict to found in dictionary
            #b = bytes(lyr)          #change string (that has encoding from earlier) to a bytes value
            #q = zlib.decompress(b).decode() #decompress value and decode
            #lyrics_str = q      #string value of lyrics to return
            return val
        """
        return val


if __name__ == "__main__":
    #setup_safe_logging()
    # Now, multiple processes can safely write to 'app_safe.log'

    logging.info("************************Restarted**************************************************")
    window = tk.Tk()
    chessgame = board_control(window)#chessboard(window)           #create object chessboard for play or pgn entry    
    window.mainloop()        
