import os
import subprocess

import tkinter as tk

from tkinter import ttk, filedialog
from sorter import Sorter

'''
This is the main window of picture_sort
'''
class MainWindow(tk.Tk):
    # Constructor
    def __init__(self):
        super().__init__()
        self.title("Sort my Media")
        self.geometry("500x450")

        wd_style = ttk.Style()
        wd_style.theme_use("clam")  # Alternativen: 'default', 'alt', 'classic', 'clam'

        # current working directory
        self.current_dir = os.getcwd()

        # Source Directory 
        frame_srcdir = ttk.LabelFrame(self, text="Source Directory")
        frame_srcdir.pack(fill="x", padx=10, pady=5)
        # Variable
        self.var_scrdir = tk.StringVar()
        entry_scrdir = ttk.Entry(frame_srcdir, textvariable=self.var_scrdir, width=40)
        entry_scrdir.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        btn_scrdir = ttk.Button(frame_srcdir, text="Browse...", command=self.browse_src)
        btn_scrdir.pack(side="left", padx=5, pady=5)

        # Radiobutton Group Months
        frame_month = ttk.LabelFrame(self, text="Name of month directorys")
        frame_month.pack(fill="x", padx=10, pady=5)
        # Variable
        self.var_month = tk.BooleanVar(value=False)
        ttk.Radiobutton(frame_month, text="Numbers", variable=self.var_month, value=False).pack(side="left", padx=5, pady=5)
        ttk.Radiobutton(frame_month, text="Names", variable=self.var_month, value=True).pack(side="left", padx=5, pady=5)

        # Radiobutton Group Copy or Move
        frame_cp_mv = ttk.LabelFrame(self, text="Copy or Move")
        frame_cp_mv.pack(fill="x", padx=10, pady=5)
        # Variable
        self.var_cpmv = tk.BooleanVar(value=True)
        ttk.Radiobutton(frame_cp_mv, text="Copy", variable=self.var_cpmv, value=True).pack(side="left", padx=5, pady=5)
        ttk.Radiobutton(frame_cp_mv, text="Move", variable=self.var_cpmv, value=False).pack(side="left", padx=5, pady=5)

        # Checkboxes
        checkbox_frame = ttk.LabelFrame(self, text="Other Options")
        checkbox_frame.pack(fill="x", padx=10, pady=5)
        # Variable
        self.var_logfile = tk.BooleanVar()
        ttk.Checkbutton(checkbox_frame, text="Create Logfile", variable=self.var_logfile).pack(side="left", padx=5, pady=5)

        # Destination Directory 
        frame_destdir = ttk.LabelFrame(self, text="Destination Directory")
        frame_destdir.pack(fill="x", padx=10, pady=5)
        # Variable
        self.var_destdir = tk.StringVar()
        entry_destdir = ttk.Entry(frame_destdir, textvariable=self.var_destdir, width=40)
        entry_destdir.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        btn_destdir = ttk.Button(frame_destdir, text="Browse...", command=self.browse_dest)
        btn_destdir.pack(side="left", padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        btn_start = ttk.Button(button_frame, text="Start", command=self.on_start)
        btn_start.pack(side="left", padx=5, pady=5)
        btn_quit = ttk.Button(button_frame, text="Quit", command=self.on_cancel)
        btn_quit.pack(side="left", padx=5, pady=5)

    # Browse the source directory
    def browse_src(self):
        path = filedialog.askdirectory(initialdir=self.current_dir)
        if path:
            self.var_scrdir.set(path)

    # Browse the destination directory
    def browse_dest(self):
        path = filedialog.askdirectory(initialdir=self.current_dir)
        if path:
            self.var_destdir.set(path)

    # Count all files in a directory (and subdirectories)
    def __count_files(self, path):
        cmd = f"find {path} -type f | wc -l"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        return int(result.stdout.strip())

    # Start the sort run
    def on_start(self):

        sort = Sorter(
            src_dir=self.var_scrdir.get(),
            dest_dir=self.var_destdir.get(),
            copy=self.var_cpmv.get(),
            months=self.var_month.get(),
            logfile=self.var_logfile.get()
        )
        # Number of files in source dir
        files_src = self.__count_files(self.var_scrdir.get())
        # Sort media files
        sort.sort_media()
        
        sort.append_notsupported(f"--- Number of files in source directory: {files_src} ---")
        # Number of files in dest dir
        files_dest = self.__count_files(self.var_destdir.get())
        sort.append_notsupported(f"--- Number of files in destination directory: {files_dest} ---")
        diff_sort = files_src - files_dest
        sort.append_notsupported(f"--- Number of not supported files should be: {files_src - files_dest} ---")

        if sort.not_supported - diff_sort == 0:
            sort.append_notsupported("--- Operation successful: all files moved/copied. ---")
        else:
            sort.append_notsupported("--- Operation finished with errors. Please review the log. ---")

        sort.append_notsupported(f"--- End of sorting ---")

        # Show messagesbox
        if self.var_cpmv.get():
            tk.messagebox.showinfo("Success - Copy", f"Your media has been copied and sorted successfully.\nSource: {files_src} files \nDestination: {files_dest} files")
        else:
            tk.messagebox.showinfo("Success - Move", f"Your media has been moved and sorted successfully.\nSource: {files_src} files \nDestination: {files_dest} files")
    
    # Exit picture_sort
    def on_cancel(self):
        self.destroy()