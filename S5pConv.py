import os
import sys
import json
import shutil
import codecs
import wx

#https://github.com/Yukikazari/V-Conv.git

"""def vprconv(infile, outfile):
    try:
        with open('./dic/Phonetic.json', encoding='utf-8') as f:#発音記号変換用
            pho = json.load(f)
    except FileNotFoundError:
        print('発音辞書がありません')
    try:
        with open('./dic/uPhonetic.json', encoding='utf-8') as f:#発音記号変換用
            upho = json.load(f)
    except FileNotFoundError:
        with open('./dic/uPhonetic.json', 'w') as f:
            pass
        upho = {}

    pho.update(upho)

    with open(infile, encoding='utf-8') as f:#s5p読み込み
        s5pj = json.load(f)

    vprj = {"title": "null", "masterTrack": {"samplingRate": 44100, "tempo": {"global": {"isEnabled": False, "value": 12000}, "events": []}, "timeSig": {"events": []}, "volume": {"events": [{"pos": 0, "value": 0}]}}, "voices": [{"compID": "AKR", "name": "Mishima_Furikake"}], "tracks": []}

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
    os.rename(dir_name + '.zip', outfile + '.vpr')
    shutil.rmtree("./Project/Project")"""

class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, files):
        if 
        self.window.text21.SetLabel(files[len(files) - 1])

        return 0




class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv", size=(650, 300))

        panel = wx.Panel(self, wx.ID_ANY)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        font_e = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

        infile = ''

        self.SetDropTarget(FileDrop(self))

        #Panel 1
        panel1 = wx.Panel(panel, wx.ID_ANY)
        box1 = wx.BoxSizer(wx.VERTICAL)
        
        text11 = wx.CheckBox(panel1, wx.ID_ANY, 'vpr (VOCALOID5)')
        text11.SetFont(font_e)        
        text12 = wx.CheckBox(panel1, wx.ID_ANY, 'ust (UTAU)')
        text12.SetFont(font_e)

        box1.Add(wx.StaticText(panel1, wx.ID_ANY, ""), 1)
        box1.Add(text11, 1)
        box1.Add(text12, 1)
        panel1.SetSizer(box1)
        hbox.Add(panel1, 0, wx.TOP | wx.LEFT, 10)

        #Panel 2
        panel2 = wx.Panel(panel, -1)
        box2 = wx.BoxSizer(wx.VERTICAL)

        self.text21 = wx.TextCtrl(panel2, wx.ID_ANY, infile)

        grid21 = wx.FlexGridSizer(rows=6, cols=2, gap=(0, 0))
        grid21.Add(wx.StaticText(panel2, wx.ID_ANY, "    変換元ファイル"), wx.ID_ANY, wx.EXPAND)
        grid21.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid21.Add(self.text21, wx.ID_ANY, wx.EXPAND)
        grid21.Add(wx.Button(panel2, wx.ID_ANY, "…", size=(30, -1)), wx.ID_ANY, wx.ALIGN_RIGHT)
        grid21.Add(wx.StaticText(panel2, wx.ID_ANY, ""), wx.ID_ANY, wx.EXPAND)
        grid21.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid21.AddGrowableCol(0)
        box2.Add(grid21, 1, wx.EXPAND)

        grid22 = wx.FlexGridSizer(rows=6, cols=2, gap=(0, 0))
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, "    変換先ファイル"), wx.ID_ANY, wx.EXPAND)
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.Add(wx.TextCtrl(panel2, wx.ID_ANY, "C:/"), wx.ID_ANY, wx.EXPAND)
        grid22.Add(wx.Button(panel2, wx.ID_ANY, "…", size=(30, -1)), wx.ID_ANY, wx.ALIGN_RIGHT)
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.AddGrowableCol(0)
        box2.Add(grid22, 1, wx.EXPAND | wx.TOP, 5)

        panel2.SetSizer(box2)
        hbox.Add(panel2, 1, wx.TOP, 15)

        #Panel 3
        panel3 = wx.Panel(panel, -1)
        grid3 = wx.GridSizer(rows=2, cols=1, gap=(0, 0))
        box31 = wx.BoxSizer(wx.VERTICAL)
        box32 = wx.BoxSizer(wx.VERTICAL)

        font3 = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        text31 = wx.Button(panel3, wx.ID_ANY, "変換", size=(120, 60))
        text31.SetFont(font3)
        text32 = wx.Button(panel3, wx.ID_ANY, "ノート編集", size=(120, -1))
        text32.SetFont(font_j)
        text33 = wx.Button(panel3, wx.ID_ANY, "使い方", size=(100, -1))
        text33.SetFont(font_j)
        text34 = wx.Button(panel3, wx.ID_ANY, "設定", size=(100, -1))
        text34.SetFont(font_j)

        box31.Add(wx.StaticText(panel3, wx.ID_ANY, ""))
        box31.Add(text31, flag=wx.CENTER | wx.ALIGN_TOP)
        box31.Add(text32, flag=wx.CENTER)

        box32.Add(text33, flag=wx.ALIGN_TOP | wx.CENTER)
        box32.Add(text34, flag=wx.CENTER)
        
        grid3.Add(box31, 1)
        grid3.Add(box32, 0, wx.ALIGN_BOTTOM | wx.CENTER |wx.LEFT | wx.BOTTOM, 10)
        
        panel3.SetSizer(grid3)
        hbox.Add(panel3, 0, wx.TOP | wx.RIGHT | wx.LEFT | wx.EXPAND, 10)

        panel.SetSizer(hbox)

    def OnFileSelect():
        pass


class SetFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv", size=(650, 300))

        panel = wx.Panel(self, wx.ID_ANY)
        hbox = wx.BoxSizer(wx.VERTICAL)

        hbox.Add(wx.Button(panel, wx.ID_ANY, "…", size=(30, 30)), 0, wx.ALIGN_BOTTOM)
        hbox.Add(wx.Button(panel, wx.ID_ANY, "…", size=(30, 30)), 0, wx.ALIGN_BOTTOM)
        panel.SetSizer(hbox)

class NoteFrame(wx.Frame):
    def __init__(self):
        pass


if __name__ == "__main__":

    app = wx.App()
    MainFrame().Show()
    app.MainLoop()

