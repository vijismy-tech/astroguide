
import React, { useState, useEffect, useCallback } from 'react';
import { DISTRICTS } from './constants';
import { getDayName, getStaticTimings } from './utils/calculations';
import { fetchPanchangData } from './services/geminiService';
import { PanchangData, StaticTimings } from './types';

const App: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [selectedDist, setSelectedDist] = useState<string>("சென்னை");
  const [panchang, setPanchang] = useState<PanchangData | null>(null);
  const [staticTimes, setStaticTimes] = useState<StaticTimings>(getStaticTimings(new Date()));
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const dist = DISTRICTS[selectedDist];
      const data = await fetchPanchangData(selectedDate, selectedDist, dist.lat, dist.lon);
      setPanchang(data);
      setStaticTimes(getStaticTimings(selectedDate));
    } catch (err) {
      console.error(err);
      setError("தகவல்களைப் பெறுவதில் சிக்கல் ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.");
    } finally {
      setLoading(false);
    }
  }, [selectedDate, selectedDist]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="min-h-screen bg-[#FDFCF0] text-gray-800 pb-12">
      {/* Header */}
      <header className="bg-[#8B0000] text-white py-6 px-4 shadow-lg sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-center md:text-left">
            <h1 className="text-3xl font-bold tracking-tight mb-1">🔱 திருக்கணிதப் பஞ்சாங்கம்</h1>
            <p className="text-red-100 text-sm font-medium">அதி துல்லியமான ஜாதக மற்றும் காலக் கணிப்பு</p>
          </div>
          <div className="flex flex-wrap items-center gap-3 bg-white/10 p-2 rounded-lg">
            <select 
              value={selectedDist}
              onChange={(e) => setSelectedDist(e.target.value)}
              className="bg-white text-gray-800 px-3 py-1.5 rounded border-none font-semibold focus:ring-2 focus:ring-yellow-400 outline-none"
            >
              {Object.keys(DISTRICTS).map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <input 
              type="date" 
              value={selectedDate.toISOString().split('T')[0]}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
              className="bg-white text-gray-800 px-3 py-1.5 rounded border-none font-semibold focus:ring-2 focus:ring-yellow-400 outline-none"
            />
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 mt-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-[#8B0000]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-current mb-4"></div>
            <p className="font-bold">ஜோதிடக் கணக்கீடுகள் தயாராகிக் கொண்டிருக்கின்றன...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded shadow-sm">
            <p className="text-red-700 font-bold">{error}</p>
            <button 
              onClick={loadData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              மீண்டும் முயற்சிக்கவும்
            </button>
          </div>
        ) : panchang && (
          <div className="space-y-6">
            {/* Special Note Card */}
            <div className="bg-yellow-50 border-l-8 border-yellow-500 p-6 rounded-xl shadow-md transform hover:scale-[1.01] transition-transform">
              <h2 className="text-xl font-bold text-yellow-900 mb-2 flex items-center gap-2">
                ✨ இன்றைய சிறப்பு மற்றும் வழிபாடு
              </h2>
              <p className="text-yellow-800 leading-relaxed font-semibold">
                {panchang.tamilMonth} {panchang.tamilDate} | {getDayName(selectedDate)} - {panchang.specialSignificance}
              </p>
            </div>

            {/* Panchang Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Primary Data */}
              <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="bg-[#8B0000] px-6 py-4 text-white flex justify-between items-center">
                  <h3 className="font-bold text-lg">📅 பஞ்சாங்க விவரங்கள்</h3>
                  <span className="text-sm bg-white/20 px-2 py-1 rounded">திருக்கணித முறை</span>
                </div>
                <div className="p-0">
                  <table className="w-full text-left">
                    <tbody className="divide-y divide-gray-100">
                      <Row 
                        label="தமிழ் தேதி" 
                        value={`${panchang.tamilMonth} ${panchang.tamilDate}`} 
                        sub={`${getDayName(selectedDate)}`}
                        icon="🗓️"
                      />
                      <Row 
                        label="திதி சஞ்சாரம்" 
                        value={panchang.tithi} 
                        sub={`முடிவு: ${panchang.tithiEndTime}`}
                        badge={panchang.paksha}
                        icon="🌙"
                      />
                      <Row 
                        label="நட்சத்திரம்" 
                        value={panchang.nakshatram} 
                        sub={`முடிவு: ${panchang.nakEndTime}`}
                        extra={`அடுத்து: ${panchang.nextNak}`}
                        icon="⭐"
                      />
                      <Row 
                        label="யோகம்" 
                        value={panchang.yogam} 
                        icon="♈"
                      />
                      <Row 
                        label="கரணம்" 
                        value={panchang.karanam} 
                        icon="⚙️"
                      />
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Timing Data */}
              <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                <div className="bg-[#5D4037] px-6 py-4 text-white flex justify-between items-center">
                  <h3 className="font-bold text-lg">🕒 சுப/அசுப நேரங்கள்</h3>
                  <span className="text-sm bg-white/20 px-2 py-1 rounded">{selectedDist}</span>
                </div>
                <div className="p-0">
                  <table className="w-full text-left">
                    <tbody className="divide-y divide-gray-100">
                      <Row 
                        label="நல்ல நேரம்" 
                        value={staticTimes.nallaNeram} 
                        isAuspicious
                        icon="✨"
                      />
                      <Row 
                        label="கௌரி நல்ல நேரம்" 
                        value={staticTimes.gowri} 
                        isAuspicious
                        icon="🔱"
                      />
                      <Row 
                        label="ராகு காலம்" 
                        value={staticTimes.rahu} 
                        isInauspicious
                        icon="🚫"
                      />
                      <Row 
                        label="எமகண்டம்" 
                        value={staticTimes.yema} 
                        isInauspicious
                        icon="⌛"
                      />
                      <Row 
                        label="குளிகை" 
                        value={staticTimes.kuli} 
                        isInauspicious
                        icon="🕒"
                      />
                      <Row 
                        label="சூலம்" 
                        value={`${staticTimes.shoolam} திசை`} 
                        sub={`பரிகாரம்: ${staticTimes.shoolamPariharam}`}
                        icon="📍"
                      />
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* AI Assistant Section */}
            <div className="mt-8">
               <PanchangAI panchang={panchang} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-8 border-t border-gray-200 text-center text-gray-500 text-sm">
        <p>© {new Date().getFullYear()} Ultra Precise Tamil Panchangam AI. அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.</p>
        <p className="mt-2">குறிப்பு: இங்கு கொடுக்கப்பட்டுள்ள நேரங்கள் திருக்கணிதப் பஞ்சாங்க முறைப்படி AI தொழில்நுட்பத்தால் கணக்கிடப்பட்டவை.</p>
      </footer>
    </div>
  );
};

