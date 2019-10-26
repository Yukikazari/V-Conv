import os
import json
import shutil
import codecs

#tmpはチンポの略だとあれほど

try:
    with open('./dic/Phonetic.json', encoding='utf-8') as f:#発音記号変換用
        pho = json.load(f)
except FileNotFoundError:
    print('発音辞書がありません')
    key = input('Enter')
    sys.exit()

with open(r'E:\どうが\歌うボイスロイド\utau支援\開発環境\hito.s5p', encoding='utf-8') as f:#s5p読み込み
    s5pj = json.load(f)

vprj = {"title": "null", "masterTrack": {"samplingRate": 44100, "tempo": {"global": {"isEnabled": False, "value": 12000}, "events": []}, "timeSig": {"events": []}, "volume": {"events": [{"pos": 0, "value": 0}]}}, "voices": [{"compID": "AKR", "name": "Mishima_Furikake"}], "tracks": []}

with open('./dic/Phonetic.json', encoding='utf-8') as f:#発音記号変換用
    pho = json.load(f)

#トラックテンプレート
t_temp = {"name": "akari", "volume": {"events": [{"pos": 0, "value": 0}]}, "parts": [{"pos": 30720, "duration": 168480, "styleName": "VOICEROID2 Akari", "voice": {"compID": "10980+Tax", "langID": 0}, "notes": []}]}

name = os.path.splitext("north.s5p")[0]

vprj["title"] = name #タイトル
vprj["masterTrack"]["tempo"]["global"]["value"] = s5pj["tempo"][0]["beatPerMinute"] * 100
#最初のとこ

for i in range(len(s5pj["tempo"])):#テンポ
    tmp = {}
    tmp["pos"] = s5pj["tempo"][i]["position"]
    tmp["value"] = s5pj["tempo"][i]["beatPerMinute"] * 100

    vprj["masterTrack"]["tempo"]["events"].append(tmp)

for i in range(len(s5pj["meter"])):  #拍子
    tmp = {}
    tmp["bar"] = s5pj["meter"][i]["measure"]
    tmp["numer"] = s5pj["meter"][i]["beatPerMeasure"]
    tmp["denom"] = s5pj["meter"][i]["beatGranularity"]
    vprj["masterTrack"]["timeSig"]["events"].append(tmp)

for j in range(len(s5pj["tracks"])):
    vprj["tracks"].append(t_temp)
    st_sy = int(s5pj["tracks"][j]["notes"][0]["onset"])
    st =  int(st_sy / 2822400000)  #開始ポイント
    vprj["tracks"][j]["parts"][0]["pos"] = st * 1920 #1分57600???

    pos = int(st * 2822400000)#s5pの開始タイム

    for i in range(len(s5pj["tracks"][j]["notes"])):#歌詞
        tmp = {"lyric": "", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}
        lyric = s5pj["tracks"][j]["notes"][i]["lyric"]
        tmp["lyric"] = lyric
        tmp["phoneme"] = pho[lyric]
        tmp["pos"] = int((s5pj["tracks"][j]["notes"][i]["onset"] - pos) / 1470000 )#空白忘れてた
        tmp["duration"] = int(s5pj["tracks"][j]["notes"][i]["duration"] / 1470000)
        tmp["number"] = int(s5pj["tracks"][j]["notes"][i]["pitch"])
        dur = int(tmp["pos"] + tmp["duration"])
        vprj["tracks"][j]["parts"][0]["notes"].append(tmp) 

    vprj["tracks"][j]["parts"][0]["duration"] =  dur

dir_name = './Project'
os.makedirs("./Project/Project", exist_ok=True)

with codecs.open('./Project/Project/sequence.json', 'w', 'utf-8') as f:
    json.dump(vprj, f, ensure_ascii=False)

shutil.make_archive(dir_name, 'zip', root_dir=dir_name)
os.rename(dir_name + '.zip', dir_name + '.vpr')