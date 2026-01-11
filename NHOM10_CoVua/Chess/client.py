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
class ChessClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Online Chess")
        self.canvas = tk.Canvas(self.root, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.canvas.pack()

        self.board = chess.Board()
        self.selected_square = None
        self.client_color = None
        self.valid_moves = set()

        load_piece_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
        except:
            messagebox.showerror("Error", "Cannot connect to server")
            self.root.destroy()
            return

        threading.Thread(target=self.listen_server, daemon=True).start()
        self.root.mainloop()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#F0D9B5", "#655548"]
        for r in range(8):
            for c in range(8):
                x0, y0 = c*TILE_SIZE, r*TILE_SIZE
                x1, y1 = x0+TILE_SIZE, y0+TILE_SIZE
                sq = chess.square(c, 7-r)
                color = colors[(r+c)%2]

                if sq in self.valid_moves:
                    color = "#88FF88"

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                piece = self.board.piece_at(sq)
                if piece:
                    self.canvas.create_image(x0, y0, image=PIECES[piece.symbol()], anchor="nw")

