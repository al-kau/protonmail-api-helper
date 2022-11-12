import sys
import os
import json

dump_ext=".dump.json"
resp_ext=".http"
cwd=os.getcwd()
dump_dir = os.path.join(cwd, ".protonmail")
responce_dir = os.path.join(cwd, ".responses")

dump_key="--dump="
resp_key="--resp="

def parseArgv():
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if arg.startswith(dump_key):
            return (True, arg[len(dump_key):])
        elif arg.startswith(resp_key):
            return (False, arg[len(resp_key):])
    return (True,"")

(is_dump, file_name) = parseArgv()

def filePath(parse_dump, file_name):
    dir = responce_dir
    ext = resp_ext
    if parse_dump:
        dir = dump_dir
        ext = dump_ext
    return os.path.join(dir, f"{file_name}{ext}")

def getJson(file_path):
    with open(file_path, "r") as file:
        return json.loads(file.read())

def processJson(json):
    try:
        return {
            "ACCESS_TOKEN" : json['AccessToken'],
            "UID" : json['UID'],
            "REFRESH_TOKEN" : json['RefreshToken']
        }
    except Exception as error: 
        print(error)

def processDump(dump):
    try:
        return processJson(dump['session_data'])
    except Exception as error: 
        print(error)

def processResp(resp):
    return processJson(resp)

def prepareEnv(path, is_dump):
    env=""
    jsonData = getJson(path)
    map = processDump(jsonData) if (is_dump) else processResp(jsonData)
    
    for key in map:
        env+=f"{key}={map[key]}\n"
    return env

def updateEnv(data):
    path=os.path.join(cwd, ".env")
    with open(path, 'w') as file:
        file.write(data)

path=filePath(is_dump, file_name)
print(f"read file: {path}")

env_data=prepareEnv(path,is_dump)
print(env_data)

updateEnv(env_data)
