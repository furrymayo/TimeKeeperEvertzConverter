import tkinter as tk
from tkinter import scrolledtext
import socket
import time  # Importing time for the delay

# Constants for VGPI formatting
VGPI_ON = "1"
VGPI_OFF = "0"  # New constant for OFF status

def format_vgpi_data(virt_gpi_num, status):
    return f"%16S{virt_gpi_num}={status}%Z"

def send_vgpi_to_endpoint(vgpi_id, status, reset=False):
    data = format_vgpi_data(vgpi_id, status)
    endpoints = list(endpoints_listbox.get(0, tk.END))
    for endpoint in endpoints:
        try:
            # Parse the endpoint to extract host and port
            host, port = endpoint.replace("http://", "").split(":")
            port = int(port)

            # Create a TCP socket and connect to the endpoint
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(data.encode('ASCII'))

            output_text.insert(tk.END, f"Sent data: {data} to {endpoint}\n")
        except Exception as e:
            output_text.insert(tk.END, f"Failed to send data to {endpoint}. Error: {e}\n")
    output_text.see(tk.END)

    # If reset is True, send a reset command after a short delay
    if reset:
        time.sleep(0.5)  # Delay for half a second
        send_vgpi_to_endpoint(vgpi_id, VGPI_OFF)

def start_pushing():
    vgpi_id = int(start_vgpi_entry.get())
    send_vgpi_to_endpoint(vgpi_id, VGPI_ON, reset=True)

def stop_pushing():
    vgpi_id = int(stop_vgpi_entry.get())
    send_vgpi_to_endpoint(vgpi_id, VGPI_ON, reset=True)

def reset_pushing():
    vgpi_id = int(reset_vgpi_entry.get())
    send_vgpi_to_endpoint(vgpi_id, VGPI_ON, reset=True)

def add_endpoint():
    try:
        endpoint = endpoint_entry.get()
        if endpoint:
            endpoints_listbox.insert(tk.END, endpoint)
            endpoint_entry.delete(0, tk.END)
    except Exception as e:
        output_text.insert(tk.END, f"Error adding endpoint: {e}\n")

def remove_endpoint():
    try:
        index = endpoints_listbox.curselection()[0]
        endpoints_listbox.delete(index)
    except IndexError:
        output_text.insert(tk.END, f"Error removing endpoint: No endpoint selected\n")

def clear_endpoints():
    endpoints_listbox.delete(0, tk.END)

def gui():
    global root, output_text, endpoints_listbox, endpoint_entry
    global start_vgpi_entry, stop_vgpi_entry, reset_vgpi_entry

    root = tk.Tk()
    root.title("API Data Processor")

    tk.Label(root, text="Endpoint:").pack(pady=10)
    endpoint_entry = tk.Entry(root, width=40)
    endpoint_entry.pack(pady=10)

    tk.Label(root, text="Start VGPI ID:").pack(pady=10)
    start_vgpi_entry = tk.Entry(root, width=40)
    start_vgpi_entry.pack(pady=10)
    start_vgpi_entry.insert(0, "1")

    tk.Label(root, text="Stop VGPI ID:").pack(pady=10)
    stop_vgpi_entry = tk.Entry(root, width=40)
    stop_vgpi_entry.pack(pady=10)
    stop_vgpi_entry.insert(0, "2")

    tk.Label(root, text="Reset VGPI ID:").pack(pady=10)
    reset_vgpi_entry = tk.Entry(root, width=40)
    reset_vgpi_entry.pack(pady=10)
    reset_vgpi_entry.insert(0, "3")

    add_button = tk.Button(root, text="Add Endpoint", command=add_endpoint)
    add_button.pack(pady=5)

    remove_button = tk.Button(root, text="Remove Selected Endpoint", command=remove_endpoint)
    remove_button.pack(pady=5)

    clear_button = tk.Button(root, text="Clear All Endpoints", command=clear_endpoints)
    clear_button.pack(pady=5)

    endpoints_listbox = tk.Listbox(root, width=50, height=10)
    endpoints_listbox.pack(pady=10)

    start_button = tk.Button(root, text="Start", command=start_pushing)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop", command=stop_pushing)
    stop_button.pack(pady=10)

    reset_button = tk.Button(root, text="Reset", command=reset_pushing)
    reset_button.pack(pady=10)

    tk.Label(root, text="Real-time Data Output:").pack(pady=10)
    output_text = scrolledtext.ScrolledText(root, width=60, height=10)
    output_text.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    gui()
