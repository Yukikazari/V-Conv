import os
import sys
import json
import shutil
import codecs
import wx
import wx.lib.scrolledpanel as scrolled
import copy
import glob

#https://github.com/Yukikazari/V-Conv.git


class VprConv():
    def __init__(self, window):
        self.infile = window.infile
        self.outfile = window.outvpr
        self.s5pf = window.s5pf
        self.Conv()

    def Conv(self):
        vprj = {"title": "null", "masterTrack": {"samplingRate": 44100, "tempo": {"global": {"isEnabled": False, "value": 12000}, "events": []}, "timeSig": {"events": []}, "volume": {"events": [{"pos": 0, "value": 0}]}}, "voices": [{"compID": "AKR", "name": "Mishima_Furikake"}], "tracks": []}

        #トラックテンプレート
        t_temp = {"name": "akari", "volume": {"events": [{"pos": 0, "value": 0}]}, "parts": [{"pos": 0, "duration": 0, "styleName": "VOICEROID2 Akari", "voice": {"compID": "10980+Tax", "langID": 0}, "notes": []}]}
        fname = os.path.basename(self.infile)
        name = os.path.splitext(fname)[0]

        vprj["title"] = name #タイトル
        vprj["masterTrack"]["tempo"]["global"]["value"] = self.s5pf["tempo"][0]["value"]
        #最初のとこ

        for i in range(len(self.s5pf["tempo"])):
            vprj["masterTrack"]["tempo"]["events"].append(self.s5pf["tempo"][i])

        for i in range(len(self.s5pf["timeSig"])):
            vprj["masterTrack"]["timeSig"]["events"].append(self.s5pf["timeSig"][i])

        for j in range(len(self.s5pf["tracks"])):
            vprj["tracks"].append(t_temp)
            st = int(self.s5pf["tracks"][j]["notes"][0]["pos"])
            vprj["tracks"][j]["parts"][0]["pos"] = st

            dur = 0
            for i in range(len(self.s5pf["tracks"][j]["notes"])):#歌詞
                tmp = {"lyric": "", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}

                tmp["lyric"] = self.s5pf["tracks"][j]["notes"][i]["lyric"]
                tmp["phoneme"] = self.s5pf["tracks"][j]["notes"][i]["phoneme"]
                tmp["pos"] = self.s5pf["tracks"][j]["notes"][i]["pos"] - st
                tmp["duration"] = self.s5pf["tracks"][j]["notes"][i]["duration"]
                tmp["number"] = self.s5pf["tracks"][j]["notes"][i]["number"]
                tmp["velocity"] = self.s5pf["tracks"][j]["notes"][i]["velocity"]
                dur = int(tmp["pos"] + tmp["duration"])
                vprj["tracks"][j]["parts"][0]["notes"].append(tmp) 

            vprj["tracks"][j]["parts"][0]["duration"] =  dur

        dir_name = './Project'
        os.makedirs("./Project/Project", exist_ok=True)

        with codecs.open('./Project/Project/sequence.json', 'w', 'utf-8') as f:
            json.dump(vprj, f, ensure_ascii=False, indent=4)

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
        infile_name = os.path.basename(infile)
        if os.path.splitext(infile)[1] == '.s5p':
            self.window.infile = infile
            self.window.infile_t.SetLabel(infile)
            if self.window.setting["setting"]["dir"] == True:
                self.window.outvpr = self.window.setting["setting"]["dir_fix"] + "/" + os.path.splitext(infile_name)[0] + '.vpr'           
            else:
                self.window.outvpr = os.path.splitext(infile)[0] + '.vpr'
                             
            self.window.outvpr_t.SetLabel(self.window.outvpr)
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
            infile_name = os.path.basename(infile)
            self.window.infile_t.SetLabel(infile)
            if self.window.setting["setting"]["dir"] == True:
                self.window.outvpr = self.window.setting["setting"]["dir_fix"] + "/" + os.path.splitext(infile_name)[0] + '.vpr'           
            else:
                self.window.outvpr = os.path.splitext(infile)[0] + '.vpr'
                             
            self.window.outvpr_t.SetLabel(self.window.outvpr)
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
        self.select = 0

        #Font
        font_e12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_e10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Segoe UI")
        font_j10 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        font_go = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "メイリオ")
        
        #Frame
        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv", size=(800, 350))
        panel = wx.Panel(self, wx.ID_ANY)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        #メニューバー     
        menu_file = wx.Menu()
        menu_file.Append(1000, '開く')

        menu_file_sub = wx.Menu()
        if len(self.vconvfiles) <= 10:
            backup_count = len(self.vconvfiles)
        else:
            backup_count = 10
        for i in range(backup_count):
            menu_file_sub.Append(i, self.vconvfiles[i])
        menu_file.AppendSubMenu(menu_file_sub, '履歴')

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'ファイル')


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
        grid21.Add(self.infile_t, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        grid21.Add(infile_b, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)
        grid21.AddGrowableCol(0)

        grid22.Add(outvpr_n)
        grid22.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid22.Add(self.outvpr_t, 0, wx.EXPAND)
        grid22.Add(self.outvpr_b, 0, wx.ALIGN_RIGHT)
        grid22.AddGrowableCol(0)

        grid23.Add(outust_n)
        grid23.Add(wx.StaticText(panel2, wx.ID_ANY, ""))
        grid23.Add(self.outust_t, 0, wx.EXPAND)
        grid23.Add(self.outust_b, 0, wx.ALIGN_RIGHT)
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
        self.text32 = wx.Button(panel3, wx.ID_ANY, "ノート編集", size=(120, -1))
        text33 = wx.Button(panel3, wx.ID_ANY, "使い方", size=(100, -1))
        text34 = wx.Button(panel3, wx.ID_ANY, "設定", size=(100, -1))

        try:
            self.com31 = wx.ComboBox(panel3, wx.ID_ANY, "トラック1", choices=self.element, style=wx.CB_READONLY, size=(100, -1))
        except:
            self.element = ["トラック1"]
            self.com31 = wx.ComboBox(panel3, wx.ID_ANY, "トラック1", choices=self.element, style=wx.CB_READONLY, size=(100, -1))

        #Panel_3 setting
        text31.SetFont(font_go)
        self.text32.SetFont(font_j12)
        text33.SetFont(font_j12)
        text33.Disable()
        text34.SetFont(font_j12)

        self.com31.SetFont(font_j10)

        #Panel_3 event
        text31.Bind(wx.EVT_BUTTON, self.OnConversion)
        self.text32.Bind(wx.EVT_BUTTON, self.OnNote)
        #text33.Bind(wx.EVT_BUTTON, self.OnHelp)
        text34.Bind(wx.EVT_BUTTON, self.OnSettings)

        self.com31.Bind(wx.EVT_COMBOBOX, self.OnChangeSelect)

        #Panel_3 layout
        box31.Add(wx.StaticText(panel3, 0, ""))
        box31.Add(text31, flag=wx.CENTER | wx.ALIGN_TOP)
        box31.Add(self.text32, flag=wx.CENTER)

        box31.Add(self.com31, flag=wx.CENTER)

        box32.Add(text33, flag=wx.ALIGN_TOP | wx.CENTER)
        box32.Add(text34, flag=wx.CENTER)
        
        grid3.Add(box31, 1)
        grid3.Add(box32, 0, wx.ALIGN_BOTTOM | wx.CENTER |wx.LEFT | wx.BOTTOM, 10)
        
        panel3.SetSizer(grid3)
        hbox.Add(panel3, 0,wx.RIGHT | wx.LEFT | wx.EXPAND, 10)


        panel.SetSizer(hbox)

        self.SetValues()
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.SelectMenu)
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
            wx.MessageBox("発音辞書がありません")
            self.Destroy()
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

        try:
            with open('./dic/Characterlist.json', encoding='utf-8') as f: #ひらがなカタカナ辞書
                    self.chardic = json.load(f)
        except FileNotFoundError:
            wx.MessageBox("Charsetlistが存在しません")

        self.vconvfiles = []
        for i in sorted(glob.glob('./backup/*'), key=lambda f: os.stat(f).st_mtime, reverse=True):
            tmp = os.path.basename(i)
            tmp = os.path.splitext(tmp)[0]
            self.vconvfiles.append(tmp)

    def SetValues(self):
        #Panel_1
        self.vpr_c.SetValue(self.setting["setting"]["vprconv"])
        self.ust_c.SetValue(self.setting["setting"]["ustconv"])
        self.OnSelectConv('')


        if self.setting["setting"]["note"] == False:
            self.text32.Disable()
            self.com31.Disable()
        else:
            self.text32.Enable()
            self.com31.Enable()

    def ReadS5p(self):
        with open(self.infile, encoding='utf-8') as f:#s5p読み込み
            ins5p = json.load(f)

        self.s5pf = {"tracks": [], "timeSig": [], "tempo": []}
        
        for j in range(len(ins5p["tracks"])):
            self.s5pf["tracks"].append({"notes": [], "count":[], "blank":[]})     
            pos = 0
            for i in range(len(ins5p["tracks"][j]["notes"])):
                #notes
                tmp = {"lyric": "", "lyric_hira":"", "phoneme": "", "pos": 0, "duration": 0, "number": 0, "velocity": 64}
                lyric = ins5p["tracks"][j]["notes"][i]["lyric"]
                try:
                    phone = self.pho["phonetic"][lyric]
                    ly_hira = self.pho["hira"][phone]
                except:
                    ly_hira = "ら"
                tmp["lyric"] = lyric
                tmp["lyric_hira"] = ly_hira
                tmp["pos"] = int(ins5p["tracks"][j]["notes"][i]["onset"] / 1470000)#空白忘れてた
                tmp["duration"] = int(ins5p["tracks"][j]["notes"][i]["duration"] / 1470000)
                tmp["number"] = int(ins5p["tracks"][j]["notes"][i]["pitch"])
                
                if self.setting["setting"]["dev"] == True:
                    if ly_hira in self.chardic["hira"]:
                        t = self.setting["setting"]["dev_hira"]
                    elif ly_hira in self.chardic["kata"]:
                        t = self.setting["setting"]["dev_kata"]
                    else:
                        t = self.setting["setting"]["dev_other"]
                    tmp["phoneme"] = self.pho["dic"][ly_hira][t]
                else:
                    tmp["phoneme"] = self.pho["phonetic"][ly_hira]

                self.s5pf["tracks"][j]["notes"].append(tmp)

                #count,blank         
                tmp = self.s5pf["tracks"][j]["notes"][i]["pos"]
                if tmp - pos >= 200 :
                    self.s5pf["tracks"][j]["count"].append(i)
                    self.s5pf["tracks"][j]["blank"].append(tmp - pos)
                pos = self.s5pf["tracks"][j]["notes"][i]["pos"] + self.s5pf["tracks"][j]["notes"][i]["duration"]
    
            if self.s5pf["tracks"][j]["notes"][0]["pos"] < 200:
                self.s5pf["tracks"][j]["count"].append(0)
                self.s5pf["tracks"][j]["blank"].append(self.s5pf["tracks"][j]["notes"][0]["pos"])

        for i in range(len(ins5p["meter"])):
            tmp = {}
            tmp["bar"] = ins5p["meter"][i]["measure"]
            tmp["numer"] = ins5p["meter"][i]["beatPerMeasure"]
            tmp["denom"] = ins5p["meter"][i]["beatGranularity"]
            self.s5pf["timeSig"].append(tmp)

        for i in range(len(ins5p["tempo"])):
            tmp = {}
            tmp["pos"] = int(ins5p["tempo"][i]["position"] / 1470000)
            tmp["value"] = int(ins5p["tempo"][i]["beatPerMinute"] * 100)
            self.s5pf["tempo"].append(tmp)


        self.element = []
        self.com31.Clear()
        for i in range(len(self.s5pf["tracks"])):
            self.element.append("トラック" + str(i + 1))
            self.com31.Append(self.element[i])
        self.com31.SetValue(self.element[0])

    def OpenVconv(self, file):
        with open(file, encoding='utf-8') as f:
            self.s5pf = json.load(f)

        self.element = []
        self.com31.Clear()
        for i in range(len(self.s5pf["tracks"])):
            self.element.append("トラック" + str(i + 1))
            self.com31.Append(self.element[i])
        self.com31.SetValue(self.element[0])
        self.infile_t.SetLabel(self.s5pf["infile"])
        self.outvpr_t.SetLabel(self.s5pf["outvpr"])



    def SelectMenu(self, event):
        evtid = event.GetId()

        if evtid == 1000:
            first_path = "./backup/"
            filter = "vconv file(*.vconv) | *.vconv"
            dialog = wx.FileDialog(None, '開く', first_path, "", filter, style=wx.FD_FILE_MUST_EXIST)
            dialog.ShowModal()
            if not dialog.GetPath() == '':
                invconv = dialog.GetPath()
                self.OpenVconv(invconv)

        else:
            invconv = './backup/' + self.vconvfiles[evtid] + '.vconv'
            self.OpenVconv(invconv)



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

    def OnChangeSelect(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()

        self.select = self.element.index(val)


    def AppClose(self, event):
        with open('./setting.json', "w") as f:
            json.dump(self.setting, f, indent=4)

        if not self.infile == '':
            backup = self.base + './backup/' + os.path.basename(self.infile) + '.vconv'

            self.s5pf["infile"] = self.infile
            self.s5pf["outvpr"] = self.outvpr

            with open(backup, 'w') as f:
                json.dump(self.s5pf, f)

        
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
        wx.Frame.__init__(self, window, wx.ID_ANY, "設定", size=(400, 400), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL)
        panel = wx.Panel(self, wx.ID_ANY)
        box = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(panel, wx.ID_ANY)

        panel1 = wx.Panel(notebook, wx.ID_ANY)
        panel2 = wx.Panel(notebook, wx.ID_ANY)

        panel_btn = wx.Panel(panel, wx.ID_ANY)

        notebook.InsertPage(0, panel1, '保存設定')
        notebook.InsertPage(1, panel2, 'ノート編集')

        #Panel_1
        box1 = wx.BoxSizer(wx.VERTICAL)
        box11_name = wx.StaticBox(panel1, wx.ID_ANY, '保存先フォルダ設定')
        box11 = wx.StaticBoxSizer(box11_name, wx.VERTICAL)
        grid11 = wx.FlexGridSizer(rows=1, cols=2, gap=(0, 0))
              
        #Panel_1 object
        self.cb111 = wx.CheckBox(panel1, wx.ID_ANY, '保存先フォルダを固定する')

        self.text111 = wx.TextCtrl(panel1, wx.ID_ANY, self.setting["setting"]["dir_fix"])        
        self.btn111 = wx.Button(panel1, wx.ID_ANY, "…", size=(30, -1))



        #Panel_1 setting
        self.cb111.SetFont(font_j10)      

        self.text111.SetFont(font_j10)



        #Panel_1 event
        self.cb111.Bind(wx.EVT_CHECKBOX, self.OnChangecb111)
        self.btn111.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

                     

        #Panel_1 layout
        grid11.Add(self.text111, 1, wx.EXPAND)
        grid11.Add(self.btn111, 0, wx.ALIGN_RIGHT)
        grid11.AddGrowableCol(0)

        box11.Add(self.cb111, 1)
        box11.Add(grid11, 1, wx.EXPAND)

  
       
        box1.Add(box11, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 10)


        panel1.SetSizer(box1)

        #Panel_2

        box2 = wx.BoxSizer(wx.VERTICAL)

        box_note_name = wx.StaticBox(panel2, wx.ID_ANY, '基本設定')
        box_note = wx.StaticBoxSizer(box_note_name, wx.VERTICAL)

        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '無声化設定')
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        box22_name = wx.StaticBox(panel2, wx.ID_ANY, '編集拡張')
        box22 = wx.StaticBoxSizer(box22_name, wx.VERTICAL)

        grid21 = wx.FlexGridSizer(rows=3, cols=2, gap=(0, 0))

        self.element = ('なし', '全体無声化', '1文字目無声化', '長音無声化')
        
        #Panel_2 object
        self.noteedit = wx.CheckBox(panel2, wx.ID_ANY, 'ノート編集を有効にする')

        self.cb21 = wx.CheckBox(panel2, wx.ID_ANY, '文字種による無声化を有効にする')        

        text211 = wx.StaticText(panel2, wx.ID_ANY, '   ひらがな：')
        text212 = wx.StaticText(panel2, wx.ID_ANY, '   カタカナ：')
        text213 = wx.StaticText(panel2, wx.ID_ANY, '   その他　：')

        self.cbox211 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_hira"]], choices=self.element, style=wx.CB_READONLY)
        self.cbox212 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_kata"]], choices=self.element, style=wx.CB_READONLY)
        self.cbox213 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_other"]], choices=self.element, style=wx.CB_READONLY)

        self.cb22 = wx.CheckBox(panel2, wx.ID_ANY, 'ベロシティの変更を有効にする')

        #Panel_2 setting
        self.noteedit.SetFont(font_j10)

        self.cb21.SetFont(font_j10)

        text211.SetFont(font_j10)
        text212.SetFont(font_j10)
        text213.SetFont(font_j10)        

        self.cb22.SetFont(font_j10)

        #Panel_2 event

        self.cb21.Bind(wx.EVT_CHECKBOX, self.OnSelectCb21)

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

        box_note.Add(self.noteedit, 0, wx.EXPAND | wx.BOTTOM, 5)
        box2.Add(box_note, 0, wx.EXPAND | wx.ALL, 10)

        box2.Add(box21, 0, wx.EXPAND | wx.ALL, 10)  
        box2.Add(box22, 0, wx.EXPAND | wx.ALL, 10)

        panel2.SetSizer(box2)

        #ボタン群
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        btny = wx.Button(panel_btn, 1000, "決定", size=(80, -1))
        btnn = wx.Button(panel_btn, wx.ID_ANY, "キャンセル", size=(80, -1))
        btny.SetFont(font_j10)
        btnn.SetFont(font_j10)
        btny.Bind(wx.EVT_BUTTON, self.OnClose)
        btnn.Bind(wx.EVT_BUTTON, self.OnClose)   
        box_btn.Add(btny, 0, wx.ALIGN_RIGHT)
        box_btn.Add(btnn, 0, wx.ALIGN_RIGHT | wx.LEFT, 8)

        panel_btn.SetSizer(box_btn)

        box.Add(notebook, 1, wx.EXPAND)
        box.Add(panel_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        panel.SetSizer(box)

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

        self.noteedit.SetValue(self.setting["setting"]["note"])


    def OnSelectFiles(self, event):
       	text = self.text111.GetValue()
        if os.path.isdir(text) == True:
            path = os.path.dirname(text)
        else:
            path = self.window.base + "/Files"

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
            self.setting["setting"]["note"] = self.noteedit.GetValue()

            self.setting["setting"]["dir"] = self.cb111.GetValue()
            self.setting["setting"]["dev"] = self.cb21.GetValue()
            self.setting["setting"]["dev_hira"] = self.element.index(self.cbox211.GetValue())
            self.setting["setting"]["dev_kata"] = self.element.index(self.cbox212.GetValue())
            self.setting["setting"]["dev_other"] = self.element.index(self.cbox213.GetValue())
            self.setting["setting"]["velocity"] = self.cb22.GetValue()
            self.window.setting = self.setting
            
        self.window.SetValues()
        self.window.setting_now = 0
        self.Destroy()

     
class NoteFrame(wx.Frame):
    def __init__(self, window):
        self.window = window
        self.FirstSettings()

        #self.track = 0
        self.track = self.window.select
        self.count = 0
        self.now = 0


        #Frame 
        wx.Frame.__init__(self, window, wx.ID_ANY, "ノート編集", size=(850, 600) , style= wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.TAB_TRAVERSAL)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.box_root = wx.BoxSizer(wx.HORIZONTAL)

        self.box_left = wx.BoxSizer(wx.VERTICAL)

        select = wx.ComboBox(self.panel, wx.ID_ANY, self.element[self.window.select], choices=self.element, style=wx.CB_READONLY)

        self.box_left.Add(select, 0, wx.ALL, 10)

        #Panel_1
        self.panel1 = scrolled.ScrolledPanel(self.panel, wx.ID_ANY, size=(150, 300))
        self.panel1.SetupScrolling()

        self.CreatePanel1()
        self.box_left.Add(self.panel1, 0, wx.LEFT, 10)
        self.box_root.Add(self.box_left)

        self.panel2 = scrolled.ScrolledPanel(self.panel, wx.ID_ANY)
        self.panel2.SetupScrolling()

        self.CreatePanel2(-1)
        self.box_root.Add(self.panel2, 1, wx.EXPAND | wx.ALL, 10)

        self.panel.SetSizer(self.box_root)


        self.Centre()
        self.panel1.Bind(wx.EVT_RADIOBUTTON, self.OnChangeRadioButton1)
        self.panel2.Bind(wx.EVT_RADIOBUTTON, self.OnChangeRadioButton2)
        self.Bind(wx.EVT_TEXT, self.OnChangeText)

        select.Bind(wx.EVT_COMBOBOX, self.OnChangeSelect)


        self.Panel2SetValue()

        select.Disable()

    def FirstSettings(self):
        self.element = self.window.element
        #for i in range(len(self.window.s5pf["tracks"])):
            #self.element.append("トラック" + str(i + 1))
         
    def CreatePanel1(self):
        try:
            self.box1.Clear(True)
        except:
            pass

        self.box1 = wx.BoxSizer(wx.VERTICAL)
        
        txt = []
        
        for j in range(len(self.window.s5pf["tracks"][self.track]["count"])):
            tmp = ''
            try:
                t = self.window.s5pf["tracks"][self.track]["count"][j + 1]
            except:
                t = len(self.window.s5pf["tracks"][self.track]["notes"])

            for i in range(self.window.s5pf["tracks"][self.track]["count"][j], t):
                tmp = tmp + self.window.s5pf["tracks"][self.track]["notes"][i]["lyric_hira"]
            txt.append(tmp)

        self.text = []
        for i in range(len(txt)):
            self.text.append(i)
            self.text[i] = wx.RadioButton(self.panel1, i, txt[i])
            if i % 2 == 1:
                self.text[i].SetBackgroundColour("#d0d0d0")
        
            self.box1.Add(self.text[i], 0, wx.EXPAND)
        self.text[0].SetValue(True)

        self.panel1.SetSizer(self.box1)
        self.panel1.SetBackgroundColour("#ffffff")




        self.box_left.Layout()


    def CreatePanel2(self, num):
        try:
            self.grid.Clear(False)

            st = self.window.s5pf["tracks"][self.track]["count"][self.now]
            try:
                ed = self.window.s5pf["tracks"][self.track]["count"][self.now + 1]
            except:
                ed = len(self.window.s5pf["tracks"][self.track]["notes"])

            for i in range(st, ed):
                self.note_0[i].Hide()
                self.note_1[i].Hide()
                self.note_2[i].Hide()
                self.note_3[i].Hide()
                self.note_4[i].Hide()
                self.note_5[i].Hide()
                self.note_6[i].Hide()
                self.note_7[i].Hide()
                self.note_8[i].Hide()
                self.note_9[i].Hide()
        except:
            pass

        if num == -1:
            num = 0
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
            self.text0 = wx.StaticText(self.panel2, wx.ID_ANY, '歌詞', style=wx.TE_CENTER, size=(80,25))
            self.text1 = wx.StaticText(self.panel2, wx.ID_ANY, 'よみ', style=wx.TE_CENTER, size=(50,25))
            self.text2 = wx.StaticText(self.panel2, wx.ID_ANY, '発音', style=wx.TE_CENTER, size=(50,25))
            self.text3 = wx.StaticText(self.panel2, wx.ID_ANY, '長さ', style=wx.TE_CENTER, size=(50,25))
            self.text4 = wx.StaticText(self.panel2, wx.ID_ANY, '高さ', style=wx.TE_CENTER, size=(50,25))
            self.text5 = wx.StaticText(self.panel2, wx.ID_ANY, 'ベロシ\nティ', style=wx.TE_CENTER, size=(50,30))
            self.text6 = wx.StaticText(self.panel2, wx.ID_ANY, 'なし', style=wx.TE_CENTER, size=(50,25))
            self.text7 = wx.StaticText(self.panel2, wx.ID_ANY, '全体\n無声化', style=wx.TE_CENTER, size=(50,30))
            self.text8 = wx.StaticText(self.panel2, wx.ID_ANY, '1文字目\n無声化', style=wx.TE_CENTER, size=(50,30))
            self.text9 = wx.StaticText(self.panel2, wx.ID_ANY, '長音\n無声化', style=wx.TE_CENTER, size=(50, 30))

            siz = len(self.window.s5pf["tracks"][self.track]["notes"])
            for i in range(siz):
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

            for i in range(siz):
                self.note_0[i] = wx.TextCtrl(self.panel2, i * 10, self.window.s5pf["tracks"][self.track]["notes"][i]["lyric"], style=wx.TE_CENTER, size=(80,20))
                self.note_1[i] = wx.StaticText(self.panel2, i * 10 + 1, self.window.s5pf["tracks"][self.track]["notes"][i]["lyric_hira"], style=wx.TE_CENTER, size=(50,20))
                self.note_2[i] = wx.StaticText(self.panel2, i * 10 + 2, self.window.s5pf["tracks"][0]["notes"][i]["phoneme"], style=wx.TE_CENTER, size=(50,20))
                self.note_3[i] = wx.StaticText(self.panel2, i * 10 + 3, str(self.window.s5pf["tracks"][self.track]["notes"][i]["duration"]), style=wx.TE_CENTER, size=(50,20))
                self.note_4[i] = wx.StaticText(self.panel2, i * 10 + 4, str(self.window.s5pf["tracks"][self.track]["notes"][i]["number"]), style=wx.TE_CENTER, size=(50,20)) 
                self.note_6[i] = wx.RadioButton(self.panel2, i * 10 + 6, "", style=wx.RB_GROUP)
                self.note_7[i] = wx.RadioButton(self.panel2, i * 10 + 7, "")
                self.note_8[i] = wx.RadioButton(self.panel2, i * 10 + 8, "")
                
                self.note_9[i] = wx.RadioButton(self.panel2, i * 10 + 9, "")
                if self.window.setting["setting"]["velocity"] == True:
                    self.note_5[i] = wx.TextCtrl(self.panel2, i * 10 + 5, str(self.window.s5pf["tracks"][self.track]["notes"][i]["velocity"]), style=wx.TE_CENTER, size=(50, 20))
                else:
                    self.note_5[i] = wx.StaticText(self.panel2, i * 10 + 5, str(self.window.s5pf["tracks"][self.track]["notes"][i]["velocity"]), style=wx.TE_CENTER, size=(50, 20))

                self.note_0[i].Hide()
                self.note_1[i].Hide()
                self.note_2[i].Hide()
                self.note_3[i].Hide()
                self.note_4[i].Hide()
                self.note_5[i].Hide()
                self.note_6[i].Hide()
                self.note_7[i].Hide()
                self.note_8[i].Hide()
                self.note_9[i].Hide()

                if i % 2 == 1:
                    self.note_0[i].SetBackgroundColour("#f6eace")
                    self.note_1[i].SetBackgroundColour("#f6eace")
                    self.note_2[i].SetBackgroundColour("#f6eace")
                    self.note_3[i].SetBackgroundColour("#f6eace")
                    self.note_4[i].SetBackgroundColour("#f6eace")
                    self.note_5[i].SetBackgroundColour("#f6eace")
                    self.note_6[i].SetBackgroundColour("#f6eace")
                    self.note_7[i].SetBackgroundColour("#f6eace")
                    self.note_8[i].SetBackgroundColour("#f6eace")
                    self.note_9[i].SetBackgroundColour("#f6eace")


        st = self.window.s5pf["tracks"][self.track]["count"][num]
        try:
            ed = self.window.s5pf["tracks"][self.track]["count"][num + 1]
        except:
            ed = len(self.window.s5pf["tracks"][self.track]["notes"])

        self.size = ed - st


        self.panel2.SetBackgroundColour("#ffffff")
        self.grid = wx.FlexGridSizer(rows=self.size+1, cols=10, gap=(0, 0))  


        self.grid.Add(self.text0, 0, wx.BOTTOM | wx.TOP | wx.LEFT, 5)
        self.grid.Add(self.text1, 0, wx.BOTTOM | wx.TOP, 5)
        self.grid.Add(self.text2, 0, wx.BOTTOM | wx.TOP, 5)
        self.grid.Add(self.text3, 0, wx.BOTTOM | wx.TOP, 5)
        self.grid.Add(self.text4, 0, wx.BOTTOM | wx.TOP, 5)
        self.grid.Add(self.text5, 0, wx.BOTTOM, 5)
        self.grid.Add(self.text6, 0, wx.BOTTOM | wx.TOP, 5)
        self.grid.Add(self.text7, 0, wx.BOTTOM, 5)
        self.grid.Add(self.text8, 0, wx.BOTTOM, 5)
        self.grid.Add(self.text9, 0, wx.BOTTOM, 5)
        
        for i in range(st, ed):
            self.grid.Add(self.note_0[i], 0, wx.LEFT, 5)
            self.grid.Add(self.note_1[i])
            self.grid.Add(self.note_2[i])
            self.grid.Add(self.note_3[i])
            self.grid.Add(self.note_4[i])
            self.grid.Add(self.note_5[i])
            self.grid.Add(self.note_6[i], 0, wx.EXPAND)
            self.grid.Add(self.note_7[i], 0, wx.EXPAND)
            self.grid.Add(self.note_8[i], 0, wx.EXPAND)
            self.grid.Add(self.note_9[i], 0, wx.EXPAND)

            self.note_0[i].Show()
            self.note_1[i].Show()
            self.note_2[i].Show()
            self.note_3[i].Show()
            self.note_4[i].Show()
            self.note_5[i].Show()
            self.note_6[i].Show()
            self.note_7[i].Show()
            self.note_8[i].Show()
            self.note_9[i].Show()

        self.panel2.SetSizer(self.grid)

        for i in range(st, ed):
            self.ChangeBackColor(i)
        self.box_root.Layout()

        self.panel2.Bind(wx.EVT_PAINT, self.OnPaint)
        self.now = num     

    def Panel2SetValue(self):
        for i in range(len(self.window.s5pf["tracks"][self.track]["notes"])):
            lyric = self.window.s5pf["tracks"][self.track]["notes"][i]["lyric_hira"]
            phoneme = self.window.s5pf["tracks"][self.track]["notes"][i]["phoneme"]
            num = self.window.pho["dic"][lyric].index(phoneme)

            if num == 0:
                pass
            elif num == 1:
                self.note_7[i].SetValue(True)
            elif num == 2:
                self.note_8[i].SetValue(True)
            elif num == 3:
                self.note_9[i].SetValue(True)

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel2)
        dc.SetPen(wx.Pen("black"))
        dc.DrawLine(5, 32, 535, 32)
        siz = 40
        dc.DrawLine(85, 5, 85, siz)
        dc.DrawLine(135, 5, 135, siz)
        dc.DrawLine(185, 5, 185, siz)
        dc.DrawLine(235, 5, 235, siz)
        dc.DrawLine(285, 5, 285, siz)
        dc.DrawLine(335, 5, 335, siz)
        dc.DrawLine(385, 5, 385, siz)
        dc.DrawLine(435, 5, 435, siz)
        dc.DrawLine(485, 5, 485, siz)

    def ChangeBackColor(self, num):
        tcolor = ""
        fcolor = ""
        if num % 2 == 0:
            tcolor = "#ffe0ff"
            fcolor = "#ffffff"
        else:
            tcolor = "#ffcc66"
            fcolor = "#f6eace"

        if self.note_6[num].GetValue() == True:
            self.note_6[num].SetBackgroundColour(tcolor)
        else:
            self.note_6[num].SetBackgroundColour(fcolor)

        if self.note_7[num].GetValue() == True:
            self.note_7[num].SetBackgroundColour(tcolor)
        else:
            self.note_7[num].SetBackgroundColour(fcolor)

        if self.note_8[num].GetValue() == True:
            self.note_8[num].SetBackgroundColour(tcolor)
        else:
            self.note_8[num].SetBackgroundColour(fcolor)

        if self.note_9[num].GetValue() == True:
            self.note_9[num].SetBackgroundColour(tcolor)
        else:
            self.note_9[num].SetBackgroundColour(fcolor)
        
    def OnChangeRadioButton1(self, event):
        evtid = event.GetId()
        self.CreatePanel2(evtid)

    def OnChangeRadioButton2(self, event):
        evtid = event.GetId()
        note = int(evtid / 10)
        num = int(evtid % 10 - 6)

        phoneme = self.window.pho["dic"][self.note_1[note].GetLabel()][num]
        self.window.s5pf["tracks"][self.track]["notes"][note]["phoneme"] =phoneme
        self.ChangeBackColor(note)
        
    def OnChangeSelect(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()

        self.track = self.element.index(val)
        self.CreatePanel1()
        self.CreatePanel2(-1)

    def OnChangeText(self, event):
        evtid = event.GetId()
        obj = event.GetEventObject()
        tmp = obj.GetValue()
        note = int(evtid / 10)
        num = int(evtid % 10)

        if num == 0:
            if tmp in self.window.pho["phonetic"]:
                old = self.window.s5pf["tracks"][self.track]["notes"][note]["lyric"]
                new = tmp
                dlg = wx.MessageDialog(None, old + " → " + new + "\n更新しますか？", "歌詞更新", wx.YES_NO | wx.ICON_INFORMATION)
                res = dlg.ShowModal()
                dlg.Destroy()
                if res == wx.ID_YES:
                    phone = phone = self.window.pho["phonetic"][new]
                    ly_hira = self.window.pho["hira"][phone]
                    self.window.s5pf["tracks"][self.track]["notes"][note]["lyric"] = new
                    self.window.s5pf["tracks"][self.track]["notes"][note]["lyric_hira"] = ly_hira
                    self.window.s5pf["tracks"][self.track]["notes"][note]["phoneme"] = self.window.pho["phonetic"][ly_hira]
                    self.note_1[note].SetLabel(self.window.s5pf["tracks"][self.track]["notes"][note]["lyric_hira"])
                    self.note_2[note].SetLabel(self.window.s5pf["tracks"][self.track]["notes"][note]["phoneme"])
                    self.note_6[note].SetValue(True)

        elif num == 5:
            if tmp.isdigit() == True:
                self.window.s5pf["tracks"][self.track]["notes"][note]["velocity"] = tmp
            else:
                pass

class FinishDialog():
    def __init__(self, file):
        wx.MessageBox( file + "\n変換が完了しました")


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()



