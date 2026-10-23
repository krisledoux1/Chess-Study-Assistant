#! /usr/bin/env python3

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

from libs.fileexplore import file_is
import libs.psutil as psutil
import tkinter as tk
import copy
from tkinter import ttk
from tkinter import messagebox
import os
import subprocess
import time
from datetime import datetime
import libs.chess as chess
import libs.chess.pgn
from scripts.miscclasses import tkwoterm
#from scripts.legalmove import legal_move
from scripts.chessboard import board_control
import libs.pyautogui as pyautogui
import pickle
    #fix for pickle to get a class when loading file created elsewhere chessclasses moved to root
from libs.tksheet import Sheet
import logging
logger = logging.getLogger(__name__)

class pgn_game_lister():

    def __init__(self, root):
        self.pgnlist = []
        self.agslist = []
        self.ags_mode = True        
        self.game_selected = False
        self.pgn_closed = False
        self.g_s_totmoves = 0
        self.game_offset_selected = 0
        self.agsfile = ""           #holder for ags file name selected
        self.pgnlist_items = []    #list to hold selected pgn headers
        self.pgn_error = False 
        self.pgnfile = ""
        self.continue_open = False
        self.notname = False
        self.permpgnlist = []
        self.permagslist = []      
        #self.sanmoves = []
        self.anadata = analyzed_data()      #instantiate (create) analyzed data object
        self.root = root        
        self.p = tkwoterm(self.root)
        self.p.buildframe()         #build the window for stockfish output so p.term() can display 
        self.p.iconify()            #minimize window               
        """  
        #make the pgn display window with ttk treeview
        """
        self.root.title("PGN Games Viewer")
        self.root.geometry("1100x650")
        # Top layout frame for the open file controls
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        # File browser trigger button
        self.open_button = tk.Button(
            self.control_frame, text="Browse Files", command=self.get_pgngames
        )
        self.open_button.pack(side=tk.LEFT)
        # File path status message label
        self.path_label = tk.Label(
            self.control_frame, text="No file selected", fg="gray"
        )
        self.path_label.pack(side=tk.LEFT, padx=10)
        self.filenumv_label = tk.Label(
            self.control_frame, width=5, text=""
        )       
        self.filenumv_label.pack(side=tk.RIGHT, padx=10)     
        self.filenum_label = tk.Label(
            self.control_frame, text="Number of Game Files"
        )       
        self.filenum_label.pack(side=tk.RIGHT, padx=10)        
        # Content frame for the analyze game button
        self.a_frame = tk.Frame(self.root)
        self.a_frame.pack(fill=tk.X, padx=10, pady=5)        
        # Analyze selected
        self.a_button = tk.Button(
            self.a_frame, text="Analyze selected", command=self.do_analysis, state=tk.DISABLED
        )
        self.a_button.pack(side=tk.LEFT) 
        s_fr = tk.Frame(self.a_frame, width=25, height=2)#, bg="light gray")
        s_fr.pack(side=tk.LEFT)         
        self.depth_label = tk.Label(self.a_frame, text="Depth to analyze")
        self.depth_label.pack(side=tk.LEFT)        
        # Dropdown options  
        a = ["12", "14", "18", "20", "22", "25", "27"]
        # Combobox  
        self.cb = ttk.Combobox(self.a_frame, width = 4, values=a)
        self.cb.set("20")
        self.cb.pack(side=tk.LEFT)
        s_fr = tk.Frame(self.a_frame, width=35, height=2)#, bg="light gray")
        s_fr.pack(side=tk.LEFT) 
        # AGS mode selected
        self.ags_button = tk.Button(
            self.a_frame, text="AGS", command=self.set_ags_mode, state=tk.DISABLED
        )
        self.ags_button.pack(side=tk.LEFT) 
        s_fr = tk.Frame(self.a_frame, width=25, height=2)#, bg="light gray")
        s_fr.pack(side=tk.LEFT)         
        # Chessboard mode selected
        self.cb_button = tk.Button(
            self.a_frame, text="Board", command=self.chess_board_open#, state=tk.DISABLED
        )
        self.cb_button.pack(side=tk.LEFT) 
        s_fr = tk.Frame(self.a_frame, width=25, height=2)#, bg="light gray")
        s_fr.pack(side=tk.LEFT)                               
        self.fnames_label = tk.Label(
            self.a_frame, text="Filter Names in List"
        )      
        self.fnames_label.pack(side=tk.LEFT)
        self.fnames_ent = tk.Entry(
            self.a_frame, width = 27, bg="white"
        )       
        self.fnames_ent.pack(side=tk.LEFT, padx=4)                 
        self.ch_not=tk.Checkbutton(self.a_frame,
            text='Not',
            command = self.cb_not_clicked,
            font=('arial', 12, 'normal'),
            highlightthickness = 0)
        self.ch_not.pack(side = tk.LEFT, anchor = "w")        
        # Filter PGN's trigger button
        self.filter_button = tk.Button(
            self.a_frame, text="Filter Games", command=self.filter_sort
        )
        self.filter_button.pack(side=tk.RIGHT)                                  
        # Content frame for the spreadsheet-style tree grid
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)        
        # Setup standard scrollbars
        self.v_scroll = ttk.Scrollbar(self.display_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = ttk.Scrollbar(self.display_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)        
        self.style = ttk.Style()        #allow selected colors to be changed if already analysed
        self.style.map('Treeview',
                  background=[('selected', '#0c2b87')],  # Selected row background color
                  foreground=[('selected', 'white')])    # Selected row text color           
        # Initialize blank view grid layout component
        self.tree = ttk.Treeview(        
            self.display_frame,
            selectmode="browse",            
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        # Link scrollbar functionality to the data display grid view widget
        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)  
        logging.info("\n\nStarting Application\n")
        self.get_agsgames()      
        """
        End of window
        """

    def cb_not_clicked(self):
        if self.notname == False:
            self.notname = True
            #self.ch_select.select()
        else:
            self.notname = False
            
    def set_ags_mode(self):
        self.ags_mode = True    
        self.ags_button.config(state=tk.DISABLED)  
        self.get_agsgames()
         
    def get_ags_files(self):
        #get all of the files in the currentworkingdirectory/saved that have .ags extension
        cwd = os.getcwd()
        path = cwd + "/saved/"        
        temp = []
        if not os.path.isdir(path):          #make sure directory path exists
            logging.error("Saved path not found")
            return temp     #if directory doesn't exist return with no list
        for file in os.listdir(path): 
            if file.startswith("."):
                continue        #skip over all hidden files so not in list  
            if os.path.isfile(os.path.join(path, file)):       #if this is a file not a directory
                sfile, _, extension = file.rpartition(".")       
                if extension == "ags":
                    temp.append(sfile)      #append filename without . or extension
        return temp

    def get_agsgames(self):
        self.root.title("AGS Games Viewer")
        #self.control_frame.configure( bg="blue")#frm_bg1)
        self.path_label.config(text="Displaying Analyzed Game Files (.ags) in saved directory", fg="blue")        
        self.filenum_label.config(text="Number of AGS games ")
        files = self.get_ags_files()
        self.agslist = []
        headers = ["Offset","Date","White","Elo","Black","Elo ","Result","Moves","Event","Site"]
        self.agslist.append(headers)
        counter = 0
        self.a_button.config(state=tk.DISABLED)     #analysis button
        for file in files: 
            add_list = []       #temp list for filling in with agslist data    
            temp = file.split("_")  #list for filename divided by "_"
            if len(temp) < 6:
                continue
            add_list.append(file)
            add_list.append(temp[0])    #date
            add_list.append(temp[1])    #white name
            add_list.append("ags")
            add_list.append(temp[2])    #black name
            add_list.append("ags")
            add_list.append(temp[3])    #result
            add_list.append(temp[5])    #moves
            add_list.append(temp[4])    #depth
            add_list.append("")                       
            self.agslist.append(add_list)            
            counter += 1
        self.permagslist = []
        print("%^%^%^%^%^%^%^%^%^%^%%^%^%^%^%^%^%^%^%^%^%^%^%^")
        for item in self.agslist:
            self.permagslist.append(item)      #Make a permanent separate cloned copy of list read from file
        self.filter_sort()

    def in_agslist(self):
        ags = []
        temp = []
        agscomparelist = []
        for item in self.permagslist:
            ags.append(item)      #Make a permanent separate cloned copy of list read from file        
        pgn = self.pgnlist_items.copy()
        for item in ags: 
            temp.append(item[1])        #date
            temp.append(item[2])        #white
            temp.append(item[4])        #black
            temp.append(item[6])        #result
            temp.append(item[7])        #moves
            agscomparelist.append(temp)
            temp = []
        temp.append(pgn[0][1])        #date
        temp.append(pgn[0][2])        #white
        temp.append(pgn[0][4])        #black
        temp.append(pgn[0][6])        #result
        temp.append(pgn[0][7])        #moves       
        if temp in agscomparelist:
            self.style.map('Treeview',
                      background=[('selected', 'white')],  # Selected row background color
                      foreground=[('selected', '#4d6dc4')])    # Selected row text color            
        else:                      
            self.style.map('Treeview',
                      background=[('selected', '#0c2b87')],  # Selected row background color
                      foreground=[('selected', 'white')])    # Selected row text color
              
    def get_pgngames(self):
        # Read the PGN file and create a CSV (list of lists) to display games in PGN file in treeview
        cwd = os.getcwd()
        _, self.pgnfile = file_is(cwd,["ags","pgn"]) 
        message = "opening " + self.pgnfile       
        logging.info(message)
        if not os.path.isfile(self.pgnfile):
            #print("Not isfile?")
            tempstr = self.pgnfile + " not found?"
            logging.error(tempstr)
            return
        extension = self.pgnfile.rpartition(".")[-1]
        try:
            self.p.iconify() 
        except:     #tkterm window is gone so recreate it
            self.p.buildframe()  
        #print(extension)  # Output: 'csv' (Note: does not include the dot)
        if extension == "ags":      #one game already analyzed so just display analyzed data
            fileok = self.load_analyzed()              
            if fileok:
                self.show_analysis()
            return
        if extension != "pgn":
            print("Not PGN")
            return
        self.root.title("PGN Games Viewer") 
        self.filenum_label.config(text="Number of PGN games ") 
        self.ags_mode = False  
        self.tree.delete(*self.tree.get_children())  #clear tree since new pgn loading 
        self.root.update()          
        self.pgnlist = []
        self.ags_button.config(state=tk.NORMAL)     #AGS button to go back to showing ags games
        headers = ["Offset","Date","White","Elo","Black","Elo ","Result","Moves","Event","Site"]
        self.pgnlist.append(headers)
        counter = 0
        #self.a_button.config(state=tk.DISABLED)        
        with open(self.pgnfile, "r")as pgn:  
            while True:
                add_list = []         
                #game = chess.pgn.read_game(pgn)
                offset = pgn.tell()
                # to go to a game use it's offset   pgn.seek(offset)             
                game_data = chess.pgn.read_game(pgn)
                if game_data == None:       #done if game_data = None
                    break
                # Count the total half-moves (plies)
                total_plies = sum(1 for _ in game_data.mainline_moves()) 
                total_moves = (total_plies + 1) // 2  #rounds up because dividend + divisor -1 (divisor 2 - 1 is 1) causes round up in positive number
                if total_moves < 2:      #no game data as not a PGN???
                    continue                
                # Access pgn game_data  
                add_list.append(offset)                    
                add_list.append(game_data.headers["Date"])
                add_list.append(game_data.headers["White"])
                try:
                    add_list.append(game_data.headers["WhiteElo"])
                except:
                    add_list.append("")                               
                add_list.append(game_data.headers["Black"])
                try:
                    add_list.append(game_data.headers["BlackElo"])
                except:
                    add_list.append("")                                     
                add_list.append(game_data.headers["Result"]) 
                add_list.append(str(total_moves))
                try:                
                    add_list.append(game_data.headers["Event"])
                except:
                    add_list.append("")
                try:                 
                    add_list.append(game_data.headers["Site"])                                
                except:
                    add_list.append("")                     
                self.pgnlist.append(add_list)
                counter +=1
        if len(self.pgnlist) < 1 or counter < 1:
            self.pgn__error = True
            logerror = self.pgnfile + " does not seem to be a valid pgn file"
            logging.error(logerror)
            print("PGN ERROR ERROR")
            return
        self.path_label.config(text=self.pgnfile, fg="black") 
        self.permpgnlist = self.pgnlist.copy()      #Make a permanent copy of list read from file
        self.filter_sort()
         
    def filter_sort(self):
        #filter and sort pgnlist for display
        self.a_button.config(state=tk.DISABLED)        
        if self.ags_mode:       #do if ags mode
            self.pgnlist = []
            for item in self.permagslist:
                self.pgnlist.append(item)      #Make a permanent separate cloned copy of list read from file                  
        else:               #do if pgn mode        
            self.pgnlist = self.permpgnlist.copy()   #get a new copy for each filter and display
        if len(self.pgnlist) > 0:
            head = self.pgnlist.pop(0)      #remove the headers from pgnlist so they do not get filtered or sorted  
            filterstr = self.fnames_ent.get()       #get value from filter text entry      
            if filterstr != "":         #if there is a value in filter entry then filter                    
                filterable = self.pgnlist.copy()
                if self.notname:        #filter filterstring out of list (NOT)
                    filtered_result = [w for w in filterable if filterstr not in w[2] and filterstr not in w[4]]
                else:
                    filtered_result = [w for w in filterable if filterstr in w[2] or filterstr in w[4]]            
                sortable = filtered_result.copy()
            else:       #If not filtered then sortable needs to be set
                sortable = self.pgnlist.copy()                        
            valid_formats = ["%Y.%m.%d", "%Y/%m/%d", "%d-%m-%Y"]
            def parse_with_fallback(date_str):
                for fmt in valid_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                # Fallback for completely unparseable formats
                return datetime.strptime("2000.01.01", "%Y.%m.%d")
            # Sort ascending (Newest first)
            # x[1] points to the index of the date field in the sublist
            sorted_data = sorted(sortable, key=lambda x: parse_with_fallback(x[1]), reverse=True)
            self.pgnlist = sorted_data      #sorted pgnlist
            totpgns = len(self.pgnlist)
            self.filenumv_label.config(text=totpgns, fg="black")             
            self.pgnlist.insert(0,head)     #put the header back on           
            self.display_pgnlist()

    def display_pgnlist(self):

        self.clear_existing_grid()
        reader = self.pgnlist#csv.reader(file)
        headers = self.pgnlist[0]  # Track first dataset row as label text
        # Establish structural grid schema attributes         
        self.tree["columns"] = headers
        self.tree["displaycolumns"] = ("Date", "White","Elo","Black","Elo ","Result","Moves","Event","Site")
        self.tree["show"] = "headings"  #Hide the zero column
        # Hides the first tree column completely
        #self.tree.column('size', width=100, anchor='center')
        self.tree.column('Date', width=110, anchor='w', stretch=False)       
        self.tree.column('White', width=250, anchor='w', stretch=False)
        self.tree.column('Elo', width=60, anchor='w', stretch=False)        
        self.tree.column('Black', width=250, anchor='w', stretch=False)
        self.tree.column('Elo ', width=60, anchor='w', stretch=False)         
        self.tree.column('Result', width=70, anchor='w', stretch=False)
        self.tree.column('Moves', width=70, anchor='w', stretch=False)
        self.tree.column('Event', width=110, anchor='w')        
        self.tree.column('Site', width=110, anchor='w')                                
        for col in headers:
            self.tree.heading(col, text=col)
            #self.tree.column(col, width=120, anchor=tk.W)

        # Feed rows item-by-item into the list matrix structure array
        for row_data in reader[1:]:
            self.tree.insert("", tk.END, values=row_data)
        #self.tree.selection_clear()             
        self.tree.bind("<<TreeviewSelect>>", self.get_tree_item_selected)                       
        
    def get_tree_item_selected(self,event):
        selected_ids = self.tree.selection()
        if selected_ids != (): 
            self.pgnlist_items = []    
            self.a_button.config(state=tk.NORMAL)
            # Get the unique ID of the selected item
            selected_id = self.tree.selection()[0]
            # Find its 0-indexed position among visible children
            row_number = self.tree.get_children().index(selected_id)
            row_number +=1      #align with offset of headers creation
            self.game_offset_selected = self.pgnlist[row_number][0] #offsets are in pgnlist showing how offset for a particular game
            self.pgnlist_items.append(self.pgnlist[row_number])      #store the list items of that game
            self.agsfile = self.pgnlist[row_number][0] #filename stores same as offset for ags file instead of offset
            self.g_s_totmoves = self.pgnlist[row_number][7]   #total number of moves that are in selected game 
            if not self.ags_mode:
                self.in_agslist()
        
    def clear_existing_grid(self):
        # Delete prior iterations before rebuilding structural headings rows
        self.tree.delete(*self.tree.get_children()) 
        self.tree.selection_clear()       

    def do_analysis(self):
        self.a_button.config(state=tk.DISABLED)
        if self.ags_mode:       #if in agsmode then just display the analysis
            cwd = os.getcwd()
            path = cwd + "/saved/"        
            temp = []
            if not os.path.isdir(path):          #make sure directory path exists
                tempstr = path + " not found?"
                logging.error(tempstr)            
                return     #if directory doesn't exist return       
            self.pgnfile = path + self.agsfile + ".ags"       #fill out filename from data
            logging.info(self.pgnfile)            
            fileok = self.load_analyzed()              
            if fileok:
                self.show_analysis()
        else:                           #in PGN mode so process pgn
            # to go to a game use it's offset   pgn.seek(offset)
            with open(self.pgnfile, "r")as pgn:
                pgn.seek(self.game_offset_selected)
                game = chess.pgn.read_game(pgn)
            depth_to_analyze = int(self.cb.get())         
            try:
                self.p.deiconify() 
            except:     #tkterm window is gone so recreate it
                self.p.buildframe()
            logging.info(self.pgnfile)
            temp = "offset " + str(self.game_offset_selected)
            logging.info(temp)          
            logging.info("Calling Stockfish from Analyze game")                               
            start = time.time()          
            self.analyzed_object = chessgame_analyze(game, self.p, depth_to_analyze, self.anadata, self.g_s_totmoves)
            start2 = time.time()
            start3 = int(round(start2 - start, 2))        
            sec_permove = round(start3 / (int(self.g_s_totmoves) * 2),2)
            temp = "Analysis time for this analysis " + str(start3) + " Seconds. (Secs per move) " + str(sec_permove) + ". Max temp " + str(self.analyzed_object.maxcputemp)
            self.p.term(temp)
            if self.analyzed_object.maxcputemp == 1111:             #cpu set to 1111 when analysis aborted
                self.p.term("Analysis was aborted by mouse positioned on left side of screen")
                return
            try:
                self.p.iconify() 
            except:     #tkterm window is gone so recreate it
                self.p.buildframe()          
            self.save_analyzed()
            self.show_analysis()
                
    def show_analysis(self):
        self.buildwindow()
        self.display_analist()
        
    def buildwindow(self):        
        self.anawin = tk.Toplevel(takefocus=True)
        self.anawin.title('Analysis of PGN')
        self.anawin.geometry('1252x693+15+10')
        # Top layout frame for the open file controls
        self.data_frame = tk.Frame(self.anawin)
        self.data_frame.pack(fill=tk.X, padx=10, pady=10)        
        # Configure data_frame columns to have equal weight and size
        self.data_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.data_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.data_frame.grid_rowconfigure(5, weight=1)
        frm_bg1 = "#83e3ff"
        frm_bg2 = "#86eafa"
        # Frames for White info
        self.white_frame0 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.white_frame0.grid(row=0, column=0, sticky="nsew")
        self.white_frame1 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.white_frame1.grid(row=1, column=0, sticky="nsew")
        self.white_frame2 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.white_frame2.grid(row=2, column=0, sticky="nsew")
        self.white_frame3 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.white_frame3.grid(row=3, column=0, sticky="nsew")  
        self.white_frame4 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.white_frame4.grid(row=4, column=0, sticky="nsew") 
        self.white_frame5 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.white_frame5.grid(row=5, column=0, sticky="nsew") 
        self.white_frame6 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.white_frame6.grid(row=6, column=0, sticky="nsew")                                
        self.tdw_lbl = tk.Label(self.white_frame0, text="Total Points Lost", bg=frm_bg1)
        self.tdw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame0, width=55, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)        
        self.tdvw_lbl = tk.Label(self.white_frame0, text="", bg=frm_bg1)
        self.tdvw_lbl.pack(side=tk.LEFT, padx=10)         
        self.adw_lbl = tk.Label(self.white_frame1, text="Average Points Lost", bg=frm_bg2)
        self.adw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame1, width=34, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)        
        self.advw_lbl = tk.Label(self.white_frame1, text="", bg=frm_bg2)
        self.advw_lbl.pack(side=tk.LEFT, padx=10)         
        self.arw_lbl = tk.Label(self.white_frame2, text="Average Choice", bg=frm_bg1)
        self.arw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame2, width=61, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)
        self.arvw_lbl = tk.Label(self.white_frame2, text="", bg=frm_bg1)
        self.arvw_lbl.pack(side=tk.LEFT, padx=10) 
        self.s_diffw_lbl = tk.Label(self.white_frame3, text="10 Moves points", bg=frm_bg2)
        self.s_diffw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame3, width=60, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)
        self.s_diffwv_lbl = tk.Label(self.white_frame3, text="", bg=frm_bg2)
        self.s_diffwv_lbl.pack(side=tk.LEFT, padx=10) 
        self.s_avw_lbl = tk.Label(self.white_frame4, text="10 Average choice", bg=frm_bg1)
        self.s_avw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame4, width=45, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)
        self.s_avwv_lbl = tk.Label(self.white_frame4, text="", bg=frm_bg1)
        self.s_avwv_lbl.pack(side=tk.LEFT, padx=10) 
        
        self.wblund_lbl = tk.Label(self.white_frame5, text = "Blunders", bg=frm_bg2)
        self.wblund_lbl.pack(side=tk.LEFT, padx=10)
        self.wblundv_lbl = tk.Label(self.white_frame5, text = " ", bg=frm_bg2)
        self.wblundv_lbl.pack(side=tk.LEFT, padx=10)          
        s_fr = tk.Frame(self.white_frame5, width=74, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)        
        self.wbmld_lbl = tk.Label(self.white_frame5, text = "Mild", bg=frm_bg2)
        self.wbmld_lbl.pack(side=tk.LEFT, padx=10)
        self.wbmldv_lbl = tk.Label(self.white_frame5, text = " ", bg=frm_bg2)
        self.wbmldv_lbl.pack(side=tk.LEFT, padx=10)        
        self.wbmed_lbl = tk.Label(self.white_frame5, text = "Medium", bg=frm_bg2)
        self.wbmed_lbl.pack(side=tk.LEFT, padx=10)
        self.wbmedv_lbl = tk.Label(self.white_frame5, text = " ", bg=frm_bg2)
        self.wbmedv_lbl.pack(side=tk.LEFT, padx=10)         
        self.wbmj_lbl = tk.Label(self.white_frame5, text = "Major", bg=frm_bg2)
        self.wbmj_lbl.pack(side=tk.LEFT, padx=10)                
        self.wbmjv_lbl = tk.Label(self.white_frame5, text = " ", bg=frm_bg2)
        self.wbmjv_lbl.pack(side=tk.LEFT, padx=10)                  
                               
        self.nw_lbl = tk.Label(self.white_frame6, text="White", bg=frm_bg1)
        self.nw_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.white_frame6, width=125, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)        
        self.nvw_lbl = tk.Label(self.white_frame6, text="", bg=frm_bg1)
        self.nvw_lbl.pack(side=tk.LEFT, padx=10)     
        self.rslt_lbl = tk.Label(self.white_frame6, text="", bg=frm_bg1)     #label for result
        self.rslt_lbl.pack(side=tk.RIGHT, padx=20)
        self.rst_lbl = tk.Label(self.white_frame6, text="Result", bg=frm_bg1)
        self.rst_lbl.pack(side=tk.RIGHT, padx=2)    
        # Frames for Black info
        self.black_frame0 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.black_frame0.grid(row=0, column=1, sticky="nsew")
        self.black_frame1 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.black_frame1.grid(row=1, column=1, sticky="nsew")
        self.black_frame2 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.black_frame2.grid(row=2, column=1, sticky="nsew")
        self.black_frame3 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.black_frame3.grid(row=3, column=1, sticky="nsew")
        self.black_frame4 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.black_frame4.grid(row=4, column=1, sticky="nsew")  
        self.black_frame5 = tk.Frame(self.data_frame, bg=frm_bg2)
        self.black_frame5.grid(row=5, column=1, sticky="nsew") 
        self.black_frame6 = tk.Frame(self.data_frame, bg=frm_bg1)
        self.black_frame6.grid(row=6, column=1, sticky="nsew")                                  
        self.tdb_lbl = tk.Label(self.black_frame0, text="Total Points Lost", bg=frm_bg1)
        self.tdb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame0, width=55, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)        
        self.tdvb_lbl = tk.Label(self.black_frame0, text="", bg=frm_bg1)
        self.tdvb_lbl.pack(side=tk.LEFT, padx=10)        
        self.datev_lbl = tk.Label(self.black_frame0, text="", bg=frm_bg1)   #depth
        self.datev_lbl.pack(side=tk.RIGHT, padx=20)        
        self.date_lbl = tk.Label(self.black_frame0, text="Game Date", bg=frm_bg1)
        self.date_lbl.pack(side=tk.RIGHT, padx=2)                          
        self.adb_lbl = tk.Label(self.black_frame1, text="Average Points Lost", bg=frm_bg2)
        self.adb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame1, width=34, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)        
        self.advb_lbl = tk.Label(self.black_frame1, text="", bg=frm_bg2)
        self.advb_lbl.pack(side=tk.LEFT, padx=10)         
        self.movev_lbl = tk.Label(self.black_frame1, text="", bg=frm_bg2)   #depth
        self.movev_lbl.pack(side=tk.RIGHT, padx=30)        
        self.move_lbl = tk.Label(self.black_frame1, text="Total moves", bg=frm_bg2)
        self.move_lbl.pack(side=tk.RIGHT, padx=30)                         
        self.arb_lbl = tk.Label(self.black_frame2, text="Average Choice", bg=frm_bg1)
        self.arb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame2, width=61, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)
        self.arvb_lbl = tk.Label(self.black_frame2, text="", bg=frm_bg1)
        self.arvb_lbl.pack(side=tk.LEFT, padx=10)        
        self.s_diffb_lbl = tk.Label(self.black_frame3, text="10 Moves points", bg=frm_bg2)
        self.s_diffb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame3, width=60, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)
        self.s_diffbv_lbl = tk.Label(self.black_frame3, text="", bg=frm_bg2)
        self.s_diffbv_lbl.pack(side=tk.LEFT, padx=10) 
        self.s_avb_lbl = tk.Label(self.black_frame4, text="10 Average choice", bg=frm_bg1)
        self.s_avb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame4, width=45, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)
        self.s_avbv_lbl = tk.Label(self.black_frame4, text="", bg=frm_bg1)
        self.s_avbv_lbl.pack(side=tk.LEFT, padx=10) 
        
        self.bblund_lbl = tk.Label(self.black_frame5, text = "Blunders", bg=frm_bg2)
        self.bblund_lbl.pack(side=tk.LEFT, padx=10) 
        self.bblundv_lbl = tk.Label(self.black_frame5, text = " ", bg=frm_bg2)
        self.bblundv_lbl.pack(side=tk.LEFT, padx=10)         
        s_fr = tk.Frame(self.black_frame5, width=74, height=2, bg=frm_bg2)
        s_fr.pack(side=tk.LEFT)        
        self.bbmld_lbl = tk.Label(self.black_frame5, text = "Mild", bg=frm_bg2)
        self.bbmld_lbl.pack(side=tk.LEFT, padx=10)
        self.bbmldv_lbl = tk.Label(self.black_frame5, text = " ", bg=frm_bg2)
        self.bbmldv_lbl.pack(side=tk.LEFT, padx=10)        
        self.bbmed_lbl = tk.Label(self.black_frame5, text = "Medium", bg=frm_bg2)
        self.bbmed_lbl.pack(side=tk.LEFT, padx=10)
        self.bbmedv_lbl = tk.Label(self.black_frame5, text = " ", bg=frm_bg2)
        self.bbmedv_lbl.pack(side=tk.LEFT, padx=10)         
        self.bbmj_lbl = tk.Label(self.black_frame5, text = "Major", bg=frm_bg2)
        self.bbmj_lbl.pack(side=tk.LEFT, padx=10)                
        self.bbmjv_lbl = tk.Label(self.black_frame5, text = " ", bg=frm_bg2)
        self.bbmjv_lbl.pack(side=tk.LEFT, padx=10)           
                                                          
        self.nb_lbl = tk.Label(self.black_frame6, text="Black", bg=frm_bg1)
        self.nb_lbl.pack(side=tk.LEFT, padx=10) 
        s_fr = tk.Frame(self.black_frame6, width=126, height=2, bg=frm_bg1)
        s_fr.pack(side=tk.LEFT)        
        self.nvb_lbl = tk.Label(self.black_frame6, text="", bg=frm_bg1)
        self.nvb_lbl.pack(side=tk.LEFT, padx=10)        
        self.dpthv_lbl = tk.Label(self.black_frame6, text="", bg=frm_bg1)   #depth
        self.dpthv_lbl.pack(side=tk.RIGHT, padx=20)        
        self.dpth_lbl = tk.Label(self.black_frame6, text="Depth", bg=frm_bg1)
        self.dpth_lbl.pack(side=tk.RIGHT, padx=2)  

        # Content frame for the spreadsheet-style tree grid
        self.display_frame = tk.Frame(self.anawin)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        #self.anawin.protocol("WM_DELETE_WINDOW", self.destroywin)        
        # Initialize an empty Sheet widget
        self.asheet = Sheet(self.display_frame)#, yscrollcommand=self.av_scroll.set, xscrollcommand=self.ah_scroll.set)
        self.asheet.pack(fill=tk.BOTH, expand=True)        
        
        # Enable key sheet behaviors
        self.asheet.enable_bindings("all")          

    def display_analist(self):

        def color_sheet_by_value(sheet, target_col, blunder):
            """
            Iterates through a specific column and colors cells based on their values.
            """
            # Retrieve all current sheet data
            data = sheet.get_sheet_data()
            
            # Iterate through each row in the specified column
            for row_idx, row_data in enumerate(data):
                # Prevent index errors if rows are uneven
                if target_col < len(row_data):
                    c_value = row_data[target_col]
                    try:
                        cell_value = int(c_value)
                    except:
                        continue
                    # Apply your conditional formatting logic here
                    if cell_value > 3.9:        #big blunder
                        sheet.highlight_cells(row=row_idx, column=target_col, bg="#a80747", fg="black")
                        blunder[0] += 1     #increase total blunder count
                        blunder[3] += 1     #increase total blunder count                        
                    elif cell_value > 1.8:       #medium blunder
                        sheet.highlight_cells(row=row_idx, column=target_col, bg="#e66eb2", fg="black")
                        blunder[0] += 1     #increase total blunder count  
                        blunder[2] += 1     #increase total blunder count                                              
                    elif cell_value > .8:       #mild blunder
                        sheet.highlight_cells(row=row_idx, column=target_col, bg="#e8dd3c", fg="black")
                        blunder[0] += 1     #increase total blunder count 
                        blunder[1] += 1     #increase total blunder count                                               
            return blunder
        def color_column(sheet, target_col, bg_color = "#ebf3f5", fg_color = "#000000"):
            # Loop through each row and color the cell in the target column
            total_rows = sheet.get_total_rows()
            for row in range(total_rows):
                sheet.highlight_cells(row, target_col, bg=bg_color, fg=fg_color)                        

        wblunders = [0,0,0,0]
        bblunders = [0,0,0,0]
       
        self.aclear_existing_grid()
        reader = self.anadata.getlists()#csv.reader(file)
        headers = reader[0]  # Track first dataset row as label text
        
        # Separate the first row as headers, rest as data rows
        headers = reader[0]
        rows = reader[1:]
        
        # Update tksheet display contents
        self.asheet.headers(headers)
        self.asheet.set_sheet_data(rows)        
              
        # hide columns
        currently_displayed = self.asheet.display_columns()
        # 2. Specify the column indexes you want to HIDE (e.g., columns 1 and 2)
        to_hide = [11]
        # 3. Create a list of columns to KEEP
        to_display = [c for c in currently_displayed if c not in to_hide]
        # 4. Update the sheet to only display the kept columns
        self.asheet.display_columns(columns=to_display, all_columns_displayed=False)       
        # Set widths for columns respectively
        self.asheet.set_column_widths([60, 110, 220, 60, 70,100,110,220,60,70,100])        

        # Highlight column 0 with a red background and white text
        # The canvas parameter can be 'table', 'header', 'row_index', or 'all'
        wblunders = color_sheet_by_value(self.asheet, 3, wblunders)        
        bblunders = color_sheet_by_value(self.asheet, 8, bblunders)
        color_column(self.asheet, 5) 
        color_column(self.asheet, 10)               
        self.asheet.refresh()  
                  
        #labels = self.anadata.getlabels()
        self.wblundv_lbl.config(text=wblunders[0]) 
        self.wbmldv_lbl.config(text=wblunders[1])
        self.wbmedv_lbl.config(text=wblunders[2]) 
        self.wbmjv_lbl.config(text=wblunders[3])
        self.bblundv_lbl.config(text=bblunders[0]) 
        self.bbmldv_lbl.config(text=bblunders[1])
        self.bbmedv_lbl.config(text=bblunders[2]) 
        self.bbmjv_lbl.config(text=bblunders[3])                                    
        last_value = reader[-1] 
        try:
            self.tdvw_lbl.config(text=self.anadata.lbldict["tdiffw"])    #total points lost
            self.tdvb_lbl.config(text=self.anadata.lbldict["tdiffb"])         
            self.advw_lbl.config(text=self.anadata.lbldict["avdiffw"])    #average points lost
            self.advb_lbl.config(text=self.anadata.lbldict["avdiffb"])                   
            self.arvw_lbl.config(text=self.anadata.lbldict["avchoicew"])    #average Choice
            self.arvb_lbl.config(text=self.anadata.lbldict["avchoiceb"])        
            self.nvw_lbl.config(text=self.anadata.lbldict["namew"])        #White player name
            self.rslt_lbl.config(text=self.anadata.lbldict["result"])      #result 
            self.nvb_lbl.config(text=self.anadata.lbldict["nameb"])        #Black player name         
            self.dpthv_lbl.config(text=self.anadata.lbldict["depth"])       #depth 
            self.datev_lbl.config(text=self.anadata.lbldict["date"])       #date
            self.movev_lbl.config(text=self.anadata.lbldict["moves"])       #total moves
            self.s_diffwv_lbl.config(text=self.anadata.lbldict["10diffw"])       #10 move difference
            self.s_diffbv_lbl.config(text=self.anadata.lbldict["10diffb"])    
            self.s_avwv_lbl.config(text=self.anadata.lbldict["10avchoicew"])       #10 move avg choice
            self.s_avbv_lbl.config(text=self.anadata.lbldict["10avchoiceb"])       #                                 
        except:
            print("label missing")
        # 2. Bind the selection event to the callback function
        self.asheet.extra_bindings("row_select", self.aget_tree_item_selected)                             

    def aget_tree_item_selected(self,event):

        #self.asheet.select_row(event.selected.row,redraw=False,run_binding_func=False)
   
        if self.continue_open:     
            return          #continue window is already open and selection is being syncronized to window so just return
        row_number = event.selected.row +1
        half_number = row_number *2 -1      #align with offset of headers creation               
        self.show_cont(half_number)   #row_number is move 
                
            
    def show_cont(self, s_move):     #`
        #print(self.anadata.bestmoves[2])
        #self.cb_button.config(state=tk.DISABLED) 
        self.pgn_closed = False
        try:
            engine2 = bestmove(self.p)      #Istantiate bestmove class to start engine connection
        except ValueError as e:
            print(e)  # engine gave no uciok 
            self.p.term(e)      #send to both   
        self.continue_open = True            
        logging.info("Opening continuation window")                        
        #root, engine, contwindow, anadata, halfmoves, asheet reference          
        self.chessgame = board_control(self.root, engine2, True, self.anadata, s_move, self.asheet)           #create object chessboard for play or pgn entry
        engine2.engine.terminate_engine()
        logging.info("Continue window closed")
        #self.a_button.config(state = tk.NORMAL)
        #if self.chessgame.board_closed:
         #   self.cb_button.config(state=tk.NORMAL)
        self.chessgame = ""        
        self.continue_open = False               
        return
      
   
    def aclear_existing_grid(self):
        # Delete prior iterations before rebuilding structural headings rows
        #self.atree.delete(*self.atree.get_children())
        self.asheet.delete(*self.asheet.get_children())
 
    def save_analyzed(self):
        # Save the object to a file 6 white 8 black 7 result 9 depth ags analyzed game save
        sp = "_"
        rslt = self.anadata.lbldict["result"]    #game result
        if rslt =="1/2-1/2":
            rslt = "2-2"
        if " " in rslt:
            rslt = rslt.replace(" ", "")
        if "*" in rslt:
            rslt = rslt.replace("*", "-")            
        cwd = os.getcwd()
        path = cwd + "/saved/"
        sfil = path + self.anadata.lbldict["date"] + sp + self.anadata.lbldict["namew"] + sp + self.anadata.lbldict["nameb"] + sp        
        sfile = sfil + rslt + sp + self.anadata.lbldict["depth"] + sp + str(self.anadata.lbldict["moves"]) + ".ags"
        while os.path.isfile(sfile):   #change filename as it already exists
            left, sep, right = sfile.rpartition(".")
            sfile = left + "_c" + sep + right        
        
        with open(sfile, "wb") as file:
            pickle.dump(self.anadata, file)       

    def load_analyzed(self):            
        # Load the object back from the file
        with open(self.pgnfile, "rb") as file:
            try:
                self.anadata = pickle.load(file)
            except:
                logging.exception("pickle could not parse file")
                #print ("pickle could not parse file")
                return False
            return True     #file parsed ok                          

    def chess_board_open(self):
        self.cb_button.config(state=tk.DISABLED) 
        self.pgn_closed = False
        
        try:
            engine2 = bestmove(self.p)      #Istantiate bestmove class to start engine connection
        except ValueError as e:
            print(e)  # engine gave no uciok 
            self.p.term(e)      #send to both            
                  
        self.chessgame = board_control(self.root, engine2)           #create object chessboard for play or pgn entry
        engine2.engine.terminate_engine()
        logging.info("PGN window closed")
        self.cb_button.config(state = tk.NORMAL)        
        if self.chessgame.board_closed:
            self.cb_button.config(state=tk.NORMAL)
        self.chessgame = ""
               
