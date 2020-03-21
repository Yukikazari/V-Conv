using System;
using System.Runtime.Serialization.Json;
using System.IO;
using System.IO.Compression;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using System.Xml.Linq;
using System.Text;
using System.Threading.Tasks;

namespace V_Conv_dev
{
    class Conv
    {
        List<List<Note>> NoteList = new List<List<Note>>();
        List<TimeSig> TimeSigList = new List<TimeSig>();
        List<Tempo> TempoList = new List<Tempo>();
        List<Name> NameList = new List<Name>();

        public void SetValue(List<List<Note>> n, List<TimeSig> ts, List<Tempo> tm, List<Name> nm)
        {
            NoteList = n;
            TimeSigList = ts;
            TempoList = tm;
            NameList = nm;
        }

        public void VprConv(string fname)
        {
            var root = new VprRoot();

            root.title = System.IO.Path.GetFileNameWithoutExtension(fname);
            root.masterTrack.tempo.grobal.value = TempoList[0].value;

            foreach (var tempo in TempoList)
            {
                var tmpa = new VprTempoEvents();
                tmpa.pos = tempo.pos;
                tmpa.value = tempo.value;

                root.masterTrack.tempo.events.Add(tmpa);
            }

            foreach (var evt in TimeSigList)
            {
                var tmpb = new VprTimeSigEvents();
                tmpb.bar = evt.bar;
                tmpb.numer = evt.numer;
                tmpb.denom = evt.denom;

                root.masterTrack.timeSig.events.Add(tmpb);
            }

            var vo = new VprVolumeEvents();
            root.masterTrack.volume.events.Add(vo);

            var tmpc = new VprVoices();
            root.voices.Add(tmpc);

            for (int i = 0; i < NoteList.Count(); i++)
            {
                var track = new VprTracks();

                var vev = new VprTracksEvents();
                track.volume.events.Add(vev);

                var parts = new VprParts(); //修正

                int st = NoteList[i][0].pos;


                parts.pos = st;

                for (int j = 0; j < NoteList[i].Count(); j++)
                {
                    var note = new VprNotes();

                    note.lyric = NoteList[i][j].lyric;
                    note.phoneme = NoteList[i][j].phoneme;
                    note.pos = NoteList[i][j].pos - st;
                    note.duration = NoteList[i][j].duration;
                    note.number = NoteList[i][j].number;
                    note.velocity = NoteList[i][j].velocity;

                    parts.notes.Add(note);
                }
                int en = parts.notes[parts.notes.Count() - 1].pos + parts.notes[parts.notes.Count() - 1].duration;

                parts.duration = en;

                track.parts.Add(parts);
                root.tracks.Add(track);
            }


            using (Stream st = new FileStream(@".\Project\Project\sequence.json", FileMode.Create))
            {
                var serializer = new DataContractJsonSerializer(typeof(VprRoot));
                serializer.WriteObject(st, root);
            }

            string zipName = @"temp.zip";
            string folderName = @".\Project";

            try
            {
                ZipFile.CreateFromDirectory(folderName, zipName);
            }
            catch
            {
                File.Delete(zipName);
                ZipFile.CreateFromDirectory(folderName, zipName);
            }

            File.Copy(zipName, fname, true);
            File.Delete(zipName);

        }

