import socket
import pickle
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class NoteClient:
    def __init__(self, master):
        self.master = master
        master.title("Нотатки")
        master.geometry("800x800")
        master.configure(bg="#f0f4f8")

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect(('localhost', 8888))
        except Exception as e:
            messagebox.showerror("Помилка підключення", f"Не вдалося підключитися до сервера:\n{e}")
            master.destroy()
            return

        # Заголовок
        title_label = tk.Label(master, text="Мої нотатки", font=("Arial", 24, "bold"), bg="#f0f4f8", fg="#333")
        title_label.pack(pady=20)

        # Рамка для списку нотаток
        self.list_frame = tk.Frame(master, bg="#f0f4f8")
        self.list_frame.pack(pady=10)

        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            self.list_frame, width=70, height=20, font=("Arial", 12),
            yscrollcommand=self.scrollbar.set, bg="white", fg="#333", bd=2, relief="groove", selectbackground="#cce5ff"
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar.config(command=self.listbox.yview)

        # Рамка для кнопок
        self.button_frame = tk.Frame(master, bg="#f0f4f8")
        self.button_frame.pack(pady=20)

        self.add_button = tk.Button(self.button_frame, text="➕ Додати нотатку", command=self.add_note, width=20, bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised")
        self.add_button.grid(row=0, column=0, padx=10, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="❌ Видалити вибрану", command=self.delete_note, width=20, bg="#f44336", fg="white", font=("Arial", 12), relief="raised")
        self.delete_button.grid(row=0, column=1, padx=10, pady=5)

        self.delete_all_button = tk.Button(self.button_frame, text="🧹 Очистити всі", command=self.delete_all, width=20, bg="#ff9800", fg="white", font=("Arial", 12), relief="raised")
        self.delete_all_button.grid(row=1, column=0, padx=10, pady=5)

        self.refresh_button = tk.Button(self.button_frame, text="🔄 Оновити", command=self.view_notes, width=20, bg="#2196F3", fg="white", font=("Arial", 12), relief="raised")
        self.refresh_button.grid(row=1, column=1, padx=10, pady=5)

        self.exit_button = tk.Button(master, text="🚪 Вийти", command=self.exit_app, width=25, bg="#9c27b0", fg="white", font=("Arial", 12), relief="raised")
        self.exit_button.pack(pady=10)

        self.view_notes()

    def send_request(self, request):
        try:
            self.conn.send(pickle.dumps(request))
            response = self.conn.recv(4096)
            return pickle.loads(response)
        except Exception as e:
            messagebox.showerror("Помилка з'єднання", f"Втрачено зв'язок із сервером:\n{e}")
            self.master.destroy()

    def view_notes(self):
        response = self.send_request({"action": "VIEW"})
        self.listbox.delete(0, tk.END)
        if response:
            for i, note in enumerate(response):
                self.listbox.insert(tk.END, f"{i+1}. {note}")
        else:
            self.listbox.insert(tk.END, "Нотатки відсутні. Додайте першу!")

    def add_note(self):
        note = simpledialog.askstring("Нова нотатка", "Введіть текст нотатки:", parent=self.master)
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
            messagebox.showwarning("Увага", "Спочатку виберіть нотатку для видалення.")

    def delete_all(self):
        if messagebox.askyesno("Підтвердження", "Ви дійсно хочете видалити всі нотатки?"):
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
