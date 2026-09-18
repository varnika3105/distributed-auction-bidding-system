import socket
import threading
import tkinter as tk
import time
import winsound

HOST = "0.0.0.0"
PORT = 5000

highest_bid = 0
highest_bidder = "None"
clients = []
lock = threading.Lock()

auction_running = False
timer_running = False
server_started = False

time_left = 0
last_bid_time = time.time()
inactivity_limit = 10

bid_history = []

def safe_ui(func):
    root.after(0, func)

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            clients.remove(client)

def update_client_count():
    safe_ui(lambda: client_count_label.config(text=f"Clients: {len(clients)}"))

def update_gui():
    def update():
        highest_label.config(text=f"₹{highest_bid}")
        bidder_label.config(text=highest_bidder)

        history_box.delete(0, tk.END)
        for entry in bid_history:
            history_box.insert(tk.END, entry)

    safe_ui(update)

def handle_client(conn, addr):
    global highest_bid, highest_bidder, last_bid_time

    clients.append(conn)
    update_client_count()

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            name, bid = data.split(":")
            bid = int(bid)

            lock.acquire()

            if not auction_running:
                conn.send("Auction is closed!".encode())

            elif bid > highest_bid:
                highest_bid = bid
                highest_bidder = name

                bid_history.append(f"{name} → ₹{bid}")
                update_gui()

                last_bid_time = time.time()  # reset inactivity

                winsound.Beep(1000, 200)

                broadcast(f"New Highest Bid: ₹{highest_bid} by {highest_bidder}")
                conn.send("Bid Accepted".encode())

            else:
                conn.send("Bid too low!".encode())

            lock.release()

        except:
            break

    conn.close()
    if conn in clients:
        clients.remove(conn)
    update_client_count()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    safe_ui(lambda: status_label.config(text="Server Running", fg="#00C853"))

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def start_server_once():
    global server_started
    if not server_started:
        server_started = True
        threading.Thread(target=start_server).start()

def run_timer():
    global time_left, auction_running, timer_running

    timer_running = True

    while auction_running:
        safe_ui(lambda t=time_left: timer_label.config(text=f"{t}s"))

        if time_left > 0:
            time_left -= 1

        
        if time.time() - last_bid_time > inactivity_limit:
            break

        time.sleep(1)

    if auction_running and highest_bidder != "None":
        winner_msg = f"⏳ Auction ended!\n🏆 Winner: {highest_bidder} (₹{highest_bid})"
        safe_ui(lambda: status_label.config(text=winner_msg, fg="#2979FF"))
        broadcast(winner_msg)

    auction_running = False
    timer_running = False
    safe_ui(lambda: timer_label.config(text="0s"))

def start_auction():
    global auction_running, time_left, last_bid_time, inactivity_limit

    duration = duration_entry.get().strip()
    inactivity = inactivity_entry.get().strip()

    if not duration.isdigit() or not inactivity.isdigit():
        status_label.config(text="Enter valid numbers!", fg="red")
        return

    if not timer_running:
        time_left = int(duration)
        inactivity_limit = int(inactivity)
        auction_running = True
        last_bid_time = time.time()

        safe_ui(lambda: inactivity_label.config(text=f"Inactivity: {inactivity_limit}s"))

        status_label.config(text="Auction Running", fg="#00C853")
        broadcast("Auction Started!")

        threading.Thread(target=run_timer).start()

def stop_auction():
    global auction_running
    auction_running = False
    status_label.config(text="Auction Stopped", fg="red")
    broadcast("Auction Stopped!")

def reset_auction():
    global highest_bid, highest_bidder, bid_history

    highest_bid = 0
    highest_bidder = "None"
    bid_history.clear()

    update_gui()
    status_label.config(text="Auction Reset", fg="#FF6D00")

root = tk.Tk()
root.title("Auction Server")
root.geometry("520x580")
root.configure(bg="#121212")

tk.Label(root, text="Auction Server", font=("Segoe UI", 20, "bold"),
         bg="#121212", fg="white").pack(pady=10)

frame_top = tk.Frame(root, bg="#1E1E1E", padx=10, pady=10)
frame_top.pack(padx=15, pady=10, fill="x")

tk.Label(frame_top, text="Highest Bid", fg="gray", bg="#1E1E1E").grid(row=0, column=0)
highest_label = tk.Label(frame_top, text="₹0", font=("Segoe UI", 16, "bold"),
                         fg="#00E676", bg="#1E1E1E")
highest_label.grid(row=1, column=0)

tk.Label(frame_top, text="Highest Bidder", fg="gray", bg="#1E1E1E").grid(row=0, column=1)
bidder_label = tk.Label(frame_top, text="None", font=("Segoe UI", 16, "bold"),
                        fg="#40C4FF", bg="#1E1E1E")
bidder_label.grid(row=1, column=1)

status_label = tk.Label(root, text="Server Stopped", fg="red", bg="#121212")
status_label.pack()

info_frame = tk.Frame(root, bg="#121212")
info_frame.pack()

client_count_label = tk.Label(info_frame, text="Clients: 0", fg="white", bg="#121212")
client_count_label.grid(row=0, column=0, padx=10)

timer_label = tk.Label(info_frame, text="0s", fg="white", bg="#121212")
timer_label.grid(row=0, column=1, padx=10)

inactivity_label = tk.Label(info_frame, text="Inactivity: 0s", fg="white", bg="#121212")
inactivity_label.grid(row=0, column=2, padx=10)

frame_controls = tk.Frame(root, bg="#1E1E1E", padx=10, pady=10)
frame_controls.pack(padx=15, pady=10, fill="x")

tk.Label(frame_controls, text="Auction Duration (sec)", bg="#1E1E1E", fg="white").pack()
duration_entry = tk.Entry(frame_controls)
duration_entry.pack(pady=5)

tk.Label(frame_controls, text="Inactivity Timeout (sec)", bg="#1E1E1E", fg="white").pack()
inactivity_entry = tk.Entry(frame_controls)
inactivity_entry.pack(pady=5)

tk.Button(frame_controls, text="Start Server", bg="#00C853", fg="white",
          command=start_server_once).pack(fill="x", pady=2)

tk.Button(frame_controls, text="Start Auction", bg="#2962FF", fg="white",
          command=start_auction).pack(fill="x", pady=2)

tk.Button(frame_controls, text="Stop Auction", bg="#D50000", fg="white",
          command=stop_auction).pack(fill="x", pady=2)

tk.Button(frame_controls, text="Reset Auction", bg="#FF6D00", fg="white",
          command=reset_auction).pack(fill="x", pady=2)

tk.Label(root, text="Bid History", fg="white", bg="#121212").pack()

history_box = tk.Listbox(root, height=12, bg="#1E1E1E", fg="white")
history_box.pack(padx=15, pady=10, fill="both", expand=True)

root.mainloop()