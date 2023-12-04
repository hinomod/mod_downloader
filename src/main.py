print("プログラムを起動しています...")
import random
import time
import requests
import tempfile
import os
import shutil
import datetime

dotmc = os.getenv('APPDATA').replace("\\","/")+"/.minecraft"
if not os.path.exists(dotmc):
    os.mkdir(dotmc)
now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

import eel

eel.init("web")

@eel.expose
def get_mods():
    res = requests.get("https://api.github.com/repos/hinomod/mod_files/contents/mods")
    files = res.json()
    if res.status_code != 200:
        message = "ステータスコード: "+str(res.status_code)
        if "message" in files:
            message += "\nエラーメッセージ: "+files["message"]
        return {"success":False,"message":files["message"]}
    mods = []
    for file in files:
        if file["type"] == "dir":
            mods.append(file["name"])
    return {"success":True,"mods":mods}

@eel.expose
def download_mod(mod):
    res = requests.get("https://api.github.com/repos/hinomod/mod_files/contents/mods/"+mod)
    files = res.json()
    if res.status_code != 200:
        message = "ステータスコード: "+str(res.status_code)
        if "message" in files:
            message += "\nエラーメッセージ: "+files["message"]
        return {"success":False,"message":files["message"]}
    temp_dir = tempfile.mkdtemp().replace("\\","/")
    os.mkdir(temp_dir+"/mods")
    total = 0
    downloaded = 0
    history = "ダウンロードを開始しています..."
    for file in files:
        if file["type"] == "file":
            total += file["size"]
    eel.update_downloading_progress({"downloading":True, "progress":0, "total": total, "history":history})
    for file in files:
        if file["type"] == "file":
            history += "\nダウンロード中: "+file["name"]
            res = requests.get(file["download_url"], stream=True)
            if res.status_code != 200:
                message = "ステータスコード: "+str(res.status_code)
                if "message" in files:
                    message += "\nエラーメッセージ: "+files["message"]
                return {"success":False,"message":files["message"]}
            with open(temp_dir+"/mods/"+file["name"], "wb") as f:
                for data in res.iter_content(1024):
                    f.write(data)
                    downloaded += len(data)
                    eel.update_downloading_progress({"downloading":True, "progress":downloaded/total*100, "total":total, "history":history})
            history += " (完了)"
    eel.update_downloading_progress({"downloading":True, "progress":100, "total":total, "history":history})
    try:shutil.move(dotmc+"/mods", dotmc+"/mods_"+now)
    except:pass
    try:shutil.move(temp_dir+"/mods", dotmc+"/mods")
    except:pass
    try:shutil.rmtree(tmp_dir)
    except:pass
    eel.update_downloading_progress({"downloading":False, "is_done":True})
    return {"success":True}

eel.start("main.html", size=(450, 550), port=59184)
