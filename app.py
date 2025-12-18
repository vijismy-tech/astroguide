
import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, MapPin, Loader2, Sparkles, Sun, Moon, Info, ArrowRightCircle } from 'lucide-react';
import { GoogleGenAI, Type } from '@google/genai';
import { DISTRICTS } from './constants';
import { District, PanchangamData } from './types';

const App: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<District>(DISTRICTS[2]); // Default Chennai
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<PanchangamData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchPanchangam = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const prompt = `Generate a detailed Tamil Thirukanitha Panchangam for the location ${selectedDistrict.name} (Latitude: ${selectedDistrict.lat}, Longitude: ${selectedDistrict.lng}) on the date ${selectedDate}. 
      All text fields must be in Tamil language.
      Provide detailed astrological calculations for Tithi, Nakshatram, Yogam, Karanam, Rahukalam, Yamagandam, and planetary positions.
      Also include a brief summary of the day's astrological significance in Tamil.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: prompt,
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              panchangam: {
                type: Type.OBJECT,
                properties: {
                  tamilYear: { type: Type.STRING },
                  tamilMonth: { type: Type.STRING },
                  tamilDay: { type: Type.STRING },
                  ayanam: { type: Type.STRING },
                  ruthu: { type: Type.STRING },
                  tithi: { type: Type.STRING },
                  nakshatram: { type: Type.STRING },
                  yogam: { type: Type.STRING },
                  karanam: { type: Type.STRING },
                  rasi: { type: Type.STRING },
                  rahukalam: { type: Type.STRING },
                  yamagandam: { type: Type.STRING },
                  kuligai: { type: Type.STRING },
                  nallaNeram: { type: Type.STRING },
                  gowriNallaNeram: { type: Type.STRING },
                  chandrashtamam: { type: Type.STRING },
                  summary: { type: Type.STRING },
                  planetaryPositions: {
                    type: Type.ARRAY,
                    items: {
                      type: Type.OBJECT,
                      properties: {
                        planet: { type: Type.STRING },
                        rasi: { type: Type.STRING },
                        degrees: { type: Type.STRING }
                      },
                      required: ['planet', 'rasi', 'degrees']
                    }
                  }
                },
                required: [
                  'tamilYear', 'tamilMonth', 'tamilDay', 'ayanam', 'ruthu', 'tithi', 
                  'nakshatram', 'yogam', 'karanam', 'rasi', 'rahukalam', 'yamagandam', 
                  'kuligai', 'nallaNeram', 'gowriNallaNeram', 'chandrashtamam', 'summary', 'planetaryPositions'
                ]
              }
            },
            required: ['panchangam']
          }
        }
      });

      const result = JSON.parse(response.text);
      setData(result.panchangam);
    } catch (err) {
      console.error(err);
      setError('பஞ்சாங்கம் விவரங்களைப் பெறுவதில் பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.');
    } finally {
      setLoading(false);
    }
  }, [selectedDistrict, selectedDate]);

  useEffect(() => {
    fetchPanchangam();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <header className="bg-tamil-gold text-white py-8 px-4 shadow-lg mb-8">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-3 rounded-full">
              <Sun className="w-8 h-8 text-yellow-200" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">தமிழ் திருக்கணித பஞ்சாங்கம்</h1>
              <p className="text-yellow-100 mt-1 opacity-90">38 மாவட்டங்கள் மற்றும் புதுச்சேரிக்கான துல்லியமான கணிப்பு</p>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-4 items-center bg-white/10 p-4 rounded-xl backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-yellow-200" />
              <select 
                value={selectedDistrict.name}
                onChange={(e) => setSelectedDistrict(DISTRICTS.find(d => d.name === e.target.value) || DISTRICTS[0])}
                className="bg-transparent border-b border-white/30 text-white focus:outline-none cursor-pointer p-1"
              >
                {DISTRICTS.map(d => (
                  <option key={d.name} value={d.name} className="text-black">{d.tamilName}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-yellow-200" />
              <input 
                type="date" 
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="bg-transparent border-b border-white/30 text-white focus:outline-none cursor-pointer p-1"
              />
            </div>
            <button 
              onClick={fetchPanchangam}
              disabled={loading}
              className="bg-white text-tamil-gold px-6 py-2 rounded-lg font-bold hover:bg-yellow-50 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRightCircle className="w-4 h-4" />}
              கணித்திடு
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 flex items-center gap-3">
            <Info className="w-5 h-5" />
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-tamil-gold">
            <Loader2 className="w-16 h-16 animate-spin mb-4" />
            <p className="text-xl font-medium">பஞ்சாங்கம் கணிக்கப்படுகிறது...</p>
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Main Daily Card */}
            <div className="lg:col-span-2 space-y-6">
              <section className="panchangam-card p-6 rounded-2xl shadow-sm">
                <div className="flex justify-between items-start mb-6 border-b border-orange-100 pb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-orange-800">{data.tamilMonth} {data.tamilDay}</h2>
                    <p className="text-orange-600 font-medium">{data.tamilYear} ஆண்டு | {data.ayanam} | {data.ruthu}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-gray-500 text-sm">தேதி: {selectedDate}</p>
                    <p className="text-gray-500 text-sm">இடம்: {selectedDistrict.tamilName}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <PanchangamItem icon={<Sun className="w-5 h-5 text-orange-500" />} label="திதி" value={data.tithi} />
                    <PanchangamItem icon={<Moon className="w-5 h-5 text-indigo-500" />} label="நட்சத்திரம்" value={data.nakshatram} />
                    <PanchangamItem icon={<Sparkles className="w-5 h-5 text-purple-500" />} label="யோகம்" value={data.yogam} />
                    <PanchangamItem icon={<Info className="w-5 h-5 text-blue-500" />} label="கரணம்" value={data.karanam} />
                  </div>
                  <div className="space-y-4">
                    <PanchangamItem icon={<MapPin className="w-5 h-5 text-red-500" />} label="ராசி" value={data.rasi} />
                    <PanchangamItem icon={<Info className="w-5 h-5 text-amber-500" />} label="சந்திராஷ்டமம்" value={data.chandrashtamam} />
                    <PanchangamItem icon={<Sun className="w-5 h-5 text-yellow-600" />} label="நல்ல நேரம்" value={data.nallaNeram} />
                    <PanchangamItem icon={<Sun className="w-5 h-5 text-yellow-500" />} label="கௌரி நல்ல நேரம்" value={data.gowriNallaNeram} />
                  </div>
                </div>
              </section>

              {/* Summary Card */}
              <section className="bg-orange-50 p-6 rounded-2xl border border-orange-100">
                <h3 className="text-lg font-bold text-orange-900 mb-3 flex items-center gap-2">
                  <Sparkles className="w-5 h-5" /> இன்றைய பலன்கள்
                </h3>
                <p className="text-orange-800 leading-relaxed">{data.summary}</p>
              </section>

              {/* Planetary Positions */}
              <section className="panchangam-card p-6 rounded-2xl shadow-sm">
                <h3 className="text-lg font-bold text-gray-800 mb-4">கிரக நிலைகள் (திருக்கணிதம்)</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {data.planetaryPositions.map((p, idx) => (
                    <div key={idx} className="bg-white p-3 rounded-xl border border-gray-100 flex flex-col items-center justify-center text-center">
                      <span className="text-gray-500 text-xs font-bold uppercase tracking-wider">{p.planet}</span>
                      <span className="text-tamil-gold font-bold">{p.rasi}</span>
                      <span className="text-gray-400 text-[10px]">{p.degrees}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* Sidebar Cards */}
            <div className="space-y-6">
              <section className="bg-red-50 p-6 rounded-2xl border border-red-100">
                <h3 className="text-lg font-bold text-red-900 mb-4 flex items-center gap-2">
                   அசுப நேரங்கள்
                </h3>
                <div className="space-y-4">
                  <TimingItem label="ராகு காலம்" value={data.rahukalam} color="text-red-700" />
                  <TimingItem label="எமகண்டம்" value={data.yamagandam} color="text-red-700" />
                  <TimingItem label="குளிகை" value={data.kuligai} color="text-blue-700" />
                </div>
              </section>

              <div className="panchangam-card p-6 rounded-2xl border border-orange-100">
                <h3 className="text-lg font-bold text-orange-900 mb-4">அடிக்கடி கேட்கப்படுபவை</h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• <strong>திருக்கணிதம்</strong> என்பது துல்லியமான கிரக நிலைகளை அடிப்படையாகக் கொண்ட முறை.</p>
                  <p>• இந்த பஞ்சாங்கம் 38 மாவட்டங்களுக்கும் இடத்திறகு ஏற்ப கணிக்கப்பட்டுள்ளது.</p>
                  <p>• விசேஷ நாட்களில் விரதம் மற்றும் வழிபாட்டு முறைகள் மாறுபடலாம்.</p>
                </div>
              </div>

              <div className="bg-indigo-900 text-white p-6 rounded-2xl shadow-xl overflow-hidden relative">
                <div className="absolute top-0 right-0 opacity-10">
                   <Moon className="w-24 h-24" />
                </div>
                <h3 className="text-xl font-bold mb-2">ஆன்மீகத் தகவல்</h3>
                <p className="text-indigo-200 text-sm leading-relaxed italic">
                  "நல்ல நேரத்தில் தொடங்கும் செயல் என்றும் வெற்றியைத் தரும்." 
                </p>
              </div>
            </div>

          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-500">விவரங்கள் எதுவும் கிடைக்கவில்லை. தேதியைத் தேர்ந்தெடுத்து 'கணித்திடு' பொத்தானை அழுத்தவும்.</p>
          </div>
        )}
      </main>

      <footer className="max-w-5xl mx-auto px-4 mt-12 text-center text-gray-500 text-sm border-t pt-8">
        <p>© 2024 தமிழ் திருக்கணித பஞ்சாங்கம். அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.</p>
        <p className="mt-1">வழங்குவது: அதிநவீன AI தொழில்நுட்பம்</p>
      </footer>
    </div>
  );
};

interface PanchangamItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

const PanchangamItem: React.FC<PanchangamItemProps> = ({ icon, label, value }) => (
  <div className="flex items-center gap-3">
    <div className="p-2 bg-gray-50 rounded-lg">{icon}</div>
    <div>
      <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">{label}</p>
      <p className="text-gray-800 font-medium">{value}</p>
    </div>
  </div>
);

interface TimingItemProps {
  label: string;
  value: string;
  color: string;
}

const TimingItem: React.FC<TimingItemProps> = ({ label, value, color }) => (
  <div className="flex justify-between items-center border-b border-white/40 pb-2 last:border-0">
    <span className="text-gray-600 font-medium">{label}</span>
    <span className={`font-bold ${color}`}>{value}</span>
  </div>
);

export default App;