        public void CcsConv(string fname)
        {
            XmlWriterSettings set = new XmlWriterSettings();
            set.Indent = true;

            int t = 1920 * (TimeSigList[0].numer / TimeSigList[0].denom);

            int delay = 0;
            for (int i = 0; i < NoteList.Count(); i++)
            {
                if (NoteList[i][0].pos < t)
                {
                    delay = t * 2;
                    break;
                }
            }

            int tmp;

            using (Stream st = new FileStream(fname, FileMode.Create))
            {
                using (XmlWriter xw = XmlWriter.Create(st, set))
                {
                    xw.WriteStartElement("Scenario");
                    xw.WriteAttributeString("Code", "7251BC4B6168E7B2992FA620BD3E1E77");

                    xw.WriteStartElement("Generation");

                    xw.WriteStartElement("Author");
                    xw.WriteAttributeString("Version", "7.0.17.0");
                    xw.WriteEndElement(); //Author

                    xw.WriteStartElement("TTS");
                    xw.WriteAttributeString("Version", "5.1.4");

                    xw.WriteStartElement("Dictionary");
                    xw.WriteAttributeString("Version", "3.0.2");
                    xw.WriteEndElement(); //Dictionary

                    xw.WriteStartElement("SoundSources");

                    xw.WriteStartElement("SoundSource");
                    xw.WriteAttributeString("Version", "1.7.3");
                    xw.WriteAttributeString("Id", "A");
                    xw.WriteAttributeString("Name", "さとうささら");
                    xw.WriteEndElement(); //SoundSource

                    xw.WriteStartElement("SoundSource");
                    xw.WriteAttributeString("Version", "1.5.0");
                    xw.WriteAttributeString("Id", "B");
                    xw.WriteAttributeString("Name", "すずきつづみ");
                    xw.WriteEndElement(); //SoundSource

                    xw.WriteStartElement("SoundSource");
                    xw.WriteAttributeString("Version", "1.7.0");
                    xw.WriteAttributeString("Id", "C");
                    xw.WriteAttributeString("Name", "タカハシ");
                    xw.WriteEndElement(); //SoundSource

                    xw.WriteEndElement(); //SoundSources
                    xw.WriteEndElement(); //TTS

                    xw.WriteStartElement("SVSS");
                    xw.WriteAttributeString("Version", "5.1.1");

                    xw.WriteStartElement("Dictionary");
                    xw.WriteAttributeString("Version", "3.0.0");
                    xw.WriteEndElement(); //Dictionary

                    xw.WriteStartElement("SoundSources");

                    xw.WriteStartElement("SoundSource");
                    xw.WriteAttributeString("Version", "1.7.0");
                    xw.WriteAttributeString("Id", "A");
                    xw.WriteAttributeString("Name", "さとうささら");
                    xw.WriteEndElement(); //SoundSource

                    xw.WriteEndElement(); //SoundSources
                    xw.WriteEndElement(); //SVSS
                    xw.WriteEndElement(); //Generation

                    xw.WriteStartElement("Sequence");
                    xw.WriteAttributeString("Id", "");

                    xw.WriteStartElement("Scene");
                    xw.WriteAttributeString("Id", "");

                    xw.WriteStartElement("Timeline");
                    xw.WriteAttributeString("Partition", "200,178");
                    xw.WriteAttributeString("CurrentPosition", "00:00:00");

                    xw.WriteStartElement("ViewScale");
                    xw.WriteAttributeString("Horizontal", "0.73");
                    xw.WriteAttributeString("Vertical", "0.64583333333333337");
                    xw.WriteEndElement(); //ViewScale
                    xw.WriteEndElement(); //Timeline

                    xw.WriteStartElement("TalkEditor");
                    xw.WriteAttributeString("Partition", "542");

                    xw.WriteStartElement("Extension");
                    xw.WriteAttributeString("VerticalRatio", "*,*");
                    xw.WriteEndElement(); //Extension
                    xw.WriteEndElement(); //TalkEditor

                    xw.WriteStartElement("SongEditor");
                    xw.WriteAttributeString("Partition", "64");
                    xw.WriteAttributeString("Quantize", "240");
                    xw.WriteAttributeString("Mode", "0");
                    xw.WriteAttributeString("EditingTool", "1");

                    xw.WriteStartElement("ViewScale");
                    xw.WriteAttributeString("Horizontal", "48");
                    xw.WriteAttributeString("Vertical", "14");
                    xw.WriteEndElement(); //ViewScale

                    xw.WriteStartElement("ReferenceState");
                    xw.WriteAttributeString("Current", "None");
                    xw.WriteAttributeString("Previous", "None");
                    xw.WriteEndElement(); //ReferenceState
                    xw.WriteEndElement(); //SongEditor

                    xw.WriteStartElement("Units");               //あとで

                    for (int i = 0; i < NoteList.Count(); i++)
                    {

                        xw.WriteStartElement("Unit");
                        xw.WriteAttributeString("Version", "1.0");
                        xw.WriteAttributeString("Id", "");
                        xw.WriteAttributeString("Category", "SingerSong");
                        xw.WriteAttributeString("Group", "7de5f694-4b60-493d-b6b0-00000000000" + i.ToString());
                        xw.WriteAttributeString("StartTime", "00:00:00");
                        xw.WriteAttributeString("Duration", "00:00:00");
                        xw.WriteAttributeString("CastId", "A");
                        xw.WriteAttributeString("Language", "Japanese");

                        xw.WriteStartElement("Song");
                        xw.WriteAttributeString("Version", "1.07");

                        xw.WriteStartElement("Tempo");

                        for (int j = 0; j < TempoList.Count(); j++)
                        {
                            xw.WriteStartElement("Sound");

                            if (j == 0)
                            {
                                tmp = TempoList[j].pos * 2;
                            }
                            else
                            {
                                tmp = TempoList[j].pos * 2 + delay;
                            }

                            xw.WriteAttributeString("Clock", tmp.ToString());

                            tmp = TempoList[j].value / 100;
                            xw.WriteAttributeString("Tempo", tmp.ToString());

                            xw.WriteEndElement(); //Sound
                        }
                        xw.WriteEndElement(); //Tempo

                        xw.WriteStartElement("Beat");

                        tmp = 0;

                        for (int j = 0; j < TimeSigList.Count(); j++)
                        {
                            xw.WriteStartElement("Time");

                            int clk = 1920 * TimeSigList[j].numer / TimeSigList[j].denom * (TimeSigList[j].bar - tmp);
                            tmp = TimeSigList[j].bar;

                            clk *= 2;

                            if (j != 0)
                            {
                                clk = clk + delay;
                            }
                            xw.WriteAttributeString("Clock", clk.ToString());

                            xw.WriteAttributeString("Beats", TimeSigList[j].numer.ToString());
                            xw.WriteAttributeString("BeatType", TimeSigList[j].denom.ToString());

                            xw.WriteEndElement(); //Time
                        }
                        xw.WriteEndElement(); //Beat

                        xw.WriteStartElement("Score");

                        xw.WriteStartElement("Key");
                        xw.WriteAttributeString("Clock", "0");
                        xw.WriteAttributeString("Fifths", "0");
                        xw.WriteAttributeString("Mode", "0");
                        xw.WriteEndElement(); //Key

                        xw.WriteStartElement("Dynamics");
                        xw.WriteAttributeString("Clock", "0");
                        xw.WriteAttributeString("Value", "5");
                        xw.WriteEndElement(); //Dynamics

                        foreach (var note in NoteList[i])
                        {
                            xw.WriteStartElement("Note");

                            tmp = note.number;
                            int step = tmp % 12;
                            int octabe = tmp / 12 - 1;

                            xw.WriteAttributeString("Clock", (note.pos * 2 + delay).ToString());
                            xw.WriteAttributeString("PitchStep", step.ToString());
                            xw.WriteAttributeString("PitchOctave", octabe.ToString());
                            xw.WriteAttributeString("Duration", (note.duration * 2).ToString());
                            xw.WriteAttributeString("Lyric", note.lyric_hira);
                            xw.WriteAttributeString("DoReMi", "false");

                            xw.WriteEndElement(); //Note
                        }
                        xw.WriteEndElement(); //Score
                        xw.WriteEndElement(); //Song
                        xw.WriteEndElement(); //Unit
                    }
                    xw.WriteEndElement(); //Units

                    xw.WriteStartElement("Groups");
                    xw.WriteAttributeString("ActiveGroup", "7de5f694-4b60-493d-b6b0-000000000000");    //中身は向こうで

                    for (int i = 0; i < NoteList.Count(); i++)
                    {
                        xw.WriteStartElement("Group");
                        xw.WriteAttributeString("Version", "1.0");
                        xw.WriteAttributeString("Id", "7de5f694-4b60-493d-b6b0-00000000000" + i.ToString());
                        xw.WriteAttributeString("Category", "SingerSong");
                        xw.WriteAttributeString("Name", NameList[i].name);
                        xw.WriteAttributeString("Color", "#FFAF1F14");
                        xw.WriteAttributeString("Volume", "0");
                        xw.WriteAttributeString("Pan", "0");
                        xw.WriteAttributeString("IsSolo", "false");
                        xw.WriteAttributeString("IsMuted", "false");
                        xw.WriteAttributeString("CastId", "A");
                        xw.WriteAttributeString("Language", "Japanese");

                        xw.WriteEndElement(); //Group
                    }

                    xw.WriteEndElement(); //Groups

                    xw.WriteStartElement("SoundSetting");
                    xw.WriteAttributeString("Rhythm", "4/4");
                    xw.WriteAttributeString("Tempo", "120");
                    xw.WriteAttributeString("MasterVolume", "0");
                    xw.WriteEndElement(); //SoundSetting
                    xw.WriteEndElement(); //Scene
                    xw.WriteEndElement(); //Sequence
                    xw.WriteEndElement(); //Scenario
                    xw.Flush();
                }
            }
        }

