import socket
import threading
import pickle

user_notes = {}
MAX_NOTES = 5
server_running = True

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

def console_listener(server_socket):
    global server_running
    while server_running:
        command = input()
        if command.strip().lower() == "stop":
            print("[Завершення] Сервер завершує роботу...")
            server_running = False
            try:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('localhost', 8888))
            except:
                pass
            server_socket.close()
            break

def start_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8888))
    server.listen(5)
    print("[Сервер запущено] Введіть 'stop' щоб завершити роботу.")

    threading.Thread(target=console_listener, args=(server,), daemon=True).start()

    while server_running:
        try:
            conn, addr = server.accept()
        except OSError:
            break  # сервер закрито
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

    print("[Сервер завершено]")

if __name__ == "__main__":
    start_server()
