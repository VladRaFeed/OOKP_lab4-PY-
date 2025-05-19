import socket
import threading
import pickle

user_notes = {}

MAX_NOTES = 5

def handle_client(conn, addr):
    print(f"[З'єднано] Клієнт {addr}")
    ip = addr[0]
    user_notes.setdefault(ip, [])

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            request = pickle.loads(data)

            match request["action"]:
                case "ADD":
                    if len(user_notes[ip]) >= MAX_NOTES:
                        response = "Нотатки заповнені. Видаліть одну, щоб додати нову."
                    else:
                        user_notes[ip].append(request["note"])
                        response = "Нотатку додано."
                case "VIEW":
                    response = user_notes[ip]
                case "DELETE":
                    index = request["index"]
                    if 0 <= index < len(user_notes[ip]):
                        del user_notes[ip][index]
                        response = "Нотатку видалено."
                    else:
                        response = "Некоректний індекс."
                case "DELETE_ALL":
                    user_notes[ip] = []
                    response = "Усі нотатки видалено."
                case "EXIT":
                    break
                case _:
                    response = "Невідома команда."

            conn.send(pickle.dumps(response))
    except Exception as e:
        print(f"[Помилка] {e}")
    finally:
        conn.close()
        print(f"[Відключено] Клієнт {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8888))
    server.listen(5)
    print("[Сервер запущено] Очікування підключень...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
