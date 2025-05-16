#!/usr/bin/python3.11
import requests


def main():
    url = "http://qam.suse.de/media/downloads/ltp_known_issues.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        print(content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