class chessgame_analyze():
#
# Class object of one chess game created from stockfish analysis.
# Record headers
# Record actual move first along with best moves
# Record scores in same format as above
#
    def __init__(self, game_pgn, p, depth, data_obj, totmoves):
        #self.pgnfilename = pgnfilename          #pgn file name this came from
        #self.pgngamenum = pgngamenum    #game number of the pgn file
        self.data = data_obj
        self.depth = depth              #depth to analyze with stockfish
        self.totmoves = totmoves        #total number of moves in selected game
        self.game_pgn = game_pgn        #pgn data of one game to be processed with stockfish (pgn data from python chess)
        self.maxcputemp = 0         #record maximum cpu temp from processing pgn with stockfish         
        self.p = p       
        self.event = ""              #event name
        self.site = ""                #site of event
        self.date = ""                #date of game
        self.tround = ""            #round of tournament (round is python word)
        self.white = ""              #white player name
        self.black = ""              #black player name
        self.result = ""            #result of game
        self.moves = []                 #list of list of moves from stockfish with actual move made and score first in list
        self.scores = []                #list of list of scores from moves list first actual move rest stockfish moves
        self.moveplace = []             #list of place of move 1-5 or 6
        self.scorediff = []             #list of the difference each move from stockfish best or first move
        self.ana_list = []              #list of lists to display analysys bu move white black both   
        self.get_headers()              #get the headers from the game_pgn 
        self.pgn_process()

    def get_headers(self):
        self.event = self.game_pgn.headers["Event"]
        self.site = self.game_pgn.headers["Site"]
        self.date = self.game_pgn.headers["Date"]
        self.tround = self.game_pgn.headers["Round"]
        self.white = self.game_pgn.headers["White"]
        try:
            welo = self.game_pgn.headers["WhiteElo"]
            if welo:        #if welo is not none then add it to white name
                self.white = self.white + "(" + welo + ")"            
        except:
            pass
        self.black = self.game_pgn.headers["Black"]
        try:
            belo = self.game_pgn.headers["BlackElo"]
            if belo:        #if welo is not none then add it to white name
                self.black = self.black + "(" + belo + ")"            
        except:
            pass        
        self.result = self.game_pgn.headers["Result"]                                                

    def bestlistslimit(self, b_lalg, scores):
        bmoves = []
        bscores = []
        limit = 0         #limit list length to actual moves only keep moves, not "" as a move holder
        for i in b_lalg:
            if i == "":
                break
            limit += 1
        if limit > 3:
            limit = 3
        count = 0
        for i in range(limit):                   
              bmoves.append(b_lalg[count])
              bscores.append(scores[count])
              count +=1
        return bmoves, bscores
              
    def pgn_process(self):
        try:
            engine = bestmove(self.p)      #Istantiate bestmove class to start engine connection
        except ValueError as e:
            print(e)  # engine gave no uciok 
            self.p.term(e)      #send to both             
        total_diff_white = 0
        total_diff_black = 0 
        total_Choice_white = 0
        total_Choice_black = 0
        need_first_movenum = True
        moves_list = []
        san_list = []
        scores = []     #list of the scores for moves
        moves = []      #list of moves       
        b_moves = []
        b_scores = []
        fenlist = []
        white_moves = 0
        black_moves = 0 
        headers = ["Move","Your Move","Best","Diff","Choice","Score","Your Move","Best ","Diff ","Choice ","Score ","fen"]
        self.ana_list.append(headers)      
        board = self.game_pgn.board()
        tempana_list = []
        black_move = False
        wfen = ""
        for move in self.game_pgn.mainline_moves():
            moves.clear()
            scores.clear()             
            fen = board.fen()
            cboard = str(chess.Board(fen))
            self.p.term(cboard)        #show a representation of board
            _,_,movenum = fen.rpartition(" ",)
            x = int (movenum)
            #need first movenum for games that start with a FEN not at first move.  Fill in space for lalg and san til first real move
            if need_first_movenum:
                need_first_movenum = False
                if x > 1:               #add in spaces for moves leading up to actual real first move since FEN started later move
                    x = (x-1) *2        #half moves
                    for i in range(x):        #got to add half moves
                        moves_list.append("")
                        san_list.append("")        
            lalgmove = move.uci()
            moves_list.append(lalgmove)       #make a list of the game moves in long algebra e2e3 type
            if " b " in fen:
                black_move = True
                black_moves +=1
                if len(tempana_list) < 6:       #fill in spaces for the white moves as we are showing pairs of moves
                    wfen = fen              #since black is the first move save fen as wfen to be added later in this function
                    for i in range (6):
                        tempana_list.append("")
            else:
                black_move = False
                wfen = fen
                white_moves +=1
            sanmove = board.san(move)   #Actual move made in san 
            san_list.append(sanmove)       
            b_lalg, scores, moves = engine.getmoves(fen, self.depth, 5)     #fen depth multipv scores are a string
            #This is saved as part of ags file for use by continuation board limit bestmoves and scores to 3 for continue 
            b_lalg3, b_scores3 = self.bestlistslimit(b_lalg, scores)
            b_moves.append(b_lalg3)
            b_scores.append(b_scores3)
            fenlist.append(fen)                                    
            if len(moves) < 5:          #make sure there are always five
                for i in range(len(moves), 5):
                    moves.append("")       
            board.push(move)
            outstr = "Actual Move made was " + str(sanmove) + "         of " + str(self.totmoves) + " Moves in game " 
            self.p.term(outstr)
            if sanmove not in moves:    #list of moves does not contain actual move so get score of actual move that was already move push
                self.p.term("not in bestmoves")
                fen = board.fen()        
                _, sanscore, _ = engine.getmoves(fen, self.depth, 1)     #get score of actual move made
                moves.insert(0,sanmove)
                scores.insert(0,sanscore[0])
                place = len(moves)              
            else:           #actual move is in list of best moves
                place = moves.index(sanmove)+1
                moves.insert(0,sanmove)         #place actual move at the beginning
                scores.insert(0,scores[place-1])  #put the score from before at that place in 0 position for actual move score
                self.p.term("INNNNN bestmoves") 
            x = -1  
            for i in scores:
                x += 1
                try:
                    floatscore = float(i)
                except:
                    continue    #has mate in it so can't be made into a float
                scores.pop(x)           #remove string score since it can be a float
                scores.insert(x,floatscore)         
            if not type(scores[0]) is str and not type(scores[1]) is str:
                x = abs(scores[0] - scores[1])
                x = int(x*100)
                score_diff = x / 100     #get's a float round(a_float, 2)
            else:
                if type(scores[0]) is str and type(scores[1]) is float: #string mate and best is a value
                    score_diff = 5
                else:
                    score_diff = 0
            self.scores.append(scores)      #add list of scores to list of scores
            self.moveplace.append(place)    #add the place the the actual move came in  
            self.scorediff.append(score_diff)   #add the difference in scores of actual vs stockfish  
            if not black_move:
                try:
                    total_diff_white = round((total_diff_white + score_diff), 3)
                except:
                    pass        #a mate in x not a score                    
                total_Choice_white = total_Choice_white + place
                if white_moves < 11:        #get totals for first 10 moves
                    s_diffw = total_diff_white
                    s_choicew = total_Choice_white
                tempana_list.append(movenum)        #only add the movenumber on White move since only displayed once per row
                x, y = pyautogui.position()     #get mouse position and see if it is outside of the board area this will stop calculation
                #print (x, left, left+width)
                if x < 20 and y > 100:  #mouse stops stockfish to the left of the board
                    tempstr = "Stopping analysis calculation by mouse positioned on left side of screen "
                    self.maxcputemp = 1111       #set max cpu temp to 1111 telling calling routine this was aborted
                    logging.info(tempstr)
                    engine.engine.put('stop')     #tell stockfish to stop
                    engine.engine.get()  
                    engine.engine.terminate_engine()
                    messagebox.showinfo("Cancel Analysis", tempstr)                    
                    return
            tempana_list.append(moves[0])           #add actual move
            best_str = moves[1] + "   " + moves[2] + " " + moves[3] + " " + moves[4] + " " + moves[5]
            tempana_list.append(best_str)           #add best move
            tempana_list.append(score_diff)         #add score difference from best move
            tempana_list.append(place)              #add selected move place
            tempana_list.append(scores[0])          #add score as of this move
            if black_move:          #if black move then add white black move info to self.ana_list
                try:
                    total_diff_black = round((total_diff_black + score_diff), 3)
                except:
                    pass        #a mate in x not a score
                total_Choice_black = total_Choice_black + place
                if black_moves < 11:        #get totals for first 10 moves
                    s_diffb = total_diff_black
                    s_choiceb = total_Choice_black                
                tempana_list.append(wfen)        #add the fen from white move since we have it for each move combination
                self.ana_list.append(tempana_list)
                tempana_list = []               #reset tempana_list after updating after black move
                cputemp = get_cpu_temp()
                if cputemp > self.maxcputemp:
                    self.maxcputemp = cputemp       #set max cpu temp to highest
                temp = "After move temp CPU " + str(cputemp)
                self.p.term(temp, "blue")                
                while cputemp > 92:
                    print(temp)
                    temp = "Overtemp CPU " + str(cputemp) 
                    self.p.term(temp, "red")                                       
                    time.sleep(5)           
                    cputemp = get_cpu_temp() 
                if cputemp > 86 or cputemp < 30:        #less than 30 is for computers that don't give temp         
                    time.sleep(.3)      #short rest of cpu between moves
        #if game ended with white move then move needs to be added to self.ana_list as only appended after black move
        if len(tempana_list) == 6:              #only contains white move so add spaces for black and append to self.ana_list
            for i in range (6):
                tempana_list.append("")              
            self.ana_list.append(tempana_list)
        tempana_list = []       #clear list
        if white_moves < 11:
            s_divw = white_moves
            s_divb = black_moves
        else:
            s_divw = 10
            s_divb = 10        
        #set all of the labels
        self.data.lbldict["tdiffw"] = total_diff_white
        self.data.lbldict["tdiffb"] = total_diff_black
        #rounded_result = round(result, 3)
        self.data.lbldict["avdiffw"] = round((total_diff_white / white_moves), 3)
        self.data.lbldict["avdiffb"] = round((total_diff_black / black_moves), 3)         
        self.data.lbldict["avchoicew"] = round((total_Choice_white / white_moves), 3)
        self.data.lbldict["avchoiceb"] = round((total_Choice_black / black_moves), 3)
        self.data.lbldict["namew"] = self.white
        self.data.lbldict["nameb"] = self.black
        self.data.lbldict["result"] = self.result
        self.data.lbldict["depth"] = "d" + str(self.depth)
        self.data.lbldict["date"] = self.date
        self.data.lbldict["10diffw"] = s_diffw
        self.data.lbldict["10diffb"] = s_diffb
        self.data.lbldict["10avchoicew"] = round((s_choicew / s_divw), 3)
        self.data.lbldict["10avchoiceb"] = round((s_choiceb / s_divb), 3)
        self.data.lbldict["moves"] = white_moves
        #labellist = [total_diff_white, total_diff_black, avg_diff_white, avg_diff_black, avg_Choice_white, avg_Choice_black,
        # self.white, self.result, self.black, ddepth, self.date]
        #put temporary lists into the analyzed data object
        self.data.newlists(self.ana_list)
        self.data.newbestmoves(b_moves)
        self.data.newbestscores(b_scores)
        self.data.newfens(fenlist)
        self.data.newlongalg(moves_list)
        self.data.newsans(san_list)       
        engine.engine.terminate_engine()        #shut down engine started by bestmove               

