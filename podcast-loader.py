import importlib
import subprocess
import sys

#### Check if feedparser library is installed, if not ask to install it ####
try:
    importlib.import_module('feedparser')
    feedparser_installed = True
except ImportError:
    feedparser_installed = False

if not feedparser_installed:
    print("The 'feedparser' library is not installed.")
    print("Press Enter to install it, or 'n' to abort.")
    choice = input().lower()
    if choice == 'n':
        print("The 'feedparser' library is required for this script. Please install it manually.")
        sys.exit(0)

    # Use pip to install feedparser
    subprocess.check_call(['pip', 'install', 'feedparser'])
    print("feedparser library has been installed.")
    
#### ---------- Process feedparser ---------- ####
import feedparser
import requests
import os

def download_episode(url, file_name, episode_num, total_episodes):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(file_name, 'wb') as file:
        for data in response.iter_content(chunk_size=4096):
            file.write(data)
            downloaded_size += len(data)
            if total_size > 0:
                progress = int((downloaded_size / total_size) * 100)
                print(f"Downloading {file_name} [{episode_num} of {total_episodes}] - {progress}% complete", end='\r')

    print(" - Done - ")

def download_podcast_feed(feed_url):
    feed = feedparser.parse(feed_url)
    podcast_title = feed.feed.title
    print(f"Downloading episodes from {podcast_title}...\n")

    episodes = []

    for index, entry in enumerate(reversed(feed.entries), start=1):
        episode_title = entry.title
        episode_url = entry.enclosures[0].href
        file_name = f"{podcast_title} [{index}] - {episode_title}.mp3"
        episodes.append((index, episode_title, episode_url, file_name))

    total_episodes = len(episodes)

    print(f"Total episodes: {total_episodes}\n")

    for idx, episode in enumerate(episodes, start=1):
        print(f"{idx}. [{episode[0]}] {episode[1]}")

    print("\n")

    # Filter episodes by word or phrase
    filter_choice = input("Enter a word or phrase to filter episodes (or Enter to skip) (or \\ to reverse ordering): ")
    if filter_choice:
        if filter_choice == "\\":
            episodes = []

            for index, entry in enumerate(feed.entries, start=1):
                episode_title = entry.title
                episode_url = entry.enclosures[0].href
                file_name = f"{podcast_title} - {episode_title}.mp3"
                episodes.append((index, episode_title, episode_url, file_name))

            total_episodes = len(episodes)

            print(f"Total episodes: {total_episodes}\n")

            for idx, episode in enumerate(episodes, start=1):
                print(f"{idx}. [{episode[0]}] {episode[1]}")

            print("\n")
        else:
            filtered_episodes = [
                episode for episode in episodes if filter_choice.lower() in episode[1].lower()
            ]
            episodes = filtered_episodes

        total_episodes = len(episodes)

        print(f"\nFiltered episodes with '{filter_choice}':\n")
        if filter_choice == "\\":
            for idx, episode in enumerate(episodes, start=1):
                print(f"{idx}. [{idx}] {episode[1]}")
        else:
            for idx, episode in enumerate(episodes, start=1):
                print(f"{idx}. [{total_episodes - idx + 1}] {episode[1]}")

        print("\n")

    episode_choice = input("Enter the episode number(s) you want to download (e.g., 1,3-5, or * for all) (or 'q' to quit): ")

    if episode_choice.lower() == "q":
        print("Quitting...")
        return

    if episode_choice.lower() in ["*", "a", "all"]:
        selected_episodes = range(1, len(episodes) + 1)
    else:
        choices = episode_choice.split(",")
        selected_episodes = []

        for choice in choices:
            if "-" in choice:
                start, end = choice.split("-")
                start = int(start.strip())
                end = int(end.strip())
                if start <= end <= len(episodes):
                    selected_episodes.extend(range(start, end+1))
                else:
                    print(f"Invalid episode range: {choice}")
            elif choice.isdigit():
                episode_num = int(choice.strip())
                if 1 <= episode_num <= len(episodes):
                    selected_episodes.append(episode_num)
                else:
                    print(f"Invalid episode number: {choice}")
            else:
                print(f"Invalid input: {choice}")

    total_selected_episodes = len(selected_episodes)

    for idx, episode_num in enumerate(selected_episodes, start=1):
        _, episode_title, episode_url, file_name = episodes[episode_num - 1]
        if not os.path.exists(file_name):
            print(f"Downloading episode {idx} of {total_selected_episodes}")
            download_episode(episode_url, file_name, idx, total_selected_episodes)
        else:
            print(f"File already exists for episode {episode_num}. Skipping download.")

    print("\nDownload complete!")

### ---------- MAIN ---------- ###
feed_url = input("Please enter podcast URL: ")
download_podcast_feed(feed_url)
