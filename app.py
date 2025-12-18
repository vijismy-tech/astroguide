
import React, { useState, useMemo, useEffect } from 'react';
import { Transaction, TransactionType, Category, CATEGORY_COLORS, TAMIL_DISTRICTS, PanchangData } from './types';
import { getSavingsTips, getPanchangData } from './geminiService';

const App: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [type, setType] = useState<TransactionType>('expense');
  const [category, setCategory] = useState<Category>('Food');
  const [amount, setAmount] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  
  // Panchang State
  const [selectedDistrict, setSelectedDistrict] = useState<string>("Chennai");
  const [panchang, setPanchang] = useState<PanchangData | null>(null);
  const [loadingPanchang, setLoadingPanchang] = useState(false);

  const [aiTips, setAiTips] = useState<string | null>(null);
  const [loadingTips, setLoadingTips] = useState(false);

  // Auto-fetch Panchang when district or date changes
  useEffect(() => {
    const fetchPanchang = async () => {
      setLoadingPanchang(true);
      try {
        const data = await getPanchangData(date, selectedDistrict);
        setPanchang(data);
      } catch (err) {
        console.error("Failed to load panchang");
      } finally {
        setLoadingPanchang(false);
      }
    };
    fetchPanchang();
  }, [date, selectedDistrict]);

  const summary = useMemo(() => {
    const income = transactions.filter(t => t.type === 'income').reduce((a, b) => a + b.amount, 0);
    const expense = transactions.filter(t => t.type === 'expense').reduce((a, b) => a + b.amount, 0);
    return { income, expense, savings: income - expense };
  }, [transactions]);

  const expenseChartData = useMemo(() => {
    const expenses = transactions.filter(t => t.type === 'expense');
    const total = expenses.reduce((a, b) => a + b.amount, 0);
    const grouped = expenses.reduce((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + t.amount;
      return acc;
    }, {} as Record<string, number>);

    let currentAngle = 0;
    return Object.entries(grouped).map(([cat, amt]) => {
      const percentage = total > 0 ? (amt / total) : 0;
      const angle = percentage * 360;
      const startAngle = currentAngle;
      currentAngle += angle;
      return { category: cat as Category, percentage, startAngle, angle };
    });
  }, [transactions]);

  const addTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    const numAmount = parseFloat(amount);
    if (!amount || isNaN(numAmount) || numAmount <= 0) return;

    const newTransaction: Transaction = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      category,
      amount: numAmount,
      description,
      date
    };

    setTransactions(prev => [newTransaction, ...prev]);
    setAmount('');
    setDescription('');
  };

  const deleteTransaction = (id: string) => {
    setTransactions(prev => prev.filter(t => t.id !== id));
  };

  const fetchAiTips = async () => {
    if (transactions.length === 0) return;
    setLoadingTips(true);
    try {
      const tips = await getSavingsTips(transactions);
      setAiTips(tips);
    } finally {
      setLoadingTips(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-slate-900 rounded-2xl">
            <svg className="w-8 h-8 text-emerald-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">SmartSpend AI</h1>
            <p className="text-slate-500 font-medium text-sm">Finances & Daily Insights</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select 
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="bg-white border border-slate-200 text-slate-600 text-xs font-bold py-2 px-4 rounded-full outline-none focus:ring-2 focus:ring-emerald-500 transition-all cursor-pointer"
          >
            {TAMIL_DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <div className="bg-emerald-100 text-emerald-700 px-4 py-2 rounded-full font-bold text-xs uppercase tracking-wider">
            {new Date().toLocaleString('default', { month: 'short', year: 'numeric' })}
          </div>
        </div>
      </header>

      {/* Astro Section */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-3 bg-gradient-to-br from-amber-500 to-orange-600 rounded-3xl p-6 shadow-xl shadow-orange-100 text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
            <svg className="w-48 h-48" fill="currentColor" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0s-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>
          </div>
          <div className="relative z-10 flex flex-col md:flex-row justify-between items-center h-full gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="bg-white/20 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest">Surya Timings</span>
                <span className="text-orange-100 text-xs font-semibold">{selectedDistrict} District</span>
              </div>
              <div className="flex items-baseline gap-6">
                <div>
                  <p className="text-orange-100 text-[10px] uppercase font-bold">Udayam (Sunrise)</p>
                  <p className="text-4xl font-black">{loadingPanchang ? '...' : panchang?.sunrise || '--:-- AM'}</p>
                </div>
                <div className="h-10 w-[1px] bg-white/20 self-end mb-1"></div>
                <div>
                  <p className="text-orange-100 text-[10px] uppercase font-bold">Asthamanam (Sunset)</p>
                  <p className="text-4xl font-black">{loadingPanchang ? '...' : panchang?.sunset || '--:-- PM'}</p>
                </div>
              </div>
            </div>
            <div className="flex gap-4 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
               <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl min-w-[120px] border border-white/10">
                <p className="text-orange-100 text-[10px] uppercase font-bold mb-1">Tithi</p>
                <p className="text-sm font-bold truncate">{loadingPanchang ? 'Loading...' : panchang?.tithi || '---'}</p>
               </div>
               <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl min-w-[120px] border border-white/10">
                <p className="text-orange-100 text-[10px] uppercase font-bold mb-1">Nakshatra</p>
                <p className="text-sm font-bold truncate">{loadingPanchang ? 'Loading...' : panchang?.nakshatra || '---'}</p>
               </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 flex flex-col justify-center">
          <p className="text-slate-400 text-[10px] uppercase font-bold mb-2 tracking-widest text-center">Auspicious Balance</p>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs text-slate-500">Rahu:</span>
              <span className="text-xs font-bold text-rose-500">{panchang?.rahukalam || '--'}</span>
            </div>
            <div className="h-[1px] bg-slate-50 w-full"></div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-slate-500">Yema:</span>
              <span className="text-xs font-bold text-orange-500">{panchang?.yamagandam || '--'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6 rounded-2xl shadow-sm border-l-4 border-emerald-500">
          <p className="text-slate-500 text-sm font-medium">Income</p>
          <p className="text-2xl font-bold text-slate-900">${summary.income.toLocaleString()}</p>
        </div>
        <div className="glass-card p-6 rounded-2xl shadow-sm border-l-4 border-rose-500">
          <p className="text-slate-500 text-sm font-medium">Expenses</p>
          <p className="text-2xl font-bold text-slate-900">${summary.expense.toLocaleString()}</p>
        </div>
        <div className="glass-card p-6 rounded-2xl shadow-sm border-l-4 border-blue-500">
          <p className="text-slate-500 text-sm font-medium">Savings</p>
          <p className={`text-2xl font-bold ${summary.savings >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
            ${summary.savings.toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-8">
          <section className="glass-card p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-slate-800">
              <span className="p-1.5 bg-slate-100 rounded-lg">➕</span> Transaction
            </h2>
            <form onSubmit={addTransaction} className="space-y-4">
              <div className="flex bg-slate-100 p-1 rounded-lg">
                <button 
                  type="button"
                  onClick={() => { setType('expense'); setCategory('Food'); }}
                  className={`flex-1 py-1.5 rounded-md text-sm font-medium transition-all ${type === 'expense' ? 'bg-white shadow-sm text-rose-600' : 'text-slate-500'}`}
                >
                  Expense
                </button>
                <button 
                  type="button"
                  onClick={() => { setType('income'); setCategory('Salary'); }}
                  className={`flex-1 py-1.5 rounded-md text-sm font-medium transition-all ${type === 'income' ? 'bg-white shadow-sm text-emerald-600' : 'text-slate-500'}`}
                >
                  Income
                </button>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Category</label>
                <select 
                  value={category}
                  onChange={(e) => setCategory(e.target.value as Category)}
                  className="w-full p-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none transition-all cursor-pointer"
                >
                  {type === 'income' ? (
                    <>
                      <option value="Salary">Salary</option>
                      <option value="Investment">Investment</option>
                      <option value="Freelance">Freelance</option>
                      <option value="Gift">Gift</option>
                    </>
                  ) : (
                    <>
                      <option value="Food">Food</option>
                      <option value="Rent">Rent</option>
                      <option value="Transport">Transport</option>
                      <option value="Shopping">Shopping</option>
                      <option value="Entertainment">Entertainment</option>
                      <option value="Utilities">Utilities</option>
                      <option value="Health">Health</option>
                      <option value="Other">Other</option>
                    </>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Amount</label>
                <input 
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full p-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none"
                  required
                />
              </div>

              <button type="submit" className="w-full py-3 bg-slate-900 text-white rounded-xl font-semibold hover:bg-slate-800 transition-all shadow-lg active:scale-95">
                Add Entry
              </button>
            </form>
          </section>

          <section className="glass-card p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-semibold mb-6">Expense Analysis</h2>
            {expenseChartData.length > 0 ? (
              <div className="flex flex-col items-center">
                <svg viewBox="0 0 100 100" className="w-40 h-40 transform -rotate-90 drop-shadow-sm">
                  {expenseChartData.map((slice, i) => {
                    const radius = 35;
                    const circumference = 2 * Math.PI * radius;
                    const strokeDasharray = `${(slice.percentage * circumference)} ${circumference}`;
                    const strokeDashoffset = - (slice.startAngle / 360) * circumference;
                    return (
                      <circle
                        key={i}
                        cx="50"
                        cy="50"
                        r={radius}
                        fill="transparent"
                        stroke={CATEGORY_COLORS[slice.category]}
                        strokeWidth="18"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={strokeDashoffset}
                        className="transition-all duration-500"
                      />
                    );
                  })}
                </svg>
                <div className="mt-8 grid grid-cols-2 gap-x-4 gap-y-2 w-full">
                  {expenseChartData.map((slice, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: CATEGORY_COLORS[slice.category] }}></div>
                      <span className="text-slate-600 truncate">{slice.category}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-10 text-center">
                <p className="text-slate-400 text-sm">Add expenses to visualize data</p>
              </div>
            )}
          </section>
        </div>

        <div className="lg:col-span-8 space-y-8">
          <section className="bg-slate-900 text-white p-6 rounded-3xl shadow-xl relative overflow-hidden">
             <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
              <svg className="w-48 h-48" fill="currentColor" viewBox="0 0 24 24"><path d="M11.5 2C6.81 2 3 5.81 3 10.5S6.81 19 11.5 19h.5v3l4.5-4.5H21V10.5C21 5.81 17.19 2 12.5 2z"/></svg>
            </div>
            <div className="relative z-10">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <span className="text-emerald-400">✨</span> AI Savings Guru
                </h2>
                <button 
                  onClick={fetchAiTips}
                  disabled={loadingTips || transactions.length === 0}
                  className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 text-white text-xs font-bold rounded-full transition-all active:scale-95"
                >
                  {loadingTips ? 'Analyzing...' : 'Refresh Advice'}
                </button>
              </div>
              
              <div className="bg-slate-800/50 rounded-2xl p-6 min-h-[120px] border border-slate-700/50">
                {aiTips ? (
                  <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                    {aiTips}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm italic text-center py-4">
                    {transactions.length === 0 
                      ? "Your AI advisor needs spending history to provide insights." 
                      : "Click refresh to generate personalized financial advice."}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="glass-card rounded-3xl shadow-sm overflow-hidden border border-slate-100">
            <div className="p-6 border-b border-slate-50 flex justify-between items-center bg-white">
              <h2 className="text-lg font-bold text-slate-800">Transaction History</h2>
              <input 
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="text-xs font-bold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg border-none outline-none"
              />
            </div>
            <div className="max-h-[500px] overflow-y-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-50 sticky top-0 text-slate-400 text-[10px] uppercase font-bold tracking-wider z-20">
                  <tr>
                    <th className="px-6 py-4">Item</th>
                    <th className="px-6 py-4">Category</th>
                    <th className="px-6 py-4 text-right">Amount</th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {transactions.map((t) => (
                    <tr key={t.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="px-6 py-5">
                        <p className="text-sm font-semibold text-slate-800">{t.description || t.category}</p>
                        <p className="text-[10px] text-slate-400 uppercase font-bold mt-0.5">{new Date(t.date).toLocaleDateString()}</p>
                      </td>
                      <td className="px-6 py-5">
                        <span 
                          className="px-2.5 py-1 rounded-md text-[9px] font-black text-white uppercase tracking-wider"
                          style={{ backgroundColor: CATEGORY_COLORS[t.category] }}
                        >
                          {t.category}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <span className={`text-sm font-black ${t.type === 'income' ? 'text-emerald-600' : 'text-slate-800'}`}>
                          {t.type === 'income' ? '+' : '-'}${t.amount.toLocaleString()}
                        </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <button 
                          onClick={() => deleteTransaction(t.id)}
                          className="text-slate-300 hover:text-rose-500 transition-colors p-2 rounded-lg hover:bg-rose-50"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {transactions.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-24 text-center text-slate-400">
                        <div className="flex flex-col items-center gap-2 opacity-40">
                          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                          <p className="text-sm font-medium tracking-wide">Ready for your first transaction</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default App;
