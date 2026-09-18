import socket
import threading
import tkinter as tk
from tkinter import messagebox

SERVER_IP = "127.0.0.1"  
PORT = 5000

def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode()
            status_label.config(text=msg)
        except:
            break

def place_bid():
    name = name_entry.get().strip()
    bid = bid_entry.get().strip()

    if name == "" or bid == "":
        messagebox.showerror("Error", "All fields required")
        return

    if not bid.isdigit():
        messagebox.showerror("Error", "Bid must be number")
        return

    client.send(f"{name}:{bid}".encode())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

root = tk.Tk()
root.title("Auction Client")
root.geometry("350x400")
root.configure(bg="#121212")

tk.Label(root, text="Place Your Bid", font=("Segoe UI", 18, "bold"),
         bg="#121212", fg="white").pack(pady=15)

frame = tk.Frame(root, bg="#1E1E1E", padx=10, pady=10)
frame.pack(padx=20, pady=10, fill="x")

tk.Label(frame, text="Name", bg="#1E1E1E", fg="white").pack(anchor="w")
name_entry = tk.Entry(frame)
name_entry.pack(fill="x", pady=5)

tk.Label(frame, text="Bid (₹)", bg="#1E1E1E", fg="white").pack(anchor="w")
bid_entry = tk.Entry(frame)
bid_entry.pack(fill="x", pady=5)

tk.Button(frame, text="Place Bid", bg="#2962FF", fg="white",
          command=place_bid).pack(fill="x", pady=10)

status_label = tk.Label(root, text="Connected", fg="#00E676", bg="#121212")
status_label.pack(pady=10)

threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()