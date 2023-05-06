import tkinter as tk
from tkinter import filedialog
import os

def select_pdf():
    root = tk.Tk()
    root.withdraw()
    # Allow the user to select a file or folder
    # Allow the user to select a folder or individual PDF files
    selected_path = filedialog.askdirectory(initialdir='/', title='Select PDF Files or Folder')

    if selected_path:
        if os.path.isdir(selected_path):
            folder_path = selected_path
            pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
            selected_files = [os.path.join(folder_path, f) for f in pdf_files]
            return selected_files
        else:
            selected_files = [selected_path]
            return selected_files
    else:
        print("No files or folder selected.")
        return []