class analyzed_data():

    def __init__(self):  
        self.list_oflists = []
        self.list_oflabels = []
        self.lbldict = {"tdiffw": "", "tdiffb": "", "avdiffw": "", "avdiffb": "",
                         "avchoicew": "", "avchoiceb": "", "namew": "", "result": "",
                         "nameb":"", "depth":"", "date":"", "10diffw":"", "10diffb":"",
                         "10avchoicew":"", "10avchoiceb":"", "moves":""}
        self.longalgmoves = []
        self.sanmoves = []
        self.bestmoves = []                          #list of lists containing three best moves (full alg) so far, will be "" "" "" for not analyzed
        self.bestscores = []                    #list of lists containing three bes scores
        self.fenlist = [] #list of lists, each sublist is string FEN of each move                 
        
    def newlists(self, nlist):
        if len(self.list_oflists) > 0:  #only one list of lists in object so replace if method called twice.  Creating the total list from temp lists
            self.list_oflists = []
        for i in nlist:
            self.list_oflists.append(i)

    def newlongalg(self, nlalg):
        if len(self.longalgmoves) > 0:  #only one list of lists in object so replace if method called twice
            self.longalgmoves = []
        for i in nlalg:
            self.longalgmoves.append(i)

    def newsans(self, nsan):
        if len(self.sanmoves) > 0:  #only one list of lists in object so replace if method called twice
            self.sanmoves = []
        for i in nsan:
            self.sanmoves.append(i)

    def newfens(self, flist):
        if len(self.fenlist) > 0:  #only one list of lists in object so replace if method called twice.  Creating the total list from temp lists
            self.fenlist = []
        for i in flist:
            self.fenlist.append(i)

    def newbestmoves(self, blalg):
        if len(self.bestmoves) > 0:  #only one list of lists in object so replace if method called twice
            self.bestmoves = []
        for i in blalg:
            self.bestmoves.append(i)

    def newbestscores(self, bscores):
        if len(self.bestscores) > 0:  #only one list of lists in object so replace if method called twice
            self.bestscores = []
        for i in bscores:
            self.bestscores.append(i)

    def add_dict(self,item):
        pass    #change label list to label dicts?  good idea?????
            
    def getlists(self):
        return self.list_oflists

    def getlongalg(self):
        return self.longalgmoves                    

    def getsans(self):
        return self.sanmoves  
        
    def getfens(self):
        return self.fenlist

    def getbestmoves(self):
        return self.bestmoves                    

    def getbestscores(self):
        return self.bestscores       

