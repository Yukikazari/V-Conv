import os
import sys
import json
import shutil
import codecs
import wx
import copy

#https://github.com/Yukikazari/V-Conv.git

class VprConv():
    def __init__(self, window):
        self.infile = window.infile
        self.outfile = window.outvpr
        self.s5pf = window.s5pf
        self.s5pj = window.s5pj
        self.Conv()

    def Conv(self):
        vprj = {"title": "null", "masterTrack": {"samplingRate": 44100, "tempo": {"global": {"isEnabled": False, "value": 12000}, "events": []}, "timeSig": {"events": []}, "volume": {"events": [{"pos": 0, "value": 0}]}}, "voices": [{"compID": "AKR", "name": "Mishima_Furikake"}], "tracks": []}

        #トラックテンプレート
        t_temp = {"name": "akari", "volume": {"events": [{"pos": 0, "value": 0}]}, "parts": [{"pos": 30720, "duration": 168480, "styleName": "VOICEROID2 Akari", "voice": {"compID": "10980+Tax", "langID": 0}, "notes": []}]}
        fname = os.path.basename(self.infile)
        name = os.path.splitext(fname)[0]

        vprj["title"] = name #タイトル
        vprj["masterTrack"]["tempo"]["global"]["value"] = self.s5pj["tempo"][0]["beatPerMinute"] * 100
        #最初のとこ

        for i in range(len(self.s5pj["tempo"])):#テンポ
            tmp = {}
            tmp["pos"] = self.s5pj["tempo"][i]["position"]
            tmp["value"] = self.s5pj["tempo"][i]["beatPerMinute"] * 100

            vprj["masterTrack"]["tempo"]["events"].append(tmp)

        for i in range(len(self.s5pj["meter"])):  #拍子
            tmp = {}
            tmp["bar"] = self.s5pj["meter"][i]["measure"]
            tmp["numer"] = self.s5pj["meter"][i]["beatPerMeasure"]
            tmp["denom"] = self.s5pj["meter"][i]["beatGranularity"]
            vprj["masterTrack"]["timeSig"]["events"].append(tmp)

        for j in range(len(self.s5pj["tracks"])):
            vprj["tracks"].append(t_temp)
            st_sy = int(self.s5pj["tracks"][j]["notes"][0]["onset"])
            st =  int(st_sy / 2822400000)  #開始ポイント
            vprj["tracks"][j]["parts"][0]["pos"] = st * 1920 #1分57600???

            pos = int(st * 2822400000)#s5pの開始タイム

            for i in range(len(self.s5pj["tracks"][j]["notes"])):#歌詞
                tmp = {"lyric": "", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}

                tmp["lyric"] = self.s5pf["tracks"][j]["notes"][i]["lyric"]
                tmp["phoneme"] = self.s5pf["tracks"][j]["notes"][i]["phoneme"]
                tmp["pos"] = int((self.s5pj["tracks"][j]["notes"][i]["onset"] - pos) / 1470000 )#空白忘れてた
                tmp["duration"] = int(self.s5pj["tracks"][j]["notes"][i]["duration"] / 1470000)
                tmp["number"] = int(self.s5pj["tracks"][j]["notes"][i]["pitch"])
                tmp["velocity"] = int(self.s5pf["tracks"][j]["notes"][i]["velocity"])
                dur = int(tmp["pos"] + tmp["duration"])
                vprj["tracks"][j]["parts"][0]["notes"].append(tmp) 

            vprj["tracks"][j]["parts"][0]["duration"] =  dur

        dir_name = './Project'
        os.makedirs("./Project/Project", exist_ok=True)

        with codecs.open('./Project/Project/sequence.json', 'w', 'utf-8') as f:
            json.dump(vprj, f, ensure_ascii=False)

        shutil.make_archive(dir_name, 'zip', root_dir=dir_name)
        try:
            os.rename(dir_name + '.zip', self.outfile)
        except WindowsError:
            os.remove(self.outfile)
            os.rename(dir_name + '.zip', self.outfile)
        shutil.rmtree("./Project/Project")

