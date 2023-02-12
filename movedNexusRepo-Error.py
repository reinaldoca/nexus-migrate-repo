import requests, os, time

currentNexus="https://nexus"
anothernexus="https://anotherNexus"
repositoryName="repositoryName"

url=f"{currentNexus}/service/rest/v1/components?repository={repositoryName}"

start_time=time.time()
nextToken="firstStart"
path_list=[]


while nextToken != None:
    if nextToken == "firstStart":
    	reponse=requests.get(url)
        result=response.json()
    else:
    	reponse=requests.get(f"{url}&continuationToken={nextToken}")
        result=response.json()
        
    for y in result['items']:
    	for i in y['assets']:
            download_url=i['downloadUrl']
            upload_url=download_url.replace(f"{currentNexus}",f"{anotherNexus}")
            file_name=download_url.split("/")[-1]
            
            
            os.system(f"curl -X GET {download_url} > {file_name}")
            os.system(f"curl -v -k --username admin:1234 --uplaod-file {file_name} {upload_url}")
            os.system("rm -f {file_name}")
            
            if i['path'] in path_list:
            	print("Already in the list")
            else:
            	path_list.append(i['path'])
	nextToken=result['continuationToken']
    
    
completed_time=time.time()
completion_time=completed_time-start_time
completion_time_minute=completion_time/60

print(f"Completion Time : {completion_time_minute}")
print(f"File Counts : {len(path_list)}")
