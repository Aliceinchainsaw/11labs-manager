

This Python script provides an interactive command-line interface for managing audio history data from the Eleven Labs API. It allows you to view, play, download, search, and delete audio files associated with your Eleven Labs account.

 Features

1. **View All Audio Metadata**: Retrieve and display metadata for all audio history items, including pagination handling to load more items if available.

2. **Play Audio Files**: Play audio files directly by providing the history item ID, using the `pygame` library for playback.

3. **Delete All History Items**: Delete all audio history items, iterating through the list of items and removing them from your account.

4. **Download Audio Files**: Download single or multiple audio files, saving them as MP3 or ZIP files locally.

5. **Search Metadata by String**: Search for specific audio files by matching strings in the metadata, then choose to play, download, or delete the selected file.

### How It Works

- **Persistent Session**: Uses a persistent session with API key authentication to manage requests efficiently.
- **Rate Limiting**: Handles API rate limiting by checking the rate limit headers and sleeping until the reset time.
- **Interactive Menu**: The script provides an interactive menu for ease of use, allowing you to select actions and input data as needed.

### Setup

1. Replace `"ENTERAPIKEY"` with your actual Eleven Labs API key.
2. Ensure that `pygame` and `playsound` libraries are installed.

### Usage

Run the script, and navigate through the menu options to manage your audio history:
- View metadata for all audio history items.
- Play, download, or delete specific audio files.
- Download all audio files in bulk.
- Search for and interact with specific audio files based on metadata.

