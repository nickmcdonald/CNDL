# importing the requests library
import requests

# api-endpoint
URL = "https://api.github.com/repos/nickmcdonald/CNDLDownloads/releases"

# sending get request and saving the response as response object
r = requests.get(url=URL)

# extracting data in json format
releases = r.json()
downloads = 0
for release in releases:
    for asset in release["assets"]:
        downloads += asset["download_count"]

# printing the output
print("downloads: " + str(downloads))
