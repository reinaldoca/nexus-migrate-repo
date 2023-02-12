import requests
from requests.auth import HTTPBasicAuth
import os
import time
from getpass import getpass
import pprint as pp

currentNexus = "https://old-nexus.example.com"
newNexus = "https://new-nexus.example.com"
currentRepositoryName = "npm-old-private"
newRepositoryName = "npm-new-private"

url = f"{currentNexus}/service/rest/v1/components?repository={currentRepositoryName}"
upload_url = url.replace(currentNexus, newNexus).replace(currentRepositoryName, newRepositoryName)

start_time = time.time()
nextToken = "firstStart"
successful_list = []
failed_list = []
fail_timeout = 1

USER=input("User: ")
PASSWORD=getpass()

def download(url, targetFileName):
    print(f"Downloading {url} to {targetFileName}")
    res = os.system(f"curl -X GET --fail --silent {url} > {targetFileName}")
    if res != 0:
        print(f"Download failed: {targetFileName}")
        time.sleep(fail_timeout)
        return False
    return True

def upload(srcFileName):
    print(f"Uploading {srcFileName} to {upload_url}")
    res = os.system(f'curl --fail --user {USER}:{PASSWORD} -F "npm.asset=@{srcFileName}" {upload_url}')
    if res != 0:
        print(f"Upload failed: {srcFileName}")
        time.sleep(fail_timeout)
        return False
    return True

def delete(fileName):
    print(f"Deleting {fileName}")
    res = os.system(f"rm -rf {fileName}")
    if res != 0:
        print(f"Delete failed: {fileName}")
        time.sleep(fail_timeout)
        return False
    return True

try:
    while nextToken != None:
        if nextToken == "firstStart":
            print(f"URL: {url}")
            response = requests.get(url, auth=HTTPBasicAuth(USER, PASSWORD))
            print(f"response: {response}")
        else:
            response = requests.get(f"{url}&continuationToken={nextToken}", auth=HTTPBasicAuth(USER, PASSWORD))
        result = response.json()
        artifacts = result['items']

        for artifact in artifacts:
            for assets in artifact['assets']:
                download_url = assets['downloadUrl']
                file_name = download_url.split("/")[-1]

                if not download(download_url, file_name):
                    failed_list.append({"path": assets['path'], "cause": "download"})
                    continue
                if not upload(file_name):
                    failed_list.append({"path": assets['path'], "cause": "upload"})
                if not delete(file_name):
                    failed_list.append({"path": assets['path'], "cause": "delete"})
                    continue

                if assets['path'] not in successful_list:
                    successful_list.append(assets['path'])
            nextToken = result['continuationToken']
except KeyboardInterrupt:
    print("^C received, stopping...")

completed_time = time.time()
completion_time = completed_time-start_time
completion_time_minute = completion_time/60

print(f"Completion Time: {completion_time_minute:.2f} min")
print(f"Successful File Count: {len(successful_list)}/{len(successful_list)+len(failed_list)}")

if len(failed_list) > 0:
    print("Failed Files:")
    pp.pprint(failed_list, width=1, indent=4)
