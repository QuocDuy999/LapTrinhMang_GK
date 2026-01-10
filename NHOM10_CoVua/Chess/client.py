import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import chess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

HOST = '127.0.0.1'
PORT = 5555
TILE_SIZE = 60
PIECES = {}

def load_piece_images():
    piece_map = {
        'P': 'white_tot', 'N': 'white_ngua', 'B': 'white_tuong',
        'R': 'white_xe', 'Q': 'white_queen', 'K': 'white_king',
        'p': 'black_tot', 'n': 'black_ngua', 'b': 'black_tuong',
        'r': 'black_xe', 'q': 'black_queen', 'k': 'black_king'
    }
    for symbol, filename in piece_map.items():
        try:
            path = os.path.join(ASSETS_DIR, f"{filename}.png")
            img = Image.open(path)
            img = img.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
            PIECES[symbol] = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"⚠️ Lỗi load {filename}: {e}")

