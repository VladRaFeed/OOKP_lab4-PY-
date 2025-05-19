import socket
import pickle
import tkinter as tk
from tkinter import messagebox, simpledialog

class NoteClient:
    def __init__(self, master):
        self.master = master
        master.title("Нотатки")

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect(('localhost', 8888))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося підключитися: {e}")
            master.destroy()
            return

        # Інтерфейс
        self.listbox = tk.Listbox(master, width=40, height=10)
        self.listbox.pack(pady=5)

        self.refresh_button = tk.Button(master, text="Оновити", command=self.view_notes)
        self.refresh_button.pack(pady=2)

        self.add_button = tk.Button(master, text="Додати нотатку", command=self.add_note)
        self.add_button.pack(pady=2)

        self.delete_button = tk.Button(master, text="Видалити вибрану", command=self.delete_note)
        self.delete_button.pack(pady=2)

        self.delete_all_button = tk.Button(master, text="Очистити всі", command=self.delete_all)
        self.delete_all_button.pack(pady=2)

        self.exit_button = tk.Button(master, text="Вийти", command=self.exit_app)
        self.exit_button.pack(pady=5)

        self.view_notes()

    def send_request(self, request):
        try:
            self.conn.send(pickle.dumps(request))
            response = self.conn.recv(4096)
            return pickle.loads(response)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка з'єднання: {e}")
            self.master.destroy()

    def view_notes(self):
        response = self.send_request({"action": "VIEW"})
        self.listbox.delete(0, tk.END)
        for i, note in enumerate(response):
            self.listbox.insert(tk.END, f"{i+1}. {note}")

    def add_note(self):
        note = simpledialog.askstring("Нотатка", "Введіть текст нотатки:")
        if note:
            response = self.send_request({"action": "ADD", "note": note})
            messagebox.showinfo("Результат", response)
            self.view_notes()

    def delete_note(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            response = self.send_request({"action": "DELETE", "index": index})
            messagebox.showinfo("Результат", response)
            self.view_notes()
        else:
            messagebox.showwarning("Увага", "Виберіть нотатку для видалення.")

    def delete_all(self):
        if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити всі нотатки?"):
            response = self.send_request({"action": "DELETE_ALL"})
            messagebox.showinfo("Результат", response)
            self.view_notes()

    def exit_app(self):
        self.send_request({"action": "EXIT"})
        self.conn.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteClient(root)
    root.mainloop()
