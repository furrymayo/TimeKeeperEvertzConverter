import requests
import tkinter as tk
from tkinter import scrolledtext
import time
import socket

BASE_URL = "http://127.0.0.1:4000"

def get_all_rooms():
    try:
        response = requests.get(f"{BASE_URL}/api/rooms")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def get_all_timers():
    try:
        response = requests.get(f"{BASE_URL}/api/timers")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

def calculate_countdown(datetime_epoch):
    current_time_epoch = int(time.time() * 1000)
    countdown_millis = datetime_epoch - current_time_epoch
    hours, remainder = divmod(countdown_millis // 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Constants for VGPI formatting
VGPI_ON = "1"
VGPI_OFF = "0"

def format_vgpi_data(virt_gpi_num, status):
    return f"%16S{virt_gpi_num}={status}%Z"


def send_data_to_endpoint(data, raw_data, endpoints, output_text):
    output_text.insert(tk.END, f"Raw data: {raw_data}\n")
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

def process_and_send_data(output_text):
    endpoints = list(endpoints_listbox.get(0, tk.END))
    rooms = get_all_rooms()

    for room in rooms:
        room_id = room.get('id')
        timers_for_room = [timer for timer in get_all_timers() if timer.get('roomID') == room_id]
        for timer in timers_for_room:
            countdown = calculate_countdown(timer['datetime'])
            status = VGPI_ON if countdown != "00:00:00" else VGPI_OFF  # Example logic, adjust as needed
            vgpi_data = format_vgpi_data(room_id, status)  # Using room_id as virtual GPI number for this example
            send_data_to_endpoint(vgpi_data, timer, endpoints, output_text)


should_continue = False

def push_data_loop():
    global should_continue, output_text
    if not should_continue:
        return

    try:
        process_and_send_data(output_text)
    except Exception as e:
        output_text.insert(tk.END, f"An error occurred: {e}\n")
    finally:
        root.after(1000, push_data_loop)  # Increase delay to 1 second

def start_pushing():
    global should_continue, base_url_entry, BASE_URL
    BASE_URL = base_url_entry.get()
    should_continue = True
    push_data_loop()

def stop_pushing():
    global should_continue
    should_continue = False

def add_endpoint():
    try:
        endpoint = endpoint_entry.get()
        if endpoint:
            endpoints_listbox.insert(tk.END, endpoint)
            endpoint_entry.delete(0, tk.END)
    except Exception as e:
        print(f"Error adding endpoint: {e}")


def remove_endpoint():
    try:
        index = endpoints_listbox.curselection()[0]
        endpoints_listbox.delete(index)
    except IndexError:
        pass

def clear_endpoints():
    endpoints_listbox.delete(0, tk.END)

def gui():
    global root, base_url_entry, output_text, endpoints_listbox, endpoint_entry
    root = tk.Tk()
    root.title("API Data Processor")

    tk.Label(root, text="Base URL:").pack(pady=10)
    base_url_entry = tk.Entry(root, width=40)
    base_url_entry.pack(pady=10)
    base_url_entry.insert(0, BASE_URL)

    tk.Label(root, text="Endpoint:").pack(pady=10)
    endpoint_entry = tk.Entry(root, width=40)
    endpoint_entry.pack(pady=10)

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

    tk.Label(root, text="Real-time Data Output:").pack(pady=10)
    output_text = scrolledtext.ScrolledText(root, width=60, height=10)
    output_text.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    gui()
