import socket
import threading
import json
import chess
import time

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

waiting_players = []
games = {}
game_id_counter = 1
lock = threading.Lock()

def broadcast(game_id, data):
    if game_id not in games:
        return
    for conn in games[game_id]['players'][:]:
        try:
            conn.sendall(json.dumps(data).encode())
        except Exception as e:
            print(f"Lỗi gửi dữ liệu: {e}")
            games[game_id]['players'].remove(conn)

def match_players():
    global game_id_counter
    while True:
        with lock:
            if len(waiting_players) >= 2:
                p1 = waiting_players.pop(0)
                p2 = waiting_players.pop(0)
                gid = game_id_counter
                game_id_counter += 1
                board = chess.Board()
                games[gid] = {
                    'board': board,
                    'players': [p1, p2],
                    'colors': {p1: 'white', p2: 'black'},
                    'turn': p1
                }
                try:
                    p1.sendall(json.dumps({
                        "action": "start",
                        "color": "white",
                        "fen": board.fen(),
                        "turn": "white"
                    }).encode())
                    p2.sendall(json.dumps({
                        "action": "start",
                        "color": "black",
                        "fen": board.fen(),
                        "turn": "white"
                    }).encode())
                    print(f"Game {gid} bắt đầu")
                except Exception as e:
                    print(f"Lỗi khi gửi thông tin bắt đầu: {e}")
        time.sleep(0.5)

