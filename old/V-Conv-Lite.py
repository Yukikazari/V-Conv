import os
import re
import sys
import json
import shutil
import codecs
import wx
import copy
import glob
import xml.etree.ElementTree as ET
import xml.dom.minidom as md

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
            tt_temp = copy.deepcopy(t_temp)
            vprj["tracks"].append(tt_temp)
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

class CcsConv():
    def __init__(self, window):
        self.infile = window.infile
        self.outfile = window.outccs
        self.s5pf = window.s5pf
        self.Conv()

    def Conv(self):
        Scenario = ET.Element("Scenario")
        Scenario.set('Code', "7251BC4B6168E7B2992FA620BD3E1E77")
        Generation = ET.SubElement(Scenario, 'Generation')
        Author = ET.SubElement(Generation, 'Author', {'Version':'6.1.55.1'})
        TTS = ET.SubElement(Generation, 'TTS', {'Version': '4.0.3'})
        Dictionary = ET.SubElement(TTS, 'Dictionary', {'Version': '2.0.2'})
        SoundSources = ET.SubElement(TTS, 'SoundSources')
        SoundSource = ET.SubElement(SoundSources, 'SoundSource', {'Version': '1.7.3', 'Id': 'A', 'Name': 'さとうささら'})
        SoundSource = ET.SubElement(SoundSources, 'SoundSource', {'Version': '1.5.0', 'Id': 'B', 'Name': 'すずきつづみ'})
        SoundSource = ET.SubElement(SoundSources, 'SoundSource', {'Version': '1.7.0', 'Id': 'C', 'Name': 'タカハシ'})
        SVSS = ET.SubElement(Generation, 'SVSS', {'Version': '4.4.11'})
        Dictionary = ET.SubElement(SVSS, 'Dictionary', {'Version': '1.1.0'})
        SoundSources = ET.SubElement(SVSS, 'SoundSources')
        SoundSource = ET.SubElement(SoundSources, 'SoundSource', {'Version': '1.6.0', 'Id': 'A', 'Name': 'さとうささら'})
        Sequence = ET.SubElement(Scenario, 'Sequence', {'Id':''})
        Scene = ET.SubElement(Sequence, 'Scene', {'Id': ''})
        TimeLine = ET.SubElement(Scene, 'TimeLine', {'Partition': '200,178', 'CurrentPosition':'00:00:00'})
        ViewScale = ET.SubElement(TimeLine, 'ViewScale', {'Horizontal': '1', 'Vertical':'0.64583333333333337'})
        TalkEditor = ET.SubElement(Scene, 'TalkEditor', {'Partition': '542'})
        Extension = ET.SubElement(TalkEditor, 'Extension', {'VerticalRatio': '*,*'})
        SongEditor = ET.SubElement(Scene, 'SongEditor', {'Partition': '64', 'Quantize':'240', 'Mode':'0', 'EditingTool':'1'})
        ViewScale = ET.SubElement(SongEditor, 'ViewScale', {'Horizontal': '16', 'Vertical':'12'})
        ReferenceState = ET.SubElement(SongEditor, 'ReferenceState', {'Current': 'None', 'Previous':'None'})

        Units = ET.SubElement(Scene, 'Units')
        Groups = ET.SubElement(Scene, 'Groups', {'ActiveGroup': '7de5f694-4b60-493d-b6b0-000000000000'})
        SoundSetting = ET.SubElement(Scene, 'SoundSetting', {'Tempo': '120', 'MasterVolume': '0', 'Rhythm':'4/4'})

        tmp = int(1920 * int(self.s5pf["timeSig"][0]["numer"]) / int(self.s5pf["timeSig"][0]["denom"]))
        delay = 0
        for i in range(len(self.s5pf["tracks"])):
            if int(self.s5pf["tracks"][i]["notes"][0]["pos"]) < tmp:
                delay = int(tmp * 2)
                break
            else:
                pass


        for j in range(len(self.s5pf["tracks"])):
            grp = '7de5f694-4b60-493d-b6b0-00000000' + str('%04d' % j)
            Group = ET.SubElement(Groups, 'Group', {'Version':'1.0', 'Id':grp, 'Category':'SingerSong', 'Name':self.s5pf["tracks"][j]["name"], 'Color':'#FFAF1F14', 'Volume':'0', 'Pan':'0', 'IsSolo':'false', 'IsMuted':'false', 'CastId':'A', 'Language':'Japanese'})

            Unit = ET.SubElement(Units, 'Unit', {'Version': '1.0', 'Id': '', 'Category':'SingerSong', 'Group':grp, 'StartTime':'00:00:00', 'Duration':'00:00:00', 'CastId':'A', 'Language':'Japanese'})
            Song = ET.SubElement(Unit, 'Song', {'Version':'1.03'})
            Tempo = ET.SubElement(Song, 'Tempo')

            for i in range(len(self.s5pf["tempo"])):
                Sound = ET.SubElement(Tempo, 'Sound')

                if i == 0:
                    Sound.set('Clock', str(int(self.s5pf["tempo"][i]["pos"] * 2)))
                else:
                    Sound.set('Clock', str(int(self.s5pf["tempo"][i]["pos"] * 2 + delay)))

                Sound.set('Tempo', str(int(self.s5pf["tempo"][i]["value"] / 100)))

            Beat = ET.SubElement(Song, 'Beat')

            tmp = 0
            for i in range(len(self.s5pf["timeSig"])):
                Time = ET.SubElement(Beat, 'Time')

                beats = int(self.s5pf["timeSig"][i]["numer"])
                beattype = int(self.s5pf["timeSig"][i]["denom"])

                clk = 1920 * beats / beattype * (self.s5pf["timeSig"][i]["bar"] - tmp)
                tmp = self.s5pf["timeSig"][i]["bar"]

                if i == 0:
                    Time.set('Clock', str(int(clk * 2)))
                else:
                    Time.set('Clock', str(int(clk * 2 + delay)))

                Time.set('Beats', str(beats))
                Time.set('BeatType', str(beattype))

            Score = ET.SubElement(Song, 'Score')
            Key = ET.SubElement(Score, 'Key', {'Clock': '0', 'Fifths': '0', 'Mode': '0'})
            Dynamics = ET.SubElement(Score, 'Dynamics', {'Clock': '0', 'Value': '5'})

            for i in range(len(self.s5pf["tracks"][j]["notes"])):
                Note = ET.SubElement(Score, 'Note')
                tmp = int(self.s5pf["tracks"][j]["notes"][i]["number"])
                step = int(tmp % 12)
                octabe = int(tmp / 12 - 1)

                Note.set('Clock', str(int(self.s5pf["tracks"][j]["notes"][i]["pos"] * 2 + delay)))
                Note.set('PitchStep', str(step))
                Note.set('PitchOctave', str(octabe))
                Note.set('Duration', str(int(self.s5pf["tracks"][j]["notes"][i]["duration"] * 2)))
                Note.set('Lyric', str(self.s5pf["tracks"][j]["notes"][i]["lyric_hira"]))


        document = md.parseString(ET.tostring(Scenario, 'utf-8'))
        with open(self.outfile, mode='w', encoding='utf-8') as f:
            document.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='  ')



class FileDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.wiondow = window

    def OnDropFiles(self, x, y, files):
        infile = files[len(files) - 1]
        infile_name = os.path.basename(infile)
        if os.path.splitext(infile)[1] == '.s5p':
            self.infile = infile
            if self.wiondow.setting["setting"]["dir"] == True:
                self.wiondow.outvpr = self.wiondow.setting["setting"]["dir_fix"] + "\\" + os.path.splitext(infile_name)[0] + '.vpr'           
                self.window.outccs = self.window.setting["setting"]["dir_fix"] + "\\" + os.path.splitext(infile_name)[0] + '.ccs'
            else:
                self.wiondow.outvpr = os.path.splitext(infile)[0] + '.vpr'
                self.window.outccs = os.path.splitext(infile)[0] + '.ccs'

            self.wiondow.ReadS5p()


class SelectFile():
    def __init__(self, window, num):
        self.wiondow = window

        first_path = os.path.dirname(self.wiondow.infile)
        if num == 0:
            filter = "VOCALOID5 File (*.vpr) | *.vpr"
        if num == 1:
            filter = "CeVIO CS File (*.ccs) | *.ccs"
        else:
            filter = "(*.*) | *.*"
        dialog = wx.FileDialog(None, '開く', first_path, '', filter, style=wx.FD_FILE_MUST_EXIST)  #atode
        dialog.ShowModal()
        if not dialog.GetPath() == '':
            inpath = dialog.GetPath()

            if num == 0:
                self.wiondow.outvpr = inpath
                return 0
            elif num == 1:
                self.window.outccs = inpath
                return 1
            else:
                pass

        return -1

