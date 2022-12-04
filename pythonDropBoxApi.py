from dropbox import DropboxOAuth2FlowNoRedirect
import os
import random
import dropbox
import webbrowser
import requests
import json
from tqdm import tqdm
from datetime import datetime
date_today = "Event-" + datetime.today().strftime('%Y-%m-%d') + \
    "-"+str(random.randint(10, 1000))
# put here path folder do you want put files inside it
Path_drop = ""
# put here app_key
App_key = ''
# put here secret_key
Secret_key = ''
# that's code for get refresh_Token  because access_token expret after 2h:

authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code&token_access_type=offline" % App_key
webbrowser.open_new(authorization_url)
authorization_code = input('Enter the code:\n')

# that's code for get refresh_Token :
#  should be copy Code d'accès généré and put then in console
token_url = "https://api.dropbox.com/oauth2/token"
params = {
    "code": authorization_code,
    "grant_type": "authorization_code",
    "client_id": App_key,
    "client_secret": Secret_key
}
r = requests.post(token_url, data=params)
print(r.text)
x = json.loads(str(r.text))
refreshToken = x["refresh_token"]
print("refresh Token :")
print(refreshToken)
#  Generated access token
token_url = "https://api.dropbox.com/oauth2/token"
params = {
    "refresh_token": refreshToken,
    "grant_type": "refresh_token",
    "client_id": App_key,
    "client_secret": Secret_key
}
r = requests.post(token_url, data=params)
# print(r.text)
v = json.loads(str(r.text))
Token = v["access_token"]
print("access Token :")
print(Token)
#  method uplload file in dropBox


def upload(
    access_token,
    file_path,
    target_path,
    timeout=900,
    chunk_size=4 * 1024 * 1024,
):
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        if file_size <= chunk_size:
            print(dbx.files_upload(f.read(), target_path))
        else:
            with tqdm(total=file_size, desc="Uploaded") as pbar:
                upload_session_start_result = dbx.files_upload_session_start(
                    f.read(chunk_size)
                )
                pbar.update(chunk_size)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell(),
                )
                commit = dropbox.files.CommitInfo(path=target_path)
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= chunk_size:
                        print(
                            dbx.files_upload_session_finish(
                                f.read(chunk_size), cursor, commit)
                        )
                    else:
                        dbx.files_upload_session_append(
                            f.read(chunk_size), cursor.session_id, cursor.offset,)
                        cursor.offset = f.tell()
                    pbar.update(chunk_size)

#  Main


def main():
    upload(Token, "./test.txt", '{}/{}.txt'.format(Path_drop, date_today))


if __name__ == '__main__':
    main()
