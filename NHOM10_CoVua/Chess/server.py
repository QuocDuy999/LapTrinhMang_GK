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

def handle_client(conn, addr):
    print(f"New connection: {addr}")
    with lock:
        waiting_players.append(conn)

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            msg = json.loads(data.decode())
            if msg.get("action") == "move":
                game_id = None
                with lock:
                    for gid, g in games.items():
                        if conn in g['players']:
                            game_id = gid
                            break
                color = games[game_id]['colors'].get(conn, "unknown") if game_id else "unknown"
                print(f"Người chơi {color} vừa đi: {msg['move']}")
            else:
                print(f"Nhận từ {addr}: {msg}")

            if msg.get('action') == 'move':
                game_id = None
                with lock:
                    for gid, g in games.items():
                        if conn in g['players']:
                            game_id = gid
                            break
                if game_id is None:
                    continue

                game = games[game_id]
                board = game['board']
                move = chess.Move.from_uci(msg['move'])

                if move in board.legal_moves:
                    board.push(move)
                    game['turn'] = [p for p in game['players'] if p != conn][0]

                    if board.is_checkmate():
                        winner = "white" if board.turn == chess.BLACK else "black"
                        broadcast(game_id, {
                            "action": "end",
                            "result": f"{winner} wins by checkmate",
                            "fen": board.fen()
                        })
                    elif board.is_stalemate():
                        broadcast(game_id, {
                            "action": "end",
                            "result": "Draw by stalemate",
                            "fen": board.fen()
                        })
                    elif board.is_insufficient_material():
                        broadcast(game_id, {
                            "action": "end",
                            "result": "Draw by insufficient material",
                            "fen": board.fen()
                        })
                    else:
                        broadcast(game_id, {
                            "action": "move",
                            "fen": board.fen(),
                            "turn": "white" if board.turn == chess.WHITE else "black"
                        })
                else:
                    try:
                        conn.sendall(json.dumps({
                            "action": "invalid",
                            "reason": "Move is not legal"
                        }).encode())
                    except Exception as e:
                        print(f"Lỗi gửi phản hồi invalid: {e}")
        except Exception as e:
            print(f"Lỗi nhận dữ liệu từ {addr}: {e}")
            break

    with lock:
        if conn in waiting_players:
            waiting_players.remove(conn)
        for gid, g in games.items():
            if conn in g['players']:
                g['players'].remove(conn)
                print(f"{addr} rời game {gid}")
    conn.close()
    print(f"Connection closed: {addr}")

def start_server():
    print(f"Chess server started on {HOST}:{PORT}")
    threading.Thread(target=match_players, daemon=True).start()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()