class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, files):
        infile = files[len(files) - 1]
        if os.path.splitext(infile)[1] == '.s5p':
            self.window.infile = infile
            self.window.outvpr = os.path.splitext(infile)[0] + '.vpr'
            self.window.infile_t.SetLabel(infile)
            self.window.outvpr_t.SetLabel(os.path.splitext(infile)[0] + '.vpr')
            self.window.ReadS5p()
        return 0

class FileSelect():
    def __init__(self, window, SetId):
        self.window = window
        if SetId == 202:
            self.S5p()
        elif SetId == 212:
            self.Vpr()
        else:
            pass

    def S5p(self):
        first_path = os.path.dirname(self.window.infile)
        first_file = os.path.basename(self.window.infile)
        filter = "SynthV file(*.s5p) | *.s5p"
        dialog = wx.FileDialog(None, '開く', first_path, first_file, filter, style=wx.FD_FILE_MUST_EXIST)  #atode
        dialog.ShowModal()
        if not dialog.GetPath() == '':
            infile = dialog.GetPath()
            self.window.infile = infile
            self.window.outvpr = os.path.splitext(infile)[0] + '.vpr'
            self.window.infile_t.SetLabel(infile)
            self.window.outvpr_t.SetLabel(os.path.splitext(infile)[0] + '.vpr')
            self.window.ReadS5p()

    def Vpr(self):
        first_path = os.path.dirname(self.window.outvpr)
        first_file = os.path.basename(self.window.outvpr)
        filter = "VOCALOID5 file(*.vpr) | *.vpr"
        dialog = wx.FileDialog(None, '保存', first_path, first_file, filter, style=wx.FD_SAVE)  #atode
        dialog.ShowModal()
        if not dialog.GetPath() == '':
            outfile = dialog.GetPath()
            self.window.outvpr = outfile
            self.window.outvpr_t.SetLabel(outfile)