        public void XmlConv(string fname)
        {
            fname = fname.Replace(".xml", "");

            XmlWriterSettings set = new XmlWriterSettings();
            set.Indent = true;

            for (int i = 0; i < NoteList.Count(); i++)
            {
                string outfile = fname + "_" + NameList[i].name + ".xml";

                using (Stream st = new FileStream(outfile, FileMode.Create))
                {
                    using (XmlWriter xw = XmlWriter.Create(st, set))
                    {
                        xw.WriteStartElement("score-partwise");
                        xw.WriteAttributeString("version", "2.0");

                        xw.WriteStartElement("identification");
                        xw.WriteStartElement("encoding");
                        xw.WriteElementString("software", "Sinsy");

                        xw.WriteEndElement();//encoding
                        xw.WriteEndElement();//identification

                        xw.WriteStartElement("part-list");

                        xw.WriteStartElement("score-part");
                        xw.WriteAttributeString("id", "P1");
                        xw.WriteElementString("part-name", "MusicXML Part");

                        xw.WriteEndElement();//score-part
                        xw.WriteEndElement();//part-list

                        xw.WriteStartElement("part");
                        xw.WriteAttributeString("id", "P1");

                        xw.WriteStartElement("measure");
                        xw.WriteAttributeString("number", "1");

                        xw.WriteStartElement("attributes");


                        xw.WriteEndElement();//attributes

                        xw.WriteEndElement();//measure

                        xw.WriteEndElement();//part

                        xw.WriteEndElement();//score-partwise

                        /*
                        xw.WriteStartElement("");
                        xw.WriteEndElement();//

                        xw.WriteAttributeString("", "");*/



                    }
                }


            }
        }

        //Xml一旦凍結。ヤバイわよ！


    }
}
