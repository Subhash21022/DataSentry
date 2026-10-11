import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Upload, 
  AlertTriangle, 
  BarChart3, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  FileText, 
  Sparkles,
  Database,
  ArrowUpRight
} from 'lucide-react';

interface QualityScore {
  score: number;
  grade: string;
  pillars: {
    completeness: number;
    uniqueness: number;
    validity: number;
  };
}

interface ColumnMeta {
  name: string;
  pandas_dtype: string;
  semantic_type: string;
  null_count: number;
  null_percentage: number;
  distinct_count: number;
  min?: number;
  max?: number;
  mean?: number;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'profiler' | 'ml' | 'rules' | 'preview'>('profiler');
  const [isUploading, setIsUploading] = useState(false);

  // Demo profile data (populated by backend or default)
  const [profileData, setProfileData] = useState({
    fileName: 'sample.csv',
    summary: {
      row_count: 20,
      column_count: 7,
      duplicate_rows: 1,
      total_missing_cells: 2,
      memory_usage_kb: 3.4,
    },
    quality_score: {
      score: 87.5,
      grade: 'B',
      pillars: { completeness: 95.0, uniqueness: 95.0, validity: 70.0 },
    } as QualityScore,
    columns: {
      id: { name: 'id', pandas_dtype: 'int64', semantic_type: 'numeric', null_count: 0, null_percentage: 0, distinct_count: 20, min: 1, max: 20, mean: 10.5 },
      name: { name: 'name', pandas_dtype: 'object', semantic_type: 'text', null_count: 0, null_percentage: 0, distinct_count: 19 },
      email: { name: 'email', pandas_dtype: 'object', semantic_type: 'email', null_count: 1, null_percentage: 5.0, distinct_count: 19 },
      age: { name: 'age', pandas_dtype: 'int64', semantic_type: 'numeric', null_count: 0, null_percentage: 0, distinct_count: 18, min: -5, max: 65, mean: 34.2 },
      salary: { name: 'salary', pandas_dtype: 'float64', semantic_type: 'numeric', null_count: 1, null_percentage: 5.0, distinct_count: 18, min: 28000, max: 1200000, mean: 184526 },
      country: { name: 'country', pandas_dtype: 'object', semantic_type: 'categorical', null_count: 0, null_percentage: 0, distinct_count: 4 },
      signup_date: { name: 'signup_date', pandas_dtype: 'object', semantic_type: 'date_string', null_count: 0, null_percentage: 0, distinct_count: 19 },
    } as Record<string, ColumnMeta>,
    cleaning_suggestions: [
      { type: 'deduplication', severity: 'medium', message: 'Found 1 duplicate row. Michael Scott appears twice with identical values.' },
      { type: 'validity', severity: 'high', message: "Column 'age' contains negative values (e.g., -5). Apply lower boundary filter." },
      { type: 'imputation', severity: 'low', message: "Column 'salary' has 1 missing value. Recommend median imputation ($75,000)." },
    ],
    anomalies: [
      { row_index: 19, anomaly_score: 0.982, suspected_primary_feature: 'salary', feature_z_score: 4.8, data: { name: 'Suspicious Bot', age: 18, salary: 1200000, country: 'Nowhere' } },
      { row_index: 6, anomaly_score: 0.894, suspected_primary_feature: 'salary', feature_z_score: 3.9, data: { name: 'George Clark', age: 19, salary: 950000, country: 'UK' } },
      { row_index: 7, anomaly_score: 0.741, suspected_primary_feature: 'age', feature_z_score: -3.2, data: { name: 'Hannah Abbott', age: -5, salary: 54000, country: 'UK' } },
    ],
    rules: [
      { id: 'R1', description: "Required columns check (id, name, email)", passed: true, violations: 0 },
      { id: 'R2', description: "Email valid syntax regex check", passed: false, violations: 2 },
      { id: 'R3', description: "Age must be >= 0 and <= 120", passed: false, violations: 1 },
      { id: 'R4', description: "Country must be in [USA, UK, Canada]", passed: false, violations: 1 },
      { id: 'R5', description: "Primary Key 'id' not null constraint", passed: true, violations: 0 },
    ]
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/profile', {
        method: 'POST',
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setProfileData(prev => ({
          ...prev,
          fileName: file.name,
          summary: data.summary,
          quality_score: data.quality_score,
          columns: data.columns,
          cleaning_suggestions: data.cleaning_suggestions || [],
        }));
      }
    } catch (err) {
      console.error('Failed to upload to backend, running in offline demo mode:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 80) return 'text-sky-400 border-sky-500/30 bg-sky-500/10';
    if (score >= 70) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  return (
    <div className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-[#0d1424]/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                DataSentry
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium">
                SWOC 2025 Edition
              </span>
            </div>
            <p className="text-xs text-slate-400">All-in-One Data Quality & ML Observability Platform</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold cursor-pointer transition shadow-md shadow-sky-600/20">
            <Upload className="h-4 w-4" />
            <span>{isUploading ? 'Analyzing...' : 'Upload CSV'}</span>
            <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
          </label>
          <a 
            href="https://github.com" 
            target="_blank" 
            rel="noreferrer"
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition flex items-center gap-1 border border-slate-700/60"
          >
            <span>GitHub</span>
            <ArrowUpRight className="h-3 w-3" />
          </a>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        
        {/* Dataset Header Card */}
        <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-2xl p-6 backdrop-blur flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-sky-400" />
              <span className="text-sm font-semibold text-slate-300">Active Dataset:</span>
              <span className="text-sm font-mono text-sky-300 bg-sky-950/60 px-2 py-0.5 rounded border border-sky-800/50">
                {profileData.fileName}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">Quality Inspection Overview</h2>
            <p className="text-xs text-slate-400">
              Evaluated with DataSentry Core Engine • Scikit-Learn Isolation Forest • Deterministic Validator
            </p>
          </div>

          {/* Quality Score Radial Badge */}
          <div className="flex items-center gap-6">
            <div className={`px-5 py-3 rounded-xl border flex items-center gap-4 ${getScoreColor(profileData.quality_score.score)}`}>
              <div>
                <div className="text-3xl font-black">{profileData.quality_score.score}%</div>
                <div className="text-[11px] font-semibold uppercase tracking-wider opacity-80">
                  Grade {profileData.quality_score.grade} Quality
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* KPI Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#0f172a]/60 border border-slate-800/60 rounded-xl p-4">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Total Records</span>
            <p className="text-2xl font-bold text-white mt-1">{profileData.summary.row_count}</p>
            <span className="text-[11px] text-slate-500">Across {profileData.summary.column_count} columns</span>
          </div>
          <div className="bg-[#0f172a]/60 border border-slate-800/60 rounded-xl p-4">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Duplicate Rows</span>
            <p className={`text-2xl font-bold mt-1 ${profileData.summary.duplicate_rows > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {profileData.summary.duplicate_rows}
            </p>
            <span className="text-[11px] text-slate-500">Exact hash collisions</span>
          </div>
          <div className="bg-[#0f172a]/60 border border-slate-800/60 rounded-xl p-4">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Missing Cells</span>
            <p className={`text-2xl font-bold mt-1 ${profileData.summary.total_missing_cells > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {profileData.summary.total_missing_cells}
            </p>
            <span className="text-[11px] text-slate-500">Requires imputation</span>
          </div>
          <div className="bg-[#0f172a]/60 border border-slate-800/60 rounded-xl p-4">
            <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">ML Anomalies</span>
            <p className="text-2xl font-bold text-indigo-400 mt-1">{profileData.anomalies.length}</p>
            <span className="text-[11px] text-slate-500">Isolation Forest flags</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800/80 gap-2">
          <button
            onClick={() => setActiveTab('profiler')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition ${
              activeTab === 'profiler'
                ? 'bg-slate-800/80 text-sky-400 border-b-2 border-sky-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            <span>Column Profiling & Types</span>
          </button>
          <button
            onClick={() => setActiveTab('ml')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition ${
              activeTab === 'ml'
                ? 'bg-slate-800/80 text-indigo-400 border-b-2 border-indigo-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span>ML Anomaly Detector</span>
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold rounded-t-lg transition ${
              activeTab === 'rules'
                ? 'bg-slate-800/80 text-emerald-400 border-b-2 border-emerald-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="h-4 w-4" />
            <span>Validation Rules</span>
          </button>
        </div>

        {/* Tab 1: Column Profiler */}
        {activeTab === 'profiler' && (
          <div className="space-y-6">
            <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl overflow-hidden shadow-lg">
              <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
                <h3 className="font-semibold text-sm text-slate-200">Schema & Column Metrics</h3>
                <span className="text-xs text-slate-500">Auto-detected types & statistics</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/60 text-slate-400 font-medium border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3">Column</th>
                      <th className="px-6 py-3">Semantic Type</th>
                      <th className="px-6 py-3">Pandas Type</th>
                      <th className="px-6 py-3">Missingness</th>
                      <th className="px-6 py-3">Distinct Values</th>
                      <th className="px-6 py-3">Summary Stats</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/40 text-slate-300">
                    {Object.entries(profileData.columns).map(([colName, meta]) => (
                      <tr key={colName} className="hover:bg-slate-800/30 transition">
                        <td className="px-6 py-3.5 font-medium text-white">{meta.name}</td>
                        <td className="px-6 py-3.5">
                          <span className="px-2 py-0.5 rounded bg-sky-950/70 text-sky-300 border border-sky-800/40 text-[11px] font-mono">
                            {meta.semantic_type}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 font-mono text-slate-400">{meta.pandas_dtype}</td>
                        <td className="px-6 py-3.5">
                          <span className={meta.null_count > 0 ? 'text-rose-400 font-semibold' : 'text-slate-400'}>
                            {meta.null_count} ({meta.null_percentage}%)
                          </span>
                        </td>
                        <td className="px-6 py-3.5">{meta.distinct_count}</td>
                        <td className="px-6 py-3.5 text-slate-400">
                          {meta.min !== undefined ? `[${meta.min} .. ${meta.max}], mean: ${meta.mean}` : 'Categorical text'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Smart Cleaning Suggestions */}
            <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-amber-400" />
                <h3 className="font-semibold text-sm text-slate-200">AI & Heuristic Cleaning Recommendations</h3>
              </div>
              <div className="grid gap-3">
                {profileData.cleaning_suggestions.map((s, idx) => (
                  <div key={idx} className="p-3.5 rounded-lg bg-slate-900/60 border-l-4 border-amber-500 text-xs flex items-start gap-3">
                    <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-amber-300 uppercase tracking-wider text-[10px] mr-2">
                        [{s.type} - {s.severity}]
                      </span>
                      <span className="text-slate-300">{s.message}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: ML Anomaly Detector */}
        {activeTab === 'ml' && (
          <div className="space-y-6">
            <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-indigo-400" />
                    Unsupervised Isolation Forest Engine
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Detects multivariate tabular outliers and anomalous patterns without requiring pre-labeled training data.
                  </p>
                </div>
                <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-xs font-semibold">
                  Contamination: 5%
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/60 text-slate-400 font-medium border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3">Row Index</th>
                      <th className="px-6 py-3">Anomaly Score</th>
                      <th className="px-6 py-3">Suspicious Primary Feature</th>
                      <th className="px-6 py-3">Record Snapshot</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/40 text-slate-300">
                    {profileData.anomalies.map((anom) => (
                      <tr key={anom.row_index} className="hover:bg-slate-800/30 transition">
                        <td className="px-6 py-3.5 font-mono text-slate-400">Row #{anom.row_index}</td>
                        <td className="px-6 py-3.5">
                          <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono font-bold">
                            {(anom.anomaly_score * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-3.5">
                          <span className="font-semibold text-indigo-300">{anom.suspected_primary_feature}</span>
                          <span className="text-slate-500 text-[11px] ml-1.5">(z={anom.feature_z_score})</span>
                        </td>
                        <td className="px-6 py-3.5 font-mono text-slate-400">
                          {JSON.stringify(anom.data)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Rules Validation */}
        {activeTab === 'rules' && (
          <div className="bg-[#0f172a]/70 border border-slate-800/80 rounded-xl overflow-hidden shadow-lg">
            <div className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
              <h3 className="font-semibold text-sm text-slate-200">Configured Quality Rules</h3>
              <span className="text-xs text-slate-400">Automated Pipeline Gates</span>
            </div>
            <div className="divide-y divide-slate-800/40 text-xs">
              {profileData.rules.map((rule) => (
                <div key={rule.id} className="px-6 py-4 flex items-center justify-between hover:bg-slate-800/30 transition">
                  <div className="flex items-center gap-3">
                    {rule.passed ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                    ) : (
                      <XCircle className="h-5 w-5 text-rose-400 shrink-0" />
                    )}
                    <div>
                      <span className="font-semibold text-slate-200">{rule.description}</span>
                      <p className="text-[11px] text-slate-500 font-mono mt-0.5">Rule ID: {rule.id}</p>
                    </div>
                  </div>
                  <div>
                    {rule.passed ? (
                      <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
                        PASSED
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 font-semibold border border-rose-500/20">
                        {rule.violations} VIOLATION{rule.violations > 1 ? 'S' : ''}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500">
        DataSentry — Open-Source All-in-One Data Quality Platform • Ready for Social Winter of Code (SWOC)
      </footer>
    </div>
  );
}
