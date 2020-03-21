import json
import os
import shutil
import re
import glob


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)

    if not os.path.isfile('./setting.json'):
        shutil.copy('./dic/setting.json', './setting.json')

    with open('./setting.json', encoding='utf-8') as f:  #設定
        setting = json.load(f)

    if not re.search('α0.2(\d*)', setting["version"]):
        setting["version"] = 'α0.20'
        setting["setting"]['ccsconv'] = True

        with open('./setting.json', "w") as f:
            json.dump(setting, f, indent=4)

        vconvfiles = []
        for i in sorted(glob.glob('./backup/*'), key=lambda f: os.stat(f).st_mtime, reverse=False):
            with open(i, encoding='utf-8') as fil:  #設定
                tmp = json.load(fil)
            inf = tmp["infile"]
            tmp["outccs"] = os.path.splitext(inf)[0] + '.ccs'

            with open(i, 'w') as f:
                json.dump(tmp, f)

