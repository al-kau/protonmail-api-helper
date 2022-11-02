import os
import getpass
import json
import readline
import atexit
from proton.api import Session

cwd = os.getcwd()
history_path = os.path.join(os.path.expanduser("~"), ".protonmail_api_history")

if os.path.exists(history_path):
    readline.read_history_file(history_path)

readline.set_history_length(100)

def remove_last_history_line():
    readline.remove_history_item(readline.get_current_history_length()-1)

def input_no_history(text):
    line = input(text)
    remove_last_history_line()
    return line


def print_help():
    print("List commands:")
    print("1) auth [(optional)--user=<id> --psw=<password> --api-url=<address> --alt-route=<[True|False]> --tls=<[True|False]>")
    print("        --app-version=<app_version> --user-agent=<user_agent> --client-secret=<client_secret>]")
    print("2) dump [(optional)--file=<filename>]")
    print("3) load [(optional)--file=<filename> --alt-route=<[True|False]> --tls=<[True|False]>]")
    print("4) refresh")
    print("5) request --query=<query> [(optional)--method<[get|post|put|delete|patch]>]")
    print("        e.g. request --query=/mail/v4/messages/count")
    print("        e.g. request --query=/mail/v4/messages?LabelID=0 --method=get")
    print("        e.g. request --query=/tests/ping")
    print("6) logout")
    print("7) get --attr=<attribute> [(optional)--param=<json>]")
    print("        e.g. get --attr=Scope")
    print("        e.g. get --attr=refresh --param={}")
    print("        e.g. get --attr=api_request --param={\"endpoint\":\"/tests/ping\"}")
    print("8) set --attr=<attribute> [(optional)--value=<value>]")
    print("        e.g. set --attr=enable_alternative_routing --value=")
    print("        e.g. set --attr=enable_alternative_routing --value=1")
    print("9) exit")
    print("")

def auth(
        username="",
        password="",
        api_url="https://mail-api.proton.me",
        appversion="Other", 
        user_agent="None",
        client_secret=None,
        tls_pinning=False, 
        alt_route=True,
):
    global proton_session 
    proton_session = Session(
        api_url=api_url,
        appversion=appversion,
        user_agent=user_agent,
        log_dir_path=os.path.join(cwd, "logs"),
        cache_dir_path=os.path.join(cwd, "cache"),
        tls_pinning=tls_pinning,
        ClientSecret=client_secret
    )

    proton_session.enable_alternative_routing=alt_route

    if not username:
        username=input_no_history("username: ")

    if not password:
        password = getpass.getpass("password: ")

    try:
        scope = proton_session.authenticate(username, password)

        if 'twofactor' in scope:
            code=input_no_history("2fa code: ")
            scope = proton_session.provide_2fa(code)

    except Exception as error:
        print('ERROR', error)

    print("The scope is: ", scope)

def load(
        file_name,
        tls_pinning=False,
        alt_route=True,
    ):
    global proton_session
    with open(file_name, "r") as f:
        dump_data = json.loads(f.read())
        proton_session = Session.load(
            dump=dump_data,
            log_dir_path=os.path.join(cwd, "logs"),
            cache_dir_path=os.path.join(cwd, "cache"),
            tls_pinning=tls_pinning
        )
        proton_session.enable_alternative_routing=alt_route

def dump(file_name):
    dump_json = proton_session.dump()
    with open(file_name, 'w') as f:
        f.write(json.dumps(dump_json))

def refresh():
    proton_session.refresh()

def request(query, method=None):
    response=proton_session.api_request(
        endpoint=query,
        method=method
    )
    print(response)

def logout():
    proton_session.logout()

def get_attribute(name,param):
    try:
        attr = getattr(proton_session,name)
        res =  attr
        if param:
            prm = json.loads(param)
            res = attr(**prm)
        print(res)
    except Exception as error:
        print(f'get_attribute({name},{param}): {error}')

def set_attribute(name,value):
    try:
        setattr(proton_session,name,value)
    except Exception as error:
        print(f'set_attribute({name},{value}): {error}')

print_help()

exit=False

while not exit:

    try:
        command=input("command: ").split("--")

        cmd="help"
        params={}

        if len(command) > 0:
            cmd=command[0].strip()

        if len(command) > 1:
            for data in [[param.strip() for param in command[i].split("=")] for i in range(1, len(command))]:
                if len(data) >= 2:
                    params[data[0]]='='.join([data[i] for i in range(1, len(data))])

        if cmd=="exit":
            exit=True
        elif cmd=="auth":
            auth (
                username=params.get("user",""),
                password=params.get("psw",""),
                api_url=params.get("api-url","https://mail-api.proton.me"),
                appversion=params.get("app-version","Other"), 
                user_agent=params.get("user-agent","None"),
                client_secret=params.get("client-secret",None),
                tls_pinning=params.get("tls",False),
                alt_route=params.get("alt-route",True)
            )
        elif cmd=="load":
            load(
                file_name=params.get("file","./protonmail.dump.json"),
                tls_pinning=params.get("tls",False),
                alt_route=params.get("alt-route",True)
            )
        elif cmd=="dump":
            dump(file_name=params.get("file","./protonmail.dump.json"))
        elif cmd=="refresh":
            refresh()
        elif cmd=="request" and params["query"]:
            request(
                query=params["query"], 
                method=params.get("method",None)
            )
        elif cmd=="logout":
            logout()
        elif cmd=="get" and params["attr"]:
            get_attribute(
                name=params["attr"],
                param=params.get("param",None)
            )
        elif cmd=="set" and params["attr"]:
            set_attribute(
                name=params["attr"],
                value=params.get("value",None)
            )
        else:
            print_help()
    except Exception as error:
        print('ERROR', error)

atexit.register(readline.write_history_file, history_path)