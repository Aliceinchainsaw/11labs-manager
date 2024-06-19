import os
import requests
from requests.exceptions import RequestException, HTTPError
import time
import pygame
from playsound import playsound
import json

# Constants
API_BASE_URL = "https://api.elevenlabs.io/v1/history"
API_KEY = "ENTERAPIKEY"

# Create a persistent session
session = requests.Session()
session.headers.update({"xi-api-key": API_KEY})

def get_all_audio_metadata(start_after_history_item_id=None):
    params = {}
    if start_after_history_item_id:
        params['start_after_history_item_id'] = start_after_history_item_id
    response = session.get(API_BASE_URL, params=params)
    return response

def view_all_audio_metadata():
    last_history_item_id = None
    has_more = True

    while has_more:
        response = get_all_audio_metadata(last_history_item_id)
        
        if not response.ok:
            print("Failed to retrieve data.")
            break
        
        metadata = response.json()  # Parse the JSON response now

        print(metadata)
        last_history_item_id = metadata.get('last_history_item_id')
        has_more = metadata.get('has_more', False)
        
        handle_rate_limiting(response)  # Pass the response object to the function''

def handle_rate_limiting(response):
    if 'X-RateLimit-Remaining' in response.headers:
        if int(response.headers['X-RateLimit-Remaining']) == 0:
            reset_time = response.headers['X-RateLimit-Reset']
            time.sleep(max(0, int(reset_time) - time.time()))

def play_audio_file(history_item_id):
    try:
        # Make a request to the API to get the audio file
        audio_response = session.get(f"{API_BASE_URL}/{history_item_id}/audio")
        audio_response.raise_for_status()  # Raise an exception for HTTP errors

        # Write the audio content to a temporary file
        with open('temp_audio.mp3', 'wb') as audio_file:
            audio_file.write(audio_response.content)

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load the audio file
        pygame.mixer.music.load('temp_audio.mp3')

        # Play the audio file
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    finally:
        # Clean up the temporary file if it exists
        try:
            os.remove('temp_audio.mp3')
        except OSError:
            pass

def delete_history_item(history_item_id):
    try:
        delete_response = session.delete(f"{API_BASE_URL}/{history_item_id}")

        if delete_response.ok:
            print(f"Successfully deleted history item with ID: {history_item_id}")
        else:
            print(f"Failed to delete history item with ID: {history_item_id}. Status code: {delete_response.status_code}")
    except RequestException as e:
        print(f"An error occurred while attempting to delete history item: {e}")


def delete_all_history_items():
    last_history_item_id = None
    has_more = True

    while has_more:
        response = get_all_audio_metadata(last_history_item_id)
        
        if not response.ok:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            break
        
        metadata = response.json()  # Ensure that this function returns JSON response

        for item in metadata.get('history', []):
            history_item_id = item['history_item_id']
            delete_response = session.delete(f"{API_BASE_URL}/{history_item_id}")
            if delete_response.ok:
                print(f"Deleted history item with ID: {history_item_id}")
            else:
                print(f"Failed to delete history item with ID: {history_item_id}. Status code: {delete_response.status_code}")
                
        last_history_item_id = metadata.get('last_history_item_id')
        has_more = metadata.get('has_more', False)

import json

def download_audio_file(history_item_id):
    try:
        # Prepare the request body with the history item ID
        data = {"history_item_ids": [history_item_id]}

        # Make a POST request to download the history item
        download_response = session.post(f"{API_BASE_URL}/download", headers={"Content-Type": "application/json"}, data=json.dumps(data))
        
        if download_response.status_code == 200:
            # Determine the file extension (single file as .mp3, multiple as .zip)
            file_extension = 'mp3' if len(data["history_item_ids"]) == 1 else 'zip'
            # Write the downloaded content to a file
            with open(f'{history_item_id}.{file_extension}', 'wb') as file:
                file.write(download_response.content)
            print(f"Audio file {history_item_id}.{file_extension} downloaded successfully.")
        else:
            print(f"Failed to download audio file. Status code: {download_response.status_code}")
    except RequestException as e:
        print(f"An error occurred while attempting to download audio file: {e}")



def download_all_history_items():
    # First, retrieve all history items
    response = session.get(API_BASE_URL)
    if response.status_code == 200:
        history_items = response.json().get('history', [])
        history_item_ids = [item['history_item_id'] for item in history_items]
        
        # Prepare the request body with history item IDs
        data = {"history_item_ids": history_item_ids}

        # Make a POST request to download the history items
        download_response = session.post(f"{API_BASE_URL}/download", data=json.dumps(data))
        
        if download_response.status_code == 200:
            # Write the downloaded content to a file
            with open('downloaded_history_items.zip', 'wb') as file:
                file.write(download_response.content)
            print("History items downloaded successfully.")
        else:
            print(f"Failed to download history items. Status code: {download_response.status_code}")
    else:
        print(f"Failed to retrieve history items. Status code: {response.status_code}")




def search_metadata_by_string(search_string):
    last_history_item_id = None
    has_more = True
    matches = []

    while has_more:
        response = get_all_audio_metadata(last_history_item_id)
        
        if not response.ok:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            break

        metadata = response.json()  # Ensure that this function returns JSON response
        
        matches.extend([item for item in metadata.get('history', []) if search_string.lower() in item.get('text', '').lower()])
        
        last_history_item_id = metadata.get('last_history_item_id')
        has_more = metadata.get('has_more', False)
    
    # Simple selection mechanism
    while matches:
        for i, match in enumerate(matches):
            print(f"{i + 1}. ID: {match['history_item_id']}, Text: {match['text']}")

        selection = input("Enter the number of the history item you want to select, or type 'back' to return to the main menu: ")
        
        if selection.lower() == 'back':
            return

        try:
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(matches):
                selected_item = matches[selected_index]
                print("Choose an action:")
                print("1 - Play audio")
                print("2 - Download audio")
                print("3 - Delete file")
                print("4 - Go back to file selection")
                print("5 - Go back to main menu")
                action = input("Enter your choice (1-5): ")

                if action == '1':
                    play_audio_file(selected_item['history_item_id'])
                elif action == '2':
                    download_audio_file(selected_item['history_item_id'])
                elif action == '3':
                    delete_history_item(selected_item['history_item_id'])
                elif action == '4':
                    continue
                elif action == '5':
                    return
                else:
                    print("Invalid selection. Please try again.")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")





def main_menu():
    while True:
        print("\nMenu:")
        print("1. View all audio metadata")
        print("2. Play an audio file")
        print("3. Delete all history items")
        print("4. Download all files")
        print("5. Search metadata by string")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            view_all_audio_metadata()
        elif choice == '2':
            history_item_id = input("Enter the history item ID of the audio file: ")
            play_audio_file(history_item_id)
        elif choice == '3':
            delete_all_history_items()
        elif choice == '4':
            download_all_history_items()
        elif choice == '5':
            search_string = input("Enter the search string: ")
            matches = search_metadata_by_string(search_string)
            if matches:
                print("Matching history items:")
                for item in matches:
                    print(f"ID: {item['history_item_id']}, Text: {item['text']}")
            else:
                print("No matching history items found.")
        elif choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()

