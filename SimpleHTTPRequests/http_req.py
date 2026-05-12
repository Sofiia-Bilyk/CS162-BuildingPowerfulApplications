"""
HTTPBin API Testing Program
============================
This program demonstrates various HTTP operations using the httpbin.org service:
1. Basic Authentication
2. Image Download
3. UUID4 Generation
4. JSON Response Retrieval

All requests and responses are printed for educational purposes.
"""

import requests
import json
from requests.auth import HTTPBasicAuth


def print_separator(title=""):
    """Print a visual separator for better readability."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_request_details(method, url, headers=None, auth=None, data=None):
    """Print detailed information about the HTTP request."""
    print(f"REQUEST METHOD: {method}")
    print(f"REQUEST URL: {url}")
    if headers:
        print(f"REQUEST HEADERS:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
    if auth:
        print(f"REQUEST AUTH: Basic Auth (username: {auth.username}, password: {auth.password})")
    if data:
        print(f"REQUEST DATA: {data}")
    print()


def print_response_details(response):
    """Print detailed information about the HTTP response."""
    print(f"RESPONSE STATUS CODE: {response.status_code}")
    print(f"RESPONSE STATUS TEXT: {response.reason}")
    print(f"RESPONSE HEADERS:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print()


def task_1_basic_auth():
    """
    Task 1: Basic Authentication
    -----------------------------
    httpbin.org provides a /basic-auth/:user/:passwd endpoint that requires
    HTTP Basic Authentication. If credentials are correct, it returns 200 OK.
    If incorrect, it returns 401 Unauthorized.
    
    The requests library makes this easy with the 'auth' parameter which
    automatically encodes credentials in the Authorization header.
    """
    print_separator("TASK 1: Basic Authentication")
    
    # Define credentials
    username = "testuser"
    password = "testpass"
    url = f"https://httpbin.org/basic-auth/{username}/{password}"
    
    # Create Basic Auth object
    auth = HTTPBasicAuth(username, password)
    
    # Print request details
    print_request_details("GET", url, auth=auth)
    
    # Make the authenticated request
    response = requests.get(url, auth=auth)
    
    # Print response details
    print_response_details(response)
    
    # Print response body
    print("RESPONSE BODY:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(response.text)
    
    # Verify success
    if response.status_code == 200:
        print("\n[SUCCESS] Authentication successful!")
    else:
        print(f"\n[FAILED] Authentication failed with status {response.status_code}")
    
    return response


def task_2_download_image():
    """
    Task 2: Download an Image
    --------------------------
    httpbin.org provides several image endpoints:
    - /image/jpeg - Returns a JPEG image
    - /image/png - Returns a PNG image
    - /image/svg - Returns an SVG image
    - /image/webp - Returns a WebP image
    
    We'll download a JPEG image and save it to disk. The response.content
    contains the binary image data.
    """
    print_separator("TASK 2: Download an Image")
    
    # Choose image format (jpeg, png, svg, webp)
    image_format = "jpeg"
    url = f"https://httpbin.org/image/{image_format}"
    
    # Set appropriate headers to request image
    headers = {
        "Accept": f"image/{image_format}"
    }
    
    # Print request details
    print_request_details("GET", url, headers=headers)
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    # Print response details
    print_response_details(response)
    
    # Print response body info (binary data, so we'll show size)
    print(f"RESPONSE BODY: Binary image data ({len(response.content)} bytes)")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    
    # Save the image to disk
    filename = f"downloaded_image.{image_format}"
    with open(filename, "wb") as f:
        f.write(response.content)
    
    print(f"\n[SUCCESS] Image downloaded and saved as '{filename}'")
    print(f"  File size: {len(response.content)} bytes")
    
    return response, filename


def task_3_generate_uuid():
    """
    Task 3: Generate a UUID4
    -------------------------
    httpbin.org provides a /uuid endpoint that generates and returns a UUID4
    (version 4 UUID). UUID4 uses random numbers to generate unique identifiers.
    
    This is a simple GET request that returns JSON with a 'uuid' field.
    """
    print_separator("TASK 3: Generate UUID4")
    
    url = "https://httpbin.org/uuid"
    
    # Print request details
    print_request_details("GET", url)
    
    # Make the request
    response = requests.get(url)
    
    # Print response details
    print_response_details(response)
    
    # Print response body
    print("RESPONSE BODY:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
        uuid_value = response_json.get("uuid")
        print(f"\n[SUCCESS] Generated UUID4: {uuid_value}")
    except:
        print(response.text)
        print("\n[FAILED] Could not parse JSON response")
    
    return response


def task_4_json_response():
    """
    Task 4: Return a Simple JSON Response
    --------------------------------------
    httpbin.org provides a /json endpoint that returns a simple JSON response.
    This is useful for testing JSON parsing and handling.
    
    The endpoint returns a predefined JSON object with various data types.
    """
    print_separator("TASK 4: Get JSON Response")
    
    url = "https://httpbin.org/json"
    
    # Print request details
    print_request_details("GET", url)
    
    # Make the request
    response = requests.get(url)
    
    # Print response details
    print_response_details(response)
    
    # Print response body
    print("RESPONSE BODY:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
        print("\n[SUCCESS] JSON response received and parsed!")
    except json.JSONDecodeError as e:
        print(response.text)
        print(f"\n[FAILED] JSON parsing error: {e}")
    
    return response


def main():
    """
    Main function that executes all tasks sequentially.
    """
    print("\n" + "=" * 80)
    print("  HTTPBin API Testing Program")
    print("  Demonstrating: Basic Auth, Image Download, UUID Generation, JSON Response")
    print("=" * 80)
    
    try:
        # Task 1: Basic Authentication
        task_1_basic_auth()
        
        # Task 2: Download Image
        task_2_download_image()
        
        # Task 3: Generate UUID4
        task_3_generate_uuid()
        
        # Task 4: Get JSON Response
        task_4_json_response()
        
        print_separator("ALL TASKS COMPLETED")
        print("[SUCCESS] All tasks executed successfully!")
        print("\nNote: Check the current directory for 'downloaded_image.jpeg'")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Network request failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    main()
