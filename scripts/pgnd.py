#! /usr/bin/env python3
#from tkinter import ttk
from tkinter import messagebox
import os
#import subprocess
#import time
#from datetime import datetime
import libs.chess as chess
import libs.chess.pgn
import logging

##############################################################################################
"""
    Chess Study Assistant scripts to create a graphic chess analysis program using Stockfish as an engine
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
class pgn_game_delete():
    #class to delete a game from a pgn file by it's offset
    #send pgn file name and the offset of the game to be deleted
    #opend the pgn file and writes all of the games NOT at that offset to a new file
    #then renames that new file to the pgn file name after succesfull write by deleting original and renaming
        #could eaisily be modified to delete a list of games from a pgn file by sending a list of offsets to not be copied
    
    def __init__(self, pgnfile, offset):
        self.pgnfile = pgnfile          #name of the pgn file to be modified
        self.offset = offset                #offset of game to be NOT copied
        self.gameslist = []             #list of the games in pgn file that does NOT include offset game
        self.modified = False           #has modified file been written
        self.offset_found = False       #was there a game at the offset sent
        self.pgn_mod()
        
    def pgn_mod(self):
        stroffset = str(self.offset)
        outstr = "Opening pgn to delete a game " + self.pgnfile + " " +stroffset
        logging.info(outstr)
        #print(outstr)
        try:
            with open(self.pgnfile, "r")as pgn:     
                offset = pgn.tell()                                
                while True:
                    game = chess.pgn.read_game(pgn)   
                    #print(offset)   
                    if game is None:
                        break                         
                    if offset != self.offset:
                        self.gameslist.append(game)         #gameslist holds all games that are not started at that offset
                    else:
                        outstr = "Game at offset " + stroffset + " not copied to modified file"
                        logging.info(outstr)
                        #print(outstr)
                        self.offset_found = True        #game found at offset to be NOT copied
                    offset = pgn.tell()
        except Exception as e:
            outstr = "Error opening PGN file " + self.pgnfile
            logging.info(outstr)
            logging.info(e)
            #print(outstr)
            #print(e)
            return 
        if self.offset_found:     
            if len(self.gameslist) > 0:  
                self.pgn_temp_write()               #write a modified.pgn file
            else:           #if no gameslist to write just delete pgn file
                self.delete_original()
        else:
            outstr = "No game found in PGN file at that offset to be deleted. Offset "+stroffset
            logging.info(outstr)
            messagebox.showinfo("Game not found", outstr)
            return
        
    def pgn_temp_write(self):
        #writes a file named modified.pgn with the new pgn games not including deleted
        try:
            with open("modified.pgn", "w") as f:   
                for game in self.gameslist:
                    #print(str(game))
                    f.write(str(game) + "\n\n")  # Ensure a blank line between games
            self.modified = True
        except Exception as e:
            outstr = "Error writing modified PGN file"
            logging.info(outstr)
            logging.info(e)
            print(outstr)
            print(e)
            return  
        go_on = messagebox.askokcancel("Delete PGN Game","Permanent, Are you sure you want to delete this pgn game?")
        if go_on:
            self.delete_original()  
            if self.modified:
                self.rename_modified()        
        else:
            outstr = "Aborted deleting PGN game"
            logging.info(outstr)
            print (outstr)          

    def delete_original(self):
        if os.path.isfile(self.pgnfile):
            #if it's a good file rename it
            if os.path.exists(self.pgnfile):
                try:
                    os.remove(self.pgnfile)      #remove original file
                except Exception as e:
                    outstr = "Could not remove original file"
                    logging.info(outstr)
                    logging.info(e)
                    print(outstr)
                    print(e)
                    return
                
    def rename_modified(self):                                
        try:
            os.rename("modified.pgn", self.pgnfile)
        except Exception as e:
            outstr = "Could not rename modified file"
            logging.info(outstr)
            logging.info(e)
            print(outstr)
            print(e)


if __name__ == "__main__":
    pgnfile = "test.pgn"
    offset = 167
    d_pgn = pgn_game_delete(pgnfile, offset)
    d_pgn = ""
    print("Done")