class bestmove():
#
# Creating a class that recieves a mainwindow reference, fen string, depth, and multipv (number of moves to return).
# Use Stockfish 17.1 for calculations in this case. Display the current depth and moves as stockfish calculates in toplevel window.
# Provide a way to abort calculation.
# Returns the number of moves (multipv) requested in order from highest score to lowest score.
# Return a list of two data item tuples.  Data items are move in algebraic notation and score of move in order of best to worst.
# If black is moving the lowest or most negative number is best.
#
    def __init__(self, p):#, fen, depth = 18, multipv = 4):
    #parent is the tk mainwindow this operates in, fen is chess position, depth is how deep for engine to analyze,
    # multipv is # of possible moves
        self.p = p
        self.engine = chess_engine(self.p)      #engine communication and initialization
 
    def getmoves(self, fen, searchdepth = 18, multipv = 5, timeout = 40):
        if multipv > 5:
            multipv = 5           
        if searchdepth > 22:        #for high depth limit multipv to 1
            multipv = 3
        outstr = "multipv set to " + str(multipv)
        self.p.term(outstr)    
        mv_cont = []    #list for moves
        scores = []     #list of the scores for moves
        moves = []      #list of moves
        sanmoves = []
        moves.clear()
        scores.clear()        
        for x in range(multipv):
            mv_cont.append("")
            scores.append("")
            moves.append("")
            sanmoves.append("")
        pvcount = 0
        board = chess.Board(fen)
        pvoption = 'setoption name MultiPV value ' + str(multipv)
        self.engine.put(pvoption)       #set multipv
        self.engine.get()  
        self.engine.put('ucinewgame')
        self.engine.get()
        self.engine.put('isready')
        self.engine.get()
        fencommand = "position fen " + fen
        self.engine.put(fencommand)
        self.engine.get()
        command = "go depth " + str(searchdepth)
        self.engine.put(command)
        depth = 0     
        start = time.time()          
        calculating = True
        sanmove = ""
        while calculating:
            stream = self.engine.comm.stdout.readline().strip()  #stdout.readline().strip()
            start2 = time.time()
            start3 = int(round(start2 - start, 2))            
            if start3 > timeout:            #if timeout has been reached then end now
                calculating = False 
                pstring = str(depth)  
                pstring = pstring + " Timout was reached in getmoves"
                logging.info(pstring)                
            if "multipv" in stream:          
                left, temp, conmoves = stream.rpartition(" pv ")   #separate at pv as move is to the right of it left will be further handled
                smove, mid , temp = conmoves.partition(" ")     #first string is move   4 maybe 5 chars
                left, mid, right = left.partition(" nodes ")
                movelist = left.split(" ")  #left side of stockfish output with depth pv info
                depth = int(movelist[2])
                pv = int(movelist[6])
                if pv > pvcount: pvcount +=1     #keep track of possible moves being sent
                pv -=1      #offset for range starting with 0
                mv_cont.pop(pv)
                mv_cont.insert(pv, conmoves)
                #self.p.term ("\n",mv_cont[pv],"  ", "moves ", pv)
                temp = movelist[8]
                if temp == "mate":
                    if not "w" in fen:   #if black mate in minus moves
                        mate = "mate -" + movelist[9]
                    else:
                        mate = "mate  " + movelist[9]
                    scores.pop (pv)
                    scores.insert(pv, mate)
                    newstr = mate
                else:
                    x = int(movelist[9])
                    if not "w" in fen:
                        x = x * -1      #change integer by inverting sign to keep whites perspective so
                                        # a negative score always means black is winning and positive white is winning
                    z = x / 100     #get's a float round(a_float, 2)   
                    newstr = str(z)
                    scores.pop(pv)
                    scores.insert(pv, newstr)#newstr)
                move = chess.Move.from_uci(smove)    #needed to get san move from chess
                sanmove = board.san(move)
                moves.pop(pv)    
                moves.insert(pv, smove) 
                sanmoves.pop(pv)
                sanmoves.insert(pv,sanmove)             
            else:   #stream no longer has multipv
                outstr = "** " + stream          
                if "bestmove" in stream:        #bestmove sent at end of calculating
                    calculating = False
                    pstring = str(depth)
                    for i in range(len(scores)):
                        pstring = pstring + sanmoves[i] + "  " + str(scores[i])
                        self.p.term (pstring)
        return moves, scores, sanmoves
        
