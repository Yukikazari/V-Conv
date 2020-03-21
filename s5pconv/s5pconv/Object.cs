using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace V_Conv_dev
{


    public class Note
    {
        public string lyric;
        public string lyric_hira;
        public string phoneme;
        public int pos;
        public int duration;
        public int number;
        public int velocity;
    }

    class TimeSig
    {
        public int bar;
        public int numer;
        public int denom;
    }

    class Tempo
    {
        public int pos;
        public int value;
    }

    class Name
    {
        public string name;
    }

    public class VprRoot
    {
        public string title;
        public VprMasterTrack masterTrack = new VprMasterTrack();
        public List<VprVoices> voices = new List<VprVoices>();
        public List<VprTracks> tracks = new List<VprTracks>();

    }

    public class VprMasterTrack
    {
        public int samplingRate = 44100;
        public VprTempo tempo = new VprTempo();
        public VprTimeSig timeSig = new VprTimeSig();
        public VprVolume volume = new VprVolume();
    }

    public class VprTempo
    {
        public VprGrobal grobal = new VprGrobal();
        public List<VprTempoEvents> events = new List<VprTempoEvents>();
    }

    public class VprGrobal
    {
        public bool inEnabled = false;
        public int value;
    }

    public class VprTempoEvents
    {
        public int pos;
        public int value;
    }

    public class VprTimeSig
    {
        public List<VprTimeSigEvents> events = new List<VprTimeSigEvents>();
    }

    public class VprTimeSigEvents
    {
        public int bar;
        public int numer;
        public int denom;
    }

    public class VprVolume
    {
        public List<VprVolumeEvents> events = new List<VprVolumeEvents>();
    }

    public class VprVolumeEvents
    {
        public int pos = 0;
        public int value = 0;
    }

    public class VprVoices
    {
        public string compID = "AKR";
        public string name = "Mishima_Furikake";
    }

    public class VprTracks
    {
        public string name = "akari";
        public VprTracksVolume volume = new VprTracksVolume();
        public List<VprParts> parts = new List<VprParts>();
    }

    public class VprTracksVolume
    {
        public List<VprTracksEvents> events = new List<VprTracksEvents>();
    }

    public class VprTracksEvents
    {
        public int pos = 0;
        public int value = 0;
    }

    public class VprParts
    {
        public int pos;
        public int duration;
        public string styleName = "VOICEROID2 Akari";
        public VprPartsVoice voice = new VprPartsVoice();
        public List<VprNotes> notes = new List<VprNotes>();

    }
    public class VprPartsVoice
    {
        public string conpID = "10980+Tax";
        public int langID = 0;
    }

    public class VprNotes
    {
        public string lyric;
        public string phoneme;
        public int pos;
        public int duration;
        public int number;
        public int velocity;
    }

}
