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

    def on_click(self, event):

        if self.client_color is None:
            return
        if (self.board.turn == chess.WHITE and self.client_color != "white") or \
           (self.board.turn == chess.BLACK and self.client_color != "black"):
            return

        col = event.x // TILE_SIZE
        row = 7 - (event.y // TILE_SIZE)
        sq = chess.square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(sq)
            if piece and ((piece.color == chess.WHITE and self.client_color == "white") or
                          (piece.color == chess.BLACK and self.client_color == "black")):
                self.selected_square = sq
                self.valid_moves = set(move.to_square for move in self.board.legal_moves if move.from_square == sq)
                self.draw_board()
        else:
            if sq != self.selected_square:
                move = chess.Move(self.selected_square, sq)
                if move in self.board.legal_moves:
                    try:
                        self.sock.sendall(json.dumps({"action": "move", "move": move.uci()}).encode())
                    except Exception as e:
                        messagebox.showerror("Error", f"Lost connection: {e}")
                else:
                    print("Nước đi không hợp lệ:", move.uci())
            self.selected_square = None
            self.valid_moves = set()
            self.draw_board()

    def listen_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = json.loads(data.decode())
                if msg.get("action") == "move":
                    if len(self.board.move_stack) > 0:
                        print(f"Đã đi: {self.board.peek().uci()} - lượt tiếp theo: {msg['turn']}")
                    else:
                        print(f"Lượt tiếp theo: {msg['turn']}")
                if msg.get("action") == "start":
                    self.client_color = msg["color"]
                    self.board.set_fen(msg["fen"])
                    self.draw_board()
                elif msg.get("action") == "move":
                    self.board.set_fen(msg["fen"])
                    self.draw_board()
                elif msg.get("action") == "end":
                    self.board.set_fen(msg["fen"])
                    self.draw_board()
                    messagebox.showinfo("Game Over", msg["result"])
                    self.canvas.unbind("<Button-1>")
            except Exception as e:
                print(f"Lỗi khi nhận dữ liệu từ server: {e}")
                break
        messagebox.showerror("Error", "Disconnected from server")
        self.root.quit()

if __name__ == "__main__":
    ChessClient()