class MainFrame(wx.Frame):
    def __init__(self):
        self.ReadSettings()
        self.infile = ''
        self.outvpr = ''
        self.outccs = ''

        wx.Frame.__init__(self, None, wx.ID_ANY, "V-Conv Lite", size=(300, 300), style= wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        panel = wx.Panel(self, wx.ID_ANY)
        box = wx.BoxSizer(wx.VERTICAL)

        #メニューバー     
        menu_file = wx.Menu()
        menu_file.Append(1000, '開く')

        menu_setting = wx.Menu()
        menu_setting.Append(1001, '設定')

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, 'ファイル')
        menu_bar.Append(menu_setting, '設定')

        text = wx.StaticText(panel, wx.ID_ANY, 'ここにドラッグアンドドロップ')
        box.Add(text, 0, wx.ALIGN_CENTER)

        panel.SetSizer(box)

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

        ver = r'α0.2(\d*)'
        if not re.search(ver, self.setting["version"]):
            wx.MessageBox("setup.exeを実行してください")
            self.Destroy()



    def ReadS5p(self):
        with open(self.infile, encoding='utf-8') as f:#s5p読み込み
            ins5p = json.load(f)

        self.s5pf = {"tracks": [], "timeSig": [], "tempo": []}
        
        for j in range(len(ins5p["tracks"])):
            self.s5pf["tracks"].append({"notes": [], "count": [], "blank": []})
            self.s5pf["tracks"][j]["name"] = ins5p["tracks"][j]["name"]
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


        SelectConv(self)


    def SelectMenu(self, event):
        evtid = event.GetId()

        if evtid == 1000:
            first_path = self.base
            filter = "SynthV file(*.s5p) | *.s5p"
            dialog = wx.FileDialog(None, '開く', first_path, "", filter, style=wx.FD_FILE_MUST_EXIST)
            dialog.ShowModal()
            if not dialog.GetPath() == '':
                infile = dialog.GetPath()
                self.infile = infile
                infile_name = os.path.basename(infile)
                if self.setting["setting"]["dir"] == True:
                    self.outvpr = self.setting["setting"]["dir_fix"] + "\\" + os.path.splitext(infile_name)[0] + '.vpr'           
                    self.outccs = self.setting["setting"]["dir_fix"] + "\\" + os.path.splitext(infile_name)[0] + '.ccs'
                else:
                    self.outvpr = os.path.splitext(infile)[0] + '.vpr'
                    self.outccs = os.path.splitext(infile)[0] + '.ccs'

                self.ReadS5p()

        elif evtid == 1001:
            SetFrame(self).Show()

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

        box21_name = wx.StaticBox(panel2, wx.ID_ANY, '無声化設定')
        box21 = wx.StaticBoxSizer(box21_name, wx.VERTICAL)

        grid21 = wx.FlexGridSizer(rows=3, cols=2, gap=(0, 0))

        self.element = ('なし', '全体無声化', '1文字目無声化', '長音無声化')
        
        #Panel_2 object
        self.cb21 = wx.CheckBox(panel2, wx.ID_ANY, '文字種による無声化を有効にする')        

        text211 = wx.StaticText(panel2, wx.ID_ANY, '   ひらがな：')
        text212 = wx.StaticText(panel2, wx.ID_ANY, '   カタカナ：')
        text213 = wx.StaticText(panel2, wx.ID_ANY, '   その他　：')

        self.cbox211 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_hira"]], choices=self.element, style=wx.CB_READONLY)
        self.cbox212 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_kata"]], choices=self.element, style=wx.CB_READONLY)
        self.cbox213 = wx.ComboBox(panel2, wx.ID_ANY, self.element[self.setting["setting"]["dev_other"]], choices=self.element, style=wx.CB_READONLY)

        #Panel_2 setting
        self.cb21.SetFont(font_j10)

        text211.SetFont(font_j10)
        text212.SetFont(font_j10)
        text213.SetFont(font_j10)        

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

        box2.Add(box21, 0, wx.EXPAND | wx.ALL, 10)  

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
            self.setting["setting"]["dir"] = self.cb111.GetValue()
            self.setting["setting"]["dev"] = self.cb21.GetValue()
            self.setting["setting"]["dev_hira"] = self.element.index(self.cbox211.GetValue())
            self.setting["setting"]["dev_kata"] = self.element.index(self.cbox212.GetValue())
            self.setting["setting"]["dev_other"] = self.element.index(self.cbox213.GetValue())
            self.window.setting = self.setting
            
        self.Destroy()