// Sub-components
const Row: React.FC<{ 
  label: string; 
  value: string | number; 
  sub?: string; 
  extra?: string;
  icon?: string;
  badge?: string;
  isAuspicious?: boolean;
  isInauspicious?: boolean;
}> = ({ label, value, sub, extra, icon, badge, isAuspicious, isInauspicious }) => {
  return (
    <tr className={`hover:bg-gray-50 transition-colors ${isInauspicious ? 'bg-red-50/30' : ''}`}>
      <td className="py-4 px-6 w-1/3">
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <span className="font-bold text-gray-600">{label}</span>
        </div>
      </td>
      <td className="py-4 px-6">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className={`font-extrabold text-lg ${isAuspicious ? 'text-green-700' : isInauspicious ? 'text-red-700' : 'text-gray-900'}`}>
              {value}
            </span>
            {badge && (
              <span className="bg-[#8B0000] text-white text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                {badge}
              </span>
            )}
          </div>
          {sub && <span className="text-sm text-gray-500 font-medium">{sub}</span>}
          {extra && <span className="text-xs text-blue-600 font-semibold mt-1">{extra}</span>}
        </div>
      </td>
    </tr>
  );
};

const PanchangAI: React.FC<{ panchang: PanchangData }> = ({ panchang }) => {
  return (
    <div className="bg-gradient-to-r from-[#8B0000] to-[#5D4037] rounded-2xl p-8 text-white shadow-2xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-20 -mt-20 blur-3xl group-hover:bg-white/20 transition-all duration-700"></div>
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-yellow-400 p-2 rounded-lg shadow-inner">
             <span className="text-2xl">🤖</span>
          </div>
          <h3 className="text-2xl font-bold">ஜோதிட AI ஆலோசகர்</h3>
        </div>
        <div className="space-y-4 max-w-3xl">
          <p className="text-red-50 leading-relaxed text-lg italic">
            "இன்று {panchang.tithi} திதி மற்றும் {panchang.nakshatram} நட்சத்திரம் கூடி வருவதால், இது ஒரு {panchang.paksha === 'வளர்பிறை' ? 'சுப' : 'ஆன்மீக ரீதியில் சிறந்த'} காலமாகும்."
          </p>
          <div className="grid md:grid-cols-2 gap-4 mt-6">
            <div className="bg-black/20 p-4 rounded-xl backdrop-blur-sm border border-white/10">
              <h4 className="font-bold text-yellow-400 mb-2 underline decoration-yellow-400/30">சந்திர நிலை:</h4>
              <p className="text-sm">நிலவு தற்போது {panchang.lunarPhase.toFixed(2)}° பாகையில் சஞ்சரிக்கிறது. இது மனோதிடத்தையும் செயல்திறனையும் பாதிக்கும் காரணியாகும்.</p>
            </div>
            <div className="bg-black/20 p-4 rounded-xl backdrop-blur-sm border border-white/10">
              <h4 className="font-bold text-yellow-400 mb-2 underline decoration-yellow-400/30">ஆலோசனை:</h4>
              <p className="text-sm">இன்று புதிய முயற்சிகளைத் தொடங்க {panchang.paksha === 'வளர்பிறை' ? 'மிகவும் உகந்த' : 'யோசனை செய்து செயல்பட வேண்டிய'} தினமாகும்.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
