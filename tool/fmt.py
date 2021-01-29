#!/usr/bin/env python3
import argparse, requests, os, pathlib, zipfile,io

def zipdir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A filemangement tool for fiverr')

    commands = parser.add_subparsers(title="commands", help="commands help", dest="commands", metavar="<command>", required=True)
    parser_pull = commands.add_parser('pull', help='pull help')
    parser_pull.add_argument('ip', metavar="<ip>")
    parser_pull.add_argument('--fromPath', metavar="path")
    parser_pull.add_argument('--toDir', metavar="path")

    parser_push = commands.add_parser('push', help='push help')
    parser_push.add_argument('ip', metavar="<ip>")
    parser_push.add_argument('--fromPath', metavar="path")
    parser_push.add_argument("--toDir", metavar="path")

    args = parser.parse_args()

    if args.commands == "pull":
        ip = args.ip
        fromPathServer = f"'{ args.fromPath }'" if args.fromPath != None else "'.'"
        toDirClient = args.toDir if args.toDir != None else os.path.abspath(".")
        res = requests.get("http://" + ip + "/pull/" + fromPathServer)

        if res.status_code == 404:
            print("file not found on server")
        elif res.status_code == 200:

            filename = res.headers['Content-Disposition'].split("=")[-1]
            file_extension = filename.split(".")[-1]
            if file_extension == "zip":
                with zipfile.ZipFile(io.BytesIO(res.content), "r") as zip_ref:
                    zip_ref.extractall(toDirClient)
            else:
                pathlib.Path(toDirClient).mkdir(exist_ok=True)
                f = open(os.path.join(toDirClient, filename), 'wb')
                f.write(res.content)
                f.close()

    elif args.commands == "push":
        ip = args.ip
        fromPathClient = args.fromPath if args.fromPath != None else os.path.abspath(".")
        toDirServer = f"'{ args.toDir }'"  if args.toDir != None else "'.'"

        if os.path.isdir(fromPathClient):
            memory_file = io.BytesIO()
            zip_file = zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED)
            zipdir(fromPathClient, zip_file)
            zip_file.close()
            memory_file.name = fromPathClient.split("/")[-1] + ".zip"
            memory_file.seek(0)
            files = { "file": memory_file }
        else:
            files = { "file": open(fromPathClient, 'rb') }

        res = requests.post("http://" + ip + "/push/" + toDirServer, files=files)
        if res.status_code == 200:
            print("uploaded data successful!")
        else:
            print("an error occured while uploading your files")