class SelectConv():
    def __init__(self, window):
        self.window = window

        dlg = CreateDialog(self.window)
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            outfiles = ''
            if dlg.cb1.Value == True:
                out = self.window.outvpr

                if os.path.isfile(out) == True:
                    dlgvpr = wx.MessageDialog(None, out + "は既に存在します。上書きしますか？", "上書き確認", wx.YES_NO |wx.ICON_INFORMATION)
                    res = dlgvpr.ShowModal()
                    dlgvpr.Destroy()
                    if res == wx.ID_YES:
                        VprConv(self.window)
                        outfiles += os.path.basename(self.window.outvpr) + '\n'
                    else:
                        if SelectFile(self.window, 0) == 0:

                            VprConv(self.window)
                            outfiles += os.path.basename(self.window.outvpr) + '\n'

                else:
                    VprConv(self.window)
                    outfiles += os.path.basename(self.window.outvpr) + '\n'

            if dlg.cb2.Value == True:
                out = self.window.outccs

                if os.path.isfile(out) == True:
                    dlgccs = wx.MessageDialog(None, out + "は既に存在します。上書きしますか？", "上書き確認", wx.YES_NO |wx.ICON_INFORMATION)
                    res = dlgccs.ShowModal()
                    dlgccs.Destroy()
                    if res == wx.ID_YES:
                        CcsConv(self.window)
                        outfiles += os.path.basename(self.window.outccs) + '\n'
                    else:
                        if SelectFile(self.window, 1) == 1:

                            CcsConv(self.window)
                            outfiles += os.path.basename(self.window.outccs) + '\n'

                else:
                    CcsConv(self.window)
                    outfiles += os.path.basename(self.window.outccs) + '\n'

            if not outfiles == '':
                FinishDialog(outfiles)

class CreateDialog(wx.Dialog):
    def __init__(self, window):
        self.window = window

        wx.Dialog.__init__(self, window, wx.ID_ANY, '変換先ファイル', size=(200, 150))
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.cb1 = wx.CheckBox(self, wx.ID_ANY, 'vpr (KotonoSync用)')
        self.cb1.SetValue(True)

        self.cb2 = wx.CheckBox(self, wx.ID_ANY, 'ccs (CeVIO)')
        self.cb2.SetValue(True)

        btnOk = wx.Button(self, wx.ID_OK)
        btnOk.SetDefault()
        btnCancel = wx.Button(self, wx.ID_CANCEL)

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(btnOk)
        btns.AddButton(btnCancel)
        btns.Realize()

        sizer.Add(self.cb1, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        sizer.Add(self.cb2, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)


class FinishDialog():
    def __init__(self, file):
        wx.MessageBox( file + "\n変換が完了しました")


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()



