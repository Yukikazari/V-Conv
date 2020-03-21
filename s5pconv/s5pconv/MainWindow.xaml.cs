using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Xml;
using System.Xml.Linq;

namespace V_Conv_dev
{
    /// <summary>
    /// MainWindow.xaml の相互作用ロジック
    /// </summary>
    public partial class MainWindow : Window
    {

        List<List<Note>> NoteList;
        List<TimeSig> TimeSigList;
        List<Tempo> TempoList;
        List<Name> NameList;


        public MainWindow()
        {
            InitializeComponent();


        }

        private void Fbtn_Click(object sender, RoutedEventArgs e)
        {
            var button = (Button)sender;

            if (button.Name == "FbtnS5p")
            {
                var dialog = new OpenFileDialog();
                dialog.Filter = "SynthesizerV(*.s5p)|*.s5p";
                if (dialog.ShowDialog() == true)
                {
                    string filename = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(dialog.FileName), System.IO.Path.GetFileNameWithoutExtension(dialog.FileName));

                    TboxS5p.Text = dialog.FileName;
                    TboxVpr.Text = filename + ".vpr";
                    TboxCcs.Text = filename + ".ccs";

                    ReadS5p(dialog.FileName);

                }
            }
            else
            {
                var dialog = new SaveFileDialog();
                var textbox = (TextBox)TboxS5p;

                if (button.Name == "FbtnVpr")
                {
                    dialog.Filter = "VOCALOID5(*.vpr) | *.vpr";
                    textbox = (TextBox)TboxVpr;
                }
                else if (button.Name == "FbtnCcs")
                {
                    dialog.Filter = "CeVIO(*.ccs)|*.ccs";
                    textbox = (TextBox)TboxCcs;
                }
                /*
                else if (button.Name == "FbtnXml")
                {
                    dialog.Filter = "MusicXML(*.xml)|*.xml";
                    textbox = (TextBox)TboxXml;
                }*/

                try
                {
                    dialog.InitialDirectory = System.IO.Path.GetDirectoryName(textbox.Text) + "\\";
                    dialog.FileName = System.IO.Path.GetFileName(textbox.Text);
                }
                catch
                {
                    dialog.InitialDirectory = Directory.GetCurrentDirectory();
                }

                if (dialog.ShowDialog() == true)
                {
                    textbox.Text = dialog.FileName;
                }
            }
        }

        private void Cb_Checked(object sender, RoutedEventArgs e)
        {
            var cb = (CheckBox)sender;

            try
            {
                if (cb.Name == "CbVpr")
                {
                    TboxVpr.IsEnabled = true;
                    FbtnVpr.IsEnabled = true;
                }
                else if (cb.Name == "CbCcs")
                {
                    TboxCcs.IsEnabled = true;
                    FbtnCcs.IsEnabled = true;
                }
                /*
                else if (cb.Name == "CbXml")
                {
                    TboxXml.IsEnabled = true;
                    FbtnXml.IsEnabled = true;
                }*/
            }
            catch { }
        }

        private void Cb_UnCheked(object sender, RoutedEventArgs e)
        {
            var cb = (CheckBox)sender;

            try
            {
                if (cb.Name == "CbVpr")
                {
                    TboxVpr.IsEnabled = false;
                    FbtnVpr.IsEnabled = false;
                }
                else if (cb.Name == "CbCcs")
                {
                    TboxCcs.IsEnabled = false;
                    FbtnCcs.IsEnabled = false;
                }
                /*
                else if (cb.Name == "CbXml")
                {
                    TboxXml.IsEnabled = false;
                    FbtnXml.IsEnabled = false;
                }*/
            }
            catch { }

        }

        private void BtnConv_Click(object sender, RoutedEventArgs e)
        {
            string result = "";

            var conv = new Conv();

            conv.SetValue(NoteList, TimeSigList, TempoList, NameList);

            if (CbVpr.IsChecked == true)
            {
                conv.VprConv(TboxVpr.Text);

                result += "a";

            }
            if (CbCcs.IsChecked == true)
            {
                conv.CcsConv(TboxCcs.Text);

            }

        }