#end of bestmove class

class chess_engine():

    def __init__(self, p):    
        self.p = p      #to output to stockfish output window tkwoterm  
        self.uci_check = False

        stockfish_location = os.getcwd() + "/libs/stockfish17_1/stockfish17.1-popcnt"
        self.p.term(stockfish_location)
        self.comm = subprocess.Popen(
            stockfish_location,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,
        ) 
           
        self.get()
        self.put('uci')      #initialize stockfish
        self.get()
        if not self.uci_check:       #if no uciok was recieved then abort engine as this is a problem
            self.p.term("Did not receive uciok !!!!!") 
            self.put('quit')
            logging.error("Did not receive uciok !!!!!")            
            return   
        self.put('setoption name Threads value 4')       #set threads to 4 or 8
        self.get()
        self.put('setoption name Hash value 1024')  #set hash value size
        self.get()
        pvoption = 'setoption name MultiPV value ' + str(4)#self.multipv)
        self.put(pvoption)       #set multipv defaults to 4        
        self.get()
        self.put ('setoption name UCI_AnalyseMode value True')      #set to analyze mode
        self.get()
        
    def put(self, command):     #put to communicate with chess engine
        if "fen" in command:
            self.p.term('\nyou:\n\t'+command)
            logging.info(command)
        try:
            self.comm.stdin.write(command+'\n')
            self.comm.stdin.flush()  # Forces the write to occur immediately to test the pipe
        except BrokenPipeError:
            logging.error("Broken Pipe")
            print("The subprocess closed the input pipe.")
            self.p.term("The subprocess closed the input pipe after this command.")
            self.p.term(command)  
    #end put function
        
    def get(self):
        # using the 'isready' command (engine has to answer 'readyok')
        # to indicate current last line of stdout
        self.comm.stdin.write('isready\n')
        #self.p.term('\nengine:')
        while True:
            text = self.comm.stdout.readline().strip()
            if text == 'readyok':
                #self.p.term ('readyok')
                break
            if text !='':
                self.p.term('\t'+text)
                if text == "uciok":
                    self.uci_check = True
                    self.p.term("Received uciok")                
    # end get function 
           
    def terminate_engine(self):
        self.put('quit')
        # Assuming your pipe is named 'self.comm'
        self.comm.stdin.write('quit\n')
        self.comm.stdin.flush()  # Make sure the command is sent
        self.comm.stdout.close()
        self.comm.stdin.close()
        self.comm.wait()         # Safely terminates the process            
        
def get_cpu_temp():
    # Fetch all hardware temperature sensors return highest       
    temps = psutil.sensors_temperatures()
    if temps:    
        # Extract all "coretemp" or similar entries, grabbing the current temperature from each
        core_temps = [entry.current for key in temps for entry in temps[key] if "core" in key.lower() or "core" in entry.label.lower()]    
        if core_temps:
            max_core_temp = max(core_temps)        
        else:
            max_core_temp = 1    
        return max_core_temp
    else:
        return 1 
