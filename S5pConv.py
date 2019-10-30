import os
import sys
import json
import shutil
import codecs
import wx
import wx.lib.scrolledpanel as scrolled
import copy

#https://github.com/Yukikazari/V-Conv.git

#めも　あとでファイルの時間ソートと表示と選択時処理を入れる。入れて。

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
                print(self.s5pf["tracks"][j]["notes"][i]["phoneme"])
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
        if self.window.infile == '':
            first_path = os.path.dirname(self.window.setting['setting']['infile'])
            first_file = ''
        else:
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

        self.setting_now = 0
        self.note_now = 0
        self.infile = ''
        self.outvpr = ''

        #Font
        font_e12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_e10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_go = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        
        #Frame
        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv", size=(800, 300))
        panel = wx.Panel(self, wx.ID_ANY)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
              

        #Panel_1
        panel1 = wx.Panel(panel, wx.ID_ANY)

        box1_name = wx.StaticBox(panel1, wx.ID_ANY, '出力ファイル形式')        
        box1 = wx.StaticBoxSizer(box1_name, wx.VERTICAL)

        #Panel_1 object
        self.vpr_c = wx.CheckBox(panel1, 101, 'vpr (VOCALOID5)')
        self.ust_c = wx.CheckBox(panel1, 102, 'ust (UTAU)')

        #Panel_1 setting
        box1_name.SetFont(font_j10)

        self.vpr_c.SetFont(font_e12)
        self.vpr_c.Disable()
        
        self.ust_c.SetFont(font_e12)
        self.ust_c.Disable()

        #Panel_1 event
        self.vpr_c.Bind(wx.EVT_CHECKBOX, self.OnSelectConv)
        self.ust_c.Bind(wx.EVT_CHECKBOX, self.OnSelectConv)

        #Panel_1 layout
        box1.Add(self.vpr_c, 1, wx.TOP, 10)
        box1.Add(self.ust_c, 1,)
        box1.Add(wx.StaticText(panel1, wx.ID_ANY, ""))
        panel1.SetSizer(box1)

        hbox.Add(panel1, 0, wx.TOP | wx.LEFT | wx.RIGHT, 10)


        #Panel_2
        panel2 = wx.Panel(panel, wx.ID_ANY)
        box2 = wx.BoxSizer(wx.VERTICAL)

        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '変換元ファイル')
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        box22_name = wx.StaticBox(panel2, wx.ID_ANY, '変換先ファイル')
        box22 = wx.StaticBoxSizer(box22_name, wx.VERTICAL)

        grid21 = wx.FlexGridSizer(rows=1, cols=2, gap=(0, 0))
        grid22 = wx.FlexGridSizer(rows=2, cols=2, gap=(0, 0))
        grid23 = wx.FlexGridSizer(rows=2, cols=2, gap=(0, 0))
           
        #Panel_2 object
        self.infile_t = wx.TextCtrl(panel2, 201, self.infile)
        infile_b = wx.Button(panel2, 202, "…", size=(30, -1))

        self.outvpr_t = wx.TextCtrl(panel2, 211, self.outvpr)
        self.outvpr_b = wx.Button(panel2, 212, "…", size=(30, -1))
        outvpr_n = wx.StaticText(panel2, wx.ID_ANY, "    vprファイル")

        self.outust_t = wx.TextCtrl(panel2, 221, "工事中")
        self.outust_b = wx.Button(panel2, 222, "…", size=(30, -1))
        outust_n = wx.StaticText(panel2, wx.ID_ANY, "    ustファイル")

        #Panel_2 setting
        box21_name.SetFont(font_j10)
        box22_name.SetFont(font_j10)

        self.infile_t.SetFont(font_j10)

        self.outvpr_t.SetFont(font_j10)
        outvpr_n.SetFont(font_j10)

        self.outust_t.SetFont(font_e10)    
        outust_n.SetFont(font_j10)

        #Panel_2 event
        infile_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)
        self.outvpr_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)
        self.outust_b.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

        #Panel_2 layout
        grid21.Add(self.infile_t, wx.ID_ANY, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        grid21.Add(infile_b, wx.ID_ANY, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)
        grid21.AddGrowableCol(0)

        grid22.Add(outvpr_n)
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.Add(self.outvpr_t, wx.ID_ANY, wx.EXPAND)
        grid22.Add(self.outvpr_b, wx.ID_ANY, wx.ALIGN_RIGHT)
        grid22.AddGrowableCol(0)

        grid23.Add(outust_n)
        grid23.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid23.Add(self.outust_t, wx.ID_ANY, wx.EXPAND)
        grid23.Add(self.outust_b, wx.ID_ANY, wx.ALIGN_RIGHT)
        grid23.AddGrowableCol(0)

        box21.Add(grid21, 1, wx.EXPAND | wx.BOTTOM, 7)

        box22.Add(grid22, 1, wx.EXPAND | wx.BOTTOM, 10)
        box22.Add(grid23, 1, wx.EXPAND | wx.BOTTOM, 10)        

        box2.Add(box21, 0, wx.EXPAND)
        box2.Add(box22, 1, wx.EXPAND)

        panel2.SetSizer(box2)
        hbox.Add(panel2, 1, wx.TOP, 10)


        #Panel_3
        panel3 = wx.Panel(panel, -1)

        grid3 = wx.GridSizer(rows=2, cols=1, gap=(0, 0))

        box31 = wx.BoxSizer(wx.VERTICAL)
        box32 = wx.BoxSizer(wx.VERTICAL)

        #Panel_3 object
        text31 = wx.Button(panel3, wx.ID_ANY, "変換", size=(120, 60))
        text32 = wx.Button(panel3, wx.ID_ANY, "ノート編集", size=(120, -1))
        text33 = wx.Button(panel3, wx.ID_ANY, "使い方", size=(100, -1))
        text34 = wx.Button(panel3, wx.ID_ANY, "設定", size=(100, -1))

        #Panel_3 setting
        text31.SetFont(font_go)
        text32.SetFont(font_j12)
        text33.SetFont(font_j12)
        text33.Disable()
        text34.SetFont(font_j12)

        #Panel_3 event
        text31.Bind(wx.EVT_BUTTON, self.OnConversion)
        text32.Bind(wx.EVT_BUTTON, self.OnNote)
        #text33.Bind(wx.EVT_BUTTON, self.OnHelp)
        text34.Bind(wx.EVT_BUTTON, self.OnSettings)

        #Panel_3 layout
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

        self.SetValues()

        self.Bind(wx.EVT_CLOSE, self.AppClose)
        self.SetDropTarget(FileDrop(self))
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

    def SetValues(self):
        #Panel_1
        self.vpr_c.SetValue(self.setting["setting"]["vprconv"])
        self.ust_c.SetValue(self.setting["setting"]["ustconv"])
        self.OnSelectConv('')

    def ReadS5p(self):
        with open(self.infile, encoding='utf-8') as f:#s5p読み込み
            self.s5pj = json.load(f)

        self.s5pf = {"tracks": []}
        
        for j in range(len(self.s5pj["tracks"])):
            self.s5pf["tracks"].append({"notes": []})     

            for i in range(len(self.s5pj["tracks"][j]["notes"])):#歌詞
                tmp = {"lyric": "", "lyric_hira":"", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}
                lyric = self.s5pj["tracks"][j]["notes"][i]["lyric"]
                tmp["lyric"] = lyric
                tmp["phoneme"] = self.pho["normal"][lyric]
                tmp["pos"] = int(self.s5pj["tracks"][j]["notes"][i]["onset"] / 1470000)#空白忘れてた
                tmp["duration"] = int(self.s5pj["tracks"][j]["notes"][i]["duration"] / 1470000)
                tmp["number"] = int(self.s5pj["tracks"][j]["notes"][i]["pitch"])
    #lyric_hira, phoneme , velocity未設定
                self.s5pf["tracks"][j]["notes"].append(tmp)

    def OnSelectFiles(self, event):
        SetId = event.GetId()
        FileSelect(self, SetId)

    def OnSelectConv(self, event):
        if self.vpr_c.GetValue() == True:
            self.outvpr_t.Enable()
            self.outvpr_b.Enable()
        else:
            self.outvpr_t.Disable()
            self.outvpr_b.Disable()

        if self.ust_c.GetValue() == True:
            self.outust_t.Enable()
            self.outust_b.Enable()
        else:
            self.outust_t.Disable()
            self.outust_b.Disable()

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
            #UstConv(self)
            outfiles += os.path.basename(self.outust) + '\n'
            pass
        if not outfiles == '':
            FinishDialog(outfiles)

    def OnNote(self, event):
        self.note_now = 1
        NoteFrame(self).Show()

    def OnSettings(self, event):
        if self.setting_now == 0:
            self.setting_now = 1
            SetFrame(self).Show()

    def AppClose(self, event):
        with open('./setting.json', "w") as f:
            json.dump(self.setting, f, indent=4)

        try:
            self.setting["tracks"] = self.s5pf["tracks"]
            backup = self.base + './backup/' + os.path.basename(self.infile) + '.vconv'
            with open(backup, 'w') as f:
                json.dump(self.setting, f)
        except AttributeError:
            pass
        
        self.Destroy()


class SetFrame(wx.Frame):
    def __init__(self, window):
        self.setting = copy.deepcopy(window.setting)
        self.window = window

        #Font
        font_e12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_e10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")

        #Frame
        wx.Frame.__init__(self, window, wx.ID_ANY, "設定", size=(400, 400), style= wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL)
        notebook = wx.Notebook(self, wx.ID_ANY)

        panel1 = wx.Panel(notebook, wx.ID_ANY)
        panel2 = wx.Panel(notebook, wx.ID_ANY)

        notebook.InsertPage(0, panel1, '保存設定')
        notebook.InsertPage(1, panel2, 'ノート編集')

        #Panel_1
        box1 = wx.BoxSizer(wx.VERTICAL)
        box11_name = wx.StaticBox(panel1, wx.ID_ANY, '保存先フォルダ設定')
        box11 = wx.StaticBoxSizer(box11_name, wx.VERTICAL)
        grid11 = wx.FlexGridSizer(rows=1, cols=2, gap=(0, 0))
        box1n = wx.BoxSizer(wx.HORIZONTAL)
              
        #Panel_1 object
        self.cb111 = wx.CheckBox(panel1, wx.ID_ANY, '保存先フォルダを固定する')

        self.text111 = wx.TextCtrl(panel1, wx.ID_ANY, self.setting["setting"]["dir_fix"])        
        self.btn111 = wx.Button(panel1, wx.ID_ANY, "…", size=(30, -1))

        btn1y = wx.Button(panel1, 1000, "決定", size=(80, -1))
        btn1n = wx.Button(panel1, wx.ID_ANY, "キャンセル", size=(80, -1))

        #Panel_1 setting
        self.cb111.SetFont(font_j10)      

        self.text111.SetFont(font_j10)

        btn1y.SetFont(font_j10)
        btn1n.SetFont(font_j10)

        #Panel_1 event
        self.cb111.Bind(wx.EVT_CHECKBOX, self.OnChangecb111)
        self.btn111.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

        btn1y.Bind(wx.EVT_BUTTON, self.OnClose)
        btn1n.Bind(wx.EVT_BUTTON, self.OnClose)                        

        #Panel_1 layout
        grid11.Add(self.text111, 1, wx.EXPAND)
        grid11.Add(self.btn111, 0, wx.ALIGN_RIGHT)
        grid11.AddGrowableCol(0)

        box11.Add(self.cb111, 1)
        box11.Add(grid11, 1, wx.EXPAND)

        box1n.Add(btn1y, 0, wx.ALIGN_BOTTOM)
        box1n.Add(btn1n, 0, wx.ALIGN_BOTTOM | wx.LEFT, 10)        
       
        box1.Add(box11, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        box1.Add(box1n, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 10)

        panel1.SetSizer(box1)

        #Panel_2

        box2 = wx.BoxSizer(wx.VERTICAL)

        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '無声化設定')
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        box22_name = wx.StaticBox(panel2, wx.ID_ANY, '編集拡張')
        box22 = wx.StaticBoxSizer(box22_name, wx.VERTICAL)

        grid21 = wx.FlexGridSizer(rows=3, cols=2, gap=(0, 0))

        box2n = wx.BoxSizer(wx.HORIZONTAL)

        element = ('なし', '全体無声化', '1文字目無声化', '長音無声化')
        
        #Panel_2 object
        self.cb21 = wx.CheckBox(panel2, wx.ID_ANY, '文字種による無声化を有効にする')        

        text211 = wx.StaticText(panel2, wx.ID_ANY, '   ひらがな：')
        text212 = wx.StaticText(panel2, wx.ID_ANY, '   カタカナ：')
        text213 = wx.StaticText(panel2, wx.ID_ANY, '   その他　：')

        self.cbox211 = wx.ComboBox(panel2, wx.ID_ANY, self.setting["setting"]["dev_hira"], choices=element, style=wx.CB_READONLY)
        self.cbox212 = wx.ComboBox(panel2, wx.ID_ANY, self.setting["setting"]["dev_kata"], choices=element, style=wx.CB_READONLY)
        self.cbox213 = wx.ComboBox(panel2, wx.ID_ANY, self.setting["setting"]["dev_other"], choices=element, style=wx.CB_READONLY)

        self.cb22 = wx.CheckBox(panel2, wx.ID_ANY, 'ベロシティの変更を有効にする')

        btn2y = wx.Button(panel2, 1000, "決定", size=(80, -1))
        btn2n = wx.Button(panel2, wx.ID_ANY, "キャンセル", size=(80, -1))

        #Panel_2 setting
        self.cb21.SetFont(font_j10)

        text211.SetFont(font_j10)
        text212.SetFont(font_j10)
        text213.SetFont(font_j10)        

        self.cb22.SetFont(font_j10)

        btn2y.SetFont(font_j10)
        btn2n.SetFont(font_j10)

        #Panel_2 event
        self.cb21.Bind(wx.EVT_CHECKBOX, self.OnSelectCb21)

        btn2y.Bind(wx.EVT_BUTTON, self.OnClose)
        btn2n.Bind(wx.EVT_BUTTON, self.OnClose)

        #Panel_2 layout
        grid21.Add(text211, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        grid21.Add(self.cbox211, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)        
        grid21.Add(text212, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        grid21.Add(self.cbox212, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)        
        grid21.Add(text213, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        grid21.Add(self.cbox213, 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)

        box21.Add(self.cb21, 0, wx.EXPAND)
        box21.Add(grid21, 0, wx.EXPAND)
      
        box22.Add(self.cb22, 0, wx.EXPAND | wx.BOTTOM, 5)

        box2n.Add(btn2y, 0, wx.ALIGN_BOTTOM)
        box2n.Add(btn2n, 0, wx.ALIGN_BOTTOM | wx.LEFT, 10)

        box2.Add(box21, 0, wx.EXPAND | wx.ALL, 10)  
        box2.Add(box22, 0, wx.EXPAND | wx.ALL, 10)
        box2.Add(box2n, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 10)

        panel2.SetSizer(box2)


        self.SetValues()
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def SetValues(self):
        #Panel_1
        self.cb111.SetValue(self.setting["setting"]["dir"])
        if self.setting["setting"]["dir"] == False:
            self.text111.Disable()
            self.btn111.Disable()

        self.cb21.SetValue(self.setting["setting"]["dev"])
        if self.setting["setting"]["dev"] == False:
            self.cbox211.Disable()
            self.cbox212.Disable()
            self.cbox213.Disable()

        self.cb22.SetValue(self.setting["setting"]["velocity"])


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

    def OnSelectCb21(self, event):
        if self.cb21.GetValue() == True:
            self.cbox211.Enable()
            self.cbox212.Enable()
            self.cbox213.Enable()
        else:
            self.cbox211.Disable()
            self.cbox212.Disable()
            self.cbox213.Disable()
            
    def OnClose(self, event):       
        if event.GetId() == 1000:
            self.setting["setting"]["dir"] = self.cb111.GetValue()
            self.setting["setting"]["dev"] = self.cb21.GetValue()
            self.setting["setting"]["dev_hira"] = self.cbox211.GetValue()
            self.setting["setting"]["dev_kata"] = self.cbox212.GetValue()
            self.setting["setting"]["dev_other"] = self.cbox213.GetValue()
            self.setting["setting"]["velocity"] = self.cb22.GetValue()
            self.window.setting = self.setting
            
        self.window.setting_now = 0
        self.Destroy()

     
class NoteFrame(wx.Frame):
    def __init__(self, window):
        self.window = window
        self.FirstSettings()
        self.element = ["トラック1"]



        #Frame 親変更 , style= wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, window, wx.ID_ANY, "ノート編集", size=(850, 600) , style= wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL)
        panel = wx.Panel(self, wx.ID_ANY)
        box_root = wx.BoxSizer(wx.HORIZONTAL)

        #左側
        box_left = wx.BoxSizer(wx.VERTICAL)

        select = wx.ComboBox(panel, wx.ID_ANY, "トラック1", choices=self.element, style=wx.CB_READONLY)


        #Panel_1
        panel1 = scrolled.ScrolledPanel(panel, wx.ID_ANY, size=(150, 300))
        panel1.SetupScrolling()
        box1 = wx.BoxSizer(wx.VERTICAL)
        
        text = wx.RadioButton(panel1, wx.ID_ANY, "あああ")
        text.SetBackgroundColour("#b0b0b0")
        
        box1.Add(text, 0, wx.EXPAND)
        panel1.SetSizer(box1)
        panel1.SetBackgroundColour("#ffffff")

        box_left.Add(select, 0, wx.ALL, 10)        
        box_left.Add(panel1, 0, wx.LEFT, 10) 

        box_root.Add(box_left)

        panels = []
        grid = []
        text0 = []
        text1 = []
        text2 = []
        text3 = []
        text4 = []
        text5 = []
        text6 = []
        text7 = []
        text8 = []
        text9 = []

        self.note_0 = []
        self.note_1 = []
        self.note_2 = []
        self.note_3 = []
        self.note_4 = []
        self.note_5 = []
        self.note_6 = []
        self.note_7 = []
        self.note_8 = []
        self.note_9 = []

        #右側
        for i in range(5):
            panels.append(i)
            grid.append(i)
            text0.append(i)
            text1.append(i)
            text2.append(i)
            text3.append(i)
            text4.append(i)
            text5.append(i)
            text6.append(i)
            text7.append(i)
            text8.append(i)
            text9.append(i)

            panels[i] = scrolled.ScrolledPanel(panel, wx.ID_ANY)
            panels[i].SetupScrolling()
            grid[i] = wx.FlexGridSizer(rows=1, cols=10, gap=(0, 0))  

            text0[i] = wx.StaticText(panels[i], wx.ID_ANY, '歌詞', style=wx.TE_CENTER, size=(80,-1))
            text1[i] = wx.StaticText(panels[i], wx.ID_ANY, 'よみ', style=wx.TE_CENTER, size=(80,-1))
            text2[i] = wx.StaticText(panels[i], wx.ID_ANY, '発音', style=wx.TE_CENTER, size=(80,-1))
            text3[i] = wx.StaticText(panels[i], wx.ID_ANY, '長さ', style=wx.TE_CENTER, size=(80,-1))
            text4[i] = wx.StaticText(panels[i], wx.ID_ANY, '高さ', style=wx.TE_CENTER, size=(80,-1))
            text5[i] = wx.StaticText(panels[i], wx.ID_ANY, '', size=(10,-1))
            text6[i] = wx.StaticText(panels[i], wx.ID_ANY, 'なし', style=wx.TE_CENTER, size=(50,-1))
            text7[i] = wx.StaticText(panels[i], wx.ID_ANY, '全体\n無声化', style=wx.TE_CENTER, size=(50,-1))
            text8[i] = wx.StaticText(panels[i], wx.ID_ANY, '1文字目\n無声化', style=wx.TE_CENTER, size=(50,-1))
            text9[i] = wx.StaticText(panels[i], wx.ID_ANY, '長音\n無声化', style=wx.TE_CENTER, size=(50,-1))

            grid[i].Add(text0[i], 0, wx.TOP, 5)
            grid[i].Add(text1[i], 0, wx.TOP, 5)
            grid[i].Add(text2[i], 0, wx.TOP, 5)
            grid[i].Add(text3[i], 0, wx.TOP, 5)
            grid[i].Add(text4[i], 0, wx.TOP, 5)
            grid[i].Add(text5[i], 0, wx.TOP, 5)
            grid[i].Add(text6[i], 0, wx.TOP, 5)
            grid[i].Add(text7[i])
            grid[i].Add(text8[i])
            grid[i].Add(text9[i])

            for j in range(i*100, i*100+100):
                self.note_0.append([j])
                self.note_1.append([j])
                self.note_2.append([j])
                self.note_3.append([j])
                self.note_4.append([j])
                self.note_5.append([j])
                self.note_6.append([j])
                self.note_7.append([j])
                self.note_8.append([j])
                self.note_9.append([j])

                self.note_0[j] = wx.TextCtrl(panels[i], j * 10, self.window.s5pf["tracks"][0]["notes"][j]["lyric"])
                self.note_1[j] = wx.TextCtrl(panels[i], j * 10 + 1, self.window.s5pf["tracks"][0]["notes"][j]["lyric_hira"])
                self.note_2[j] = wx.StaticText(panels[i], j * 10 + 2, self.window.s5pf["tracks"][0]["notes"][j]["phoneme"])
                self.note_3[j] = wx.StaticText(panels[i], j * 10 + 3, str(self.window.s5pf["tracks"][0]["notes"][j]["duration"]))
                self.note_4[j] = wx.StaticText(panels[i], j * 10 + 4, str(self.window.s5pf["tracks"][0]["notes"][j]["number"]))
                self.note_5[j] = wx.StaticText(panels[i], j * 10 + 5, "")
                self.note_6[j] = wx.RadioButton(panels[i], j * 10 + 6, "", style=wx.RB_GROUP)
                self.note_7[j] = wx.RadioButton(panels[i], j * 10 + 7, "")
                self.note_8[j] = wx.RadioButton(panels[i], j * 10 + 8, "")
                self.note_9[j] = wx.RadioButton(panels[i], j * 10 + 9, "")

                grid[i].Add(note_0[j])
                grid[i].Add(note_1[j])
                grid[i].Add(note_2[j])
                grid[i].Add(note_3[j])
                grid[i].Add(note_4[j])
                grid[i].Add(note_5[j])
                grid[i].Add(note_6[j])
                grid[i].Add(note_7[j])
                grid[i].Add(note_8[j])
                grid[i].Add(note_9[j])

            panels[i].SetSizer(grid[i])
            panels[i].Hide()


        box_root.Add(panels[0], 1, wx.EXPAND | wx.ALL, 10)

        panels[0].Show()
        panel.SetSizer(box_root)

        self.Centre()

        #select.Bind(wx.EVT_COMBOBOX, )





    def FirstSettings(self):
        self.st_time = self.window.s5pf["tracks"][0]["notes"][0]["pos"]
        pos = self.st_time
        self.notescount = 0
        for i in range(len(self.window.s5pf["tracks"][0]["notes"])):
            self.notescount += 1
            if not pos == self.window.s5pf["tracks"][0]["notes"][i]["pos"]:
                pos == self.window.s5pf["tracks"][0]["notes"][i]["pos"]
                self.notescount += 1

        self.element = []
        for i in range(len(self.window.s5pf["tracks"])):
            self.element.append("トラック" + str(i + 1))



class FinishDialog():
    def __init__(self, file):
        wx.MessageBox( file + "\n変換が完了しました")


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    #SetFrame().Show()
    #NoteFrame().Show()
    app.MainLoop()







"""        for i in range(20):
            self.note_0.append(i)
            self.note_1.append(i)
            self.note_2.append(i)
            self.note_3.append(i)
            self.note_4.append(i)
            self.note_5.append(i)
            self.note_6.append(i)
            self.note_7.append(i)
            self.note_8.append(i)
            self.note_9.append(i)

            self.note_0[i, j] = wx.TextCtrl(panel, i * 10, self.window.s5pf["tracks"][0]["notes"][i, j]["lyric"])
            self.note_1[i, j] = wx.TextCtrl(panel, i * 10 + 1, self.window.s5pf["tracks"][0]["notes"][i, j]["lyric_hira"])
            self.note_2[i, j] = wx.StaticText(panel, i * 10 + 2, self.window.s5pf["tracks"][0]["notes"][i, j]["phoneme"])
            self.note_3[i, j] = wx.StaticText(panel, i * 10 + 3, str(self.window.s5pf["tracks"][0]["notes"][i, j]["duration"]))
            self.note_4[i, j] = wx.StaticText(panel, i * 10 + 4, str(self.window.s5pf["tracks"][0]["notes"][i, j]["number"]))
            self.note_5[i, j] = wx.StaticText(panel, i * 10 + 5, "")
            self.note_6[i, j] = wx.RadioButton(panel, i * 10 + 6, "", style=wx.RB_GROUP)
            self.note_7[i, j] = wx.RadioButton(panel, i * 10 + 7, "")
            self.note_8[i, j] = wx.RadioButton(panel, i * 10 + 8, "")
            self.note_9[i, j] = wx.RadioButton(panel, i * 10 + 9, "")

            grid.Add(note_0[i, j])
            grid.Add(note_1[i, j])
            grid.Add(note_2[i, j])
            grid.Add(note_3[i, j])
            grid.Add(note_4[i, j])
            grid.Add(note_5[i, j])
            grid.Add(note_6[i, j])
            grid.Add(note_7[i, j])
            grid.Add(note_8[i, j])
            grid.Add(note_9[i, j])
"""