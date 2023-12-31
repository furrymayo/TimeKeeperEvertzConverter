import socket
import threading
import re  # For regex parsing


def handle_client(client_socket):
    # This function will handle the client connection
    client_address = client_socket.getpeername()
    print(f"Connection from {client_address}")

    data_parts = []
    while True:
        # Receive data in chunks
        chunk = client_socket.recv(1024)
        if not chunk:
            # No more data to receive
            break
        data_parts.append(chunk)

    # Combine all chunks and decode
    data = b''.join(data_parts).decode('ASCII')
    if data:  # Check if data is not empty
        print(f"Received raw data from {client_address}: {data}")

        # Parse UMD data
        match = re.match(r"%\d{2,3}D%\dS(.+)%Z", data)
        if match:
            umd_text = match.group(1)
            print(f"UMD Text: {umd_text}")
        else:
            print(f"Received data from {client_address} doesn't match UMD format.")
    else:
        print(f"Received empty data from {client_address}")

    client_socket.close()


def start_server(port=9801):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Listening for UMD data on port {port}...")

    while True:
        # Accept a connection
        client_socket, _ = server_socket.accept()

        # Start a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Error: {e}")