class MainFrame(wx.Frame):
    def __init__(self):
        self.ReadSettings()

        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv", size=(800, 300))

        panel = wx.Panel(self, wx.ID_ANY)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        font_e12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_e10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

        self.infile = ''
        self.outvpr = ''

        self.SetDropTarget(FileDrop(self))

        #Panel 1
        panel1 = wx.Panel(panel, wx.ID_ANY)

        box1_name = wx.StaticBox(panel1, wx.ID_ANY, '出力ファイル形式')
        box1_name.SetFont(font_j10)
        box1 = wx.StaticBoxSizer(box1_name, wx.VERTICAL)
        
        self.vpr_c = wx.CheckBox(panel1, 101, 'vpr (VOCALOID5)')
        self.vpr_c.SetFont(font_e12)
        self.vpr_c.SetValue(True)
        self.vpr_c.Disable()
        
        self.ust_c = wx.CheckBox(panel1, 102, 'ust (UTAU)')
        self.ust_c.SetFont(font_e12)
        self.ust_c.Disable()  #ここ

        box1.Add(self.vpr_c, 1, wx.TOP, 10)
        box1.Add(self.ust_c, 1,)
        box1.Add(wx.StaticText(panel1, wx.ID_ANY, ""))
        panel1.SetSizer(box1)
        hbox.Add(panel1, 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)

        #Panel 2
        panel2 = wx.Panel(panel, wx.ID_ANY)
        box2 = wx.BoxSizer(wx.VERTICAL)

        self.infile_t = wx.TextCtrl(panel2, 201, self.infile)
        self.infile_t.SetFont(font_j10)
        infile_b = wx.Button(panel2, 202, "…", size=(30, -1))
        infile_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

        self.outvpr_t = wx.TextCtrl(panel2, 211, self.outvpr)
        self.outvpr_t.SetFont(font_j10)
        outvpr_b = wx.Button(panel2, 212, "…", size=(30, -1))
        outvpr_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)
        outvpr_n = wx.StaticText(panel2, wx.ID_ANY, "    vprファイル")
        outvpr_n.SetFont(font_j10)

        self.outust_t = wx.TextCtrl(panel2, 221, "工事中")
        self.outust_t.SetFont(font_e10)
        outust_b = wx.Button(panel2, 222, "…", size=(30, -1))
        outust_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)
        outust_n = wx.StaticText(panel2, wx.ID_ANY, "    ustファイル")
        outust_n.SetFont(font_j10)
        self.outust_t.Disable()  #ここ
        outust_b.Disable()  #ここ


        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '変換元ファイル')
        box21_name.SetFont(font_j10)
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        grid21 = wx.FlexGridSizer(rows=1, cols=2, gap=(0, 0))
        grid21.Add(self.infile_t, wx.ID_ANY, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        grid21.Add(infile_b, wx.ID_ANY, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)
        grid21.AddGrowableCol(0)

        box21.Add(grid21, 1, wx.EXPAND | wx.BOTTOM, 7)
        box2.Add(box21, 0, wx.EXPAND)

        box22_name = wx.StaticBox(panel2, wx.ID_ANY, '変換先ファイル')
        box22_name.SetFont(font_j10)
        box22 = wx.StaticBoxSizer(box22_name, wx.VERTICAL)

        grid22 = wx.FlexGridSizer(rows=2, cols=2, gap=(0, 0))
        grid22.Add(outvpr_n)
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.Add(self.outvpr_t, wx.ID_ANY, wx.EXPAND)
        grid22.Add(outvpr_b, wx.ID_ANY, wx.ALIGN_RIGHT)
        grid22.AddGrowableCol(0)
        box22.Add(grid22, 1, wx.EXPAND | wx.BOTTOM, 10)

        grid23 = wx.FlexGridSizer(rows=2, cols=2, gap=(0, 0))
        grid23.Add(outust_n)
        grid23.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid23.Add(self.outust_t, wx.ID_ANY, wx.EXPAND)
        grid23.Add(outust_b, wx.ID_ANY, wx.ALIGN_RIGHT)
        grid23.AddGrowableCol(0)
        box22.Add(grid23, 1, wx.EXPAND | wx.BOTTOM, 10)


        box2.Add(box22, 1, wx.EXPAND)

        panel2.SetSizer(box2)
        hbox.Add(panel2, 1, wx.TOP, 10)

        #Panel 3
        panel3 = wx.Panel(panel, -1)
        grid3 = wx.GridSizer(rows=2, cols=1, gap=(0, 0))
        box31 = wx.BoxSizer(wx.VERTICAL)
        box32 = wx.BoxSizer(wx.VERTICAL)

        font3 = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

        text31 = wx.Button(panel3, wx.ID_ANY, "変換", size=(120, 60))
        text31.SetFont(font3)
        text31.Bind(wx.EVT_BUTTON, self.OnConversion)

        text32 = wx.Button(panel3, wx.ID_ANY, "ノート編集", size=(120, -1))
        text32.SetFont(font_j12)

        text33 = wx.Button(panel3, wx.ID_ANY, "使い方", size=(100, -1))
        text33.SetFont(font_j12)
        text33.Disable()

        text34 = wx.Button(panel3, wx.ID_ANY, "設定", size=(100, -1))
        text34.SetFont(font_j12)
        text34.Bind(wx.EVT_BUTTON, self.OnSettings)


        box31.Add(wx.StaticText(panel3, wx.ID_ANY, ""))
        box31.Add(text31, flag=wx.CENTER | wx.ALIGN_TOP)
        box31.Add(text32, flag=wx.CENTER)

        box32.Add(text33, flag=wx.ALIGN_TOP | wx.CENTER)
        box32.Add(text34, flag=wx.CENTER)
        
        grid3.Add(box31, 1)
        grid3.Add(box32, 0, wx.ALIGN_BOTTOM | wx.CENTER |wx.LEFT | wx.BOTTOM, 10)
        
        panel3.SetSizer(grid3)
        hbox.Add(panel3, 0,wx.RIGHT | wx.LEFT | wx.EXPAND, 10)

        panel.SetSizer(hbox)

        self.Centre()

    def ReadSettings(self):
        self.base = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.base)
        try:
            with open('./dic/Phonetic.json', encoding='utf-8') as f:#発音記号変換用
                self.pho = json.load(f)
        except FileNotFoundError:
            print('発音辞書がありません')
        try:
            with open('./dic/uPhonetic.json', encoding='utf-8') as f:#発音記号変換用
                upho = json.load(f)
        except FileNotFoundError:
            with open('./dic/uPhonetic.json', 'w') as f:
                pass
            upho = {}

        self.pho.update(upho)

        if not os.path.isfile('./setting.json'):
            shutil.copy('./dic/setting.json', './setting.json')

        with open('./setting.json', encoding='utf-8') as f:  #設定
            self.setting = json.load(f)

    def ReadS5p(self):
        with open(self.infile, encoding='utf-8') as f:#s5p読み込み
            self.s5pj = json.load(f)

        self.s5pf = {"tracks": []}
        
        for j in range(len(self.s5pj["tracks"])):
            self.s5pf["tracks"].append({"notes": []})     

            for i in range(len(self.s5pj["tracks"][j]["notes"])):#歌詞
                tmp = {"lyric": "", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}
                lyric = self.s5pj["tracks"][j]["notes"][i]["lyric"]
                tmp["lyric"] = lyric
                tmp["phoneme"] = self.pho[lyric]
                tmp["pos"] = int(self.s5pj["tracks"][j]["notes"][i]["onset"] / 1470000)#空白忘れてた
                tmp["duration"] = int(self.s5pj["tracks"][j]["notes"][i]["duration"] / 1470000)
                tmp["number"] = int(self.s5pj["tracks"][j]["notes"][i]["pitch"])
                self.s5pf["tracks"][j]["notes"].append(tmp)

    def OnSelectFiles(self, event):
        SetId = event.GetId()
        FileSelect(self, SetId)

    def OnConversion(self, event):
        self.outvpr = self.outvpr_t.GetValue()
        outfiles = ''
        if self.vpr_c.GetValue() == True:
            if os.path.isfile(self.outvpr) == True:
                dlg = wx.MessageDialog(None, os.path.basename(self.outvpr) + "は既に存在します。上書きしますか？", "上書き確認", wx.YES_NO | wx.ICON_INFORMATION)
                res = dlg.ShowModal()
                dlg.Destroy()
                if res == wx.ID_YES:
                    VprConv(self)
                    outfiles += os.path.basename(self.outvpr) + '\n'
            else:
                VprConv(self)
                outfiles += os.path.basename(self.outvpr) + '\n'


        if self.ust_c.GetValue() == True:
            outfiles += os.path.basename(self.outust) + '\n'
            pass
        if not outfiles == '':
            FinishDialog(outfiles)

    def OnSettings(self, event):
        SetFrame(self).Show()