        private void BtnNote_Click(object sender, RoutedEventArgs e)
        {
            var nw = new NoteWindow();
            nw.Owner = this;
            nw.Show();
        }

        public void ReadS5p(string pass)
        {
            var text = File.ReadAllText(pass);

            var xdoc = JsonConvert.DeserializeXNode(text, "root");

            var phonetic = JsonConvert.DeserializeObject<Dictionary<string, Dictionary<string, string>>>(File.ReadAllText("./dict/Phonetic.json"))["phonetic"];


            NoteList = new List<List<Note>>();

            NameList = new List<Name>();

            IEnumerable<XElement> Xobj1 = from item in xdoc.Elements("root").Elements("tracks") select item;

            foreach (XElement track in Xobj1)
            {
                IEnumerable<XElement> Xobj2 = from item in track.Elements("notes") select item;

                NoteList.Add(new List<Note>());

                Name name = new Name();
                name.name = track.Element("name").Value;

                NameList.Add(name);

                foreach (XElement obj in Xobj2)
                {
                    var n = new Note();

                    n.lyric = obj.Element("lyric").Value;
                    n.lyric_hira = obj.Element("lyric").Value;

                    try
                    {
                        n.phoneme = phonetic[obj.Element("lyric").Value];
                    }
                    catch
                    {
                        var ly = obj.Element("lyric").Value;
                        ly = ly.Replace("　", "").Replace(" ", "");
                        try
                        {
                            n.phoneme = phonetic[ly];
                        }
                        catch
                        {
                            n.phoneme = "4 a";
                        }
                    }


                    long tmp = Convert.ToInt64(obj.Element("onset").Value);
                    tmp = tmp / 1470000;
                    n.pos = (int)tmp;

                    tmp = Convert.ToInt64(obj.Element("duration").Value);
                    tmp = tmp / 1470000;
                    n.duration = (int)tmp;

                    n.number = Convert.ToInt32(obj.Element("pitch").Value);
                    n.velocity = 64;

                    NoteList[NoteList.Count() - 1].Add(n);

                }
            }

            Xobj1 = from item in xdoc.Elements("root").Elements("meter") select item;

            TimeSigList = new List<TimeSig>();

            foreach (XElement obj in Xobj1)
            {
                var n = new TimeSig();

                n.bar = Convert.ToInt32(obj.Element("measure").Value);
                n.numer = Convert.ToInt32(obj.Element("beatPerMeasure").Value);
                n.denom = Convert.ToInt32(obj.Element("beatGranularity").Value);

                TimeSigList.Add(n);
            }

            Xobj1 = from item in xdoc.Elements("root").Elements("tempo") select item;

            TempoList = new List<Tempo>();

            foreach (XElement obj in Xobj1)
            {
                var n = new Tempo();

                long tmp = Convert.ToInt64(obj.Element("position").Value);
                tmp = tmp / 1470000;

                n.pos = (int)tmp;

                tmp = Convert.ToInt32(obj.Element("beatPerMinute").Value);
                tmp = tmp * 100;

                n.value = (int)tmp;

                TempoList.Add(n);
            }
        }

        public void CreateBackup(string fname)
        {

        }

        public void OpenBackup(string pass)
        {
            //TODO バックアップを開く
        }

        private void MenuItem_Newfile_Click(object sender, RoutedEventArgs e)
        {
            //TODO 保存処理追加
            TboxS5p.Text = "";
            TboxCcs.Text = "";
            TboxVpr.Text = "";
        }

        private void MenuItem_BackupOpen_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog();
            dialog.Filter = "backup file(*.vconv)|*.vconv";
            if (dialog.ShowDialog() == true)
            {


                OpenBackup(dialog.FileName);

            }
        }
    }
}