class SetFrame(wx.Frame):
    def __init__(self, window):
        self.setting = copy.deepcopy(window.setting)
        self.window = window

        wx.Frame.__init__(self, window, wx.ID_ANY, "設定", size=(400, 300))
        notebook = wx.Notebook(self, wx.ID_ANY)
        font_e12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_e10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

        panel1 = wx.Panel(notebook, wx.ID_ANY)
        panel2 = wx.Panel(notebook, wx.ID_ANY)

        notebook.InsertPage(0, panel1, '保存設定')
        notebook.InsertPage(1, panel2, 'ノート編集')

        box1 = wx.BoxSizer(wx.VERTICAL)
        box11_name = wx.StaticBox(panel1, wx.ID_ANY, '保存先フォルダ設定')
        box11 = wx.StaticBoxSizer(box11_name, wx.VERTICAL)
        grid11 = wx.FlexGridSizer(rows=1, cols=2, gap=(0,0))

        self.cb111 = wx.CheckBox(panel1, wx.ID_ANY, '保存先フォルダを固定する')
        self.cb111.SetFont(font_j10)
        self.cb111.Bind(wx.EVT_CHECKBOX, self.OnChangecb111)
        self.text111 = wx.TextCtrl(panel1, wx.ID_ANY, "")
        self.text111.SetFont(font_j10)
        self.btn111 = wx.Button(panel1, wx.ID_ANY, "…", size=(30, -1))
        self.btn111.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

        grid11.Add(self.text111, 1, wx.EXPAND)
        grid11.Add(self.btn111, 0, wx.ALIGN_RIGHT)
        grid11.AddGrowableCol(0)

        box11.Add(self.cb111, 1)
        box11.Add(grid11, 1, wx.EXPAND)


            
        box1.Add(box11, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        box1n = wx.BoxSizer(wx.HORIZONTAL)
        btn1y = wx.Button(panel1, wx.ID_ANY, "決定", size=(80, -1))
        btn1y.SetFont(font_j10)
        btn1n = wx.Button(panel1, wx.ID_ANY, "キャンセル", size=(80, -1))
        btn1n.SetFont(font_j10)

        box1n.Add(btn1y, 0, wx.ALIGN_BOTTOM)
        box1n.Add(btn1n, 0, wx.ALIGN_BOTTOM | wx.LEFT, 10)

        box1.Add(box1n, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 10)


        panel1.SetSizer(box1)

        box2 = wx.BoxSizer(wx.VERTICAL)

        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '無声化設定')
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        cb21 = wx.CheckBox(panel2, wx.ID_ANY, '文字種による無声化を有効にする')
        cb21.SetFont(font_j10)

        grid21 = wx.FlexGridSizer()

        box21.Add(cb21, 0, wx.EXPAND)
        box2.Add(box21, 0, wx.EXPAND | wx.ALL, 10)        
        
        box22_name = wx.StaticBox(panel2, wx.ID_ANY, '編集拡張')
        box22 = wx.StaticBoxSizer(box22_name, wx.VERTICAL)

        cb22 = wx.CheckBox(panel2, wx.ID_ANY, 'ベロシティの変更を有効にする')
        cb22.SetFont(font_j10)

        box22.Add(cb22, 0, wx.EXPAND)
        box2.Add(box22, 0, wx.EXPAND | wx.ALL, 10)

        panel2.SetSizer(box2)

        self.Bind(wx.EVT_CLOSE, self.frame_close)
        self.Centre()


    def OnSelectFiles(self, event):
       	text = self.text111
        try:
            path = os.path.dirname(text)
        except TypeError:
            path = os.path.dirname(os.path.abspath(__file__)) + "/Files"

        dialog = wx.DirDialog(None, '開く', path, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)  #atode
        dialog.ShowModal()
        self.text111.SetValue(dialog.GetPath())
        self.setting["setting"]["dir_fix"] = dialog.GetPath()


    def OnChangecb111(self, event):
        if self.cb111.GetValue() == True:
            self.text111.Enable()
            self.btn111.Enable()
        else:
            self.text111.Disable()
            self.btn111.Disable()
            
    def frame_close(self, event):

        self.Destroy()
     
class NoteFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "ノート編集", size=(400, 300))

        panel = wx.Panel(self, wx.ID_ANY)
        vbox = wx.BoxSizer(wx.VERTICAL)
        font_e = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

class FinishDialog(wx.Frame):
    def __init__(self, file):
        wx.MessageBox( file + "\n変換が完了しました")

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    #SetFrame().Show()
    app.MainLoop()


