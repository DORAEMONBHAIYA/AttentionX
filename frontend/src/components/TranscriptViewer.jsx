import React from 'react';
import { Clock, AlignLeft } from 'lucide-react';

const TranscriptViewer = ({ segments, filename }) => {
  if (!segments || segments.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl w-full max-w-2xl mx-auto mt-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center text-blue-500">
            <AlignLeft size={20} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Generated Transcript</h3>
            <p className="text-slate-400 text-xs">{filename}</p>
          </div>
        </div>
        <div className="px-3 py-1 bg-slate-800 rounded-full text-xs font-medium text-slate-300">
          {segments.length} Segments
        </div>
      </div>

      <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        {segments.map((segment, index) => (
          <div 
            key={index} 
            className="group flex gap-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-purple-500/30 transition-all"
          >
            <div className="flex items-start pt-1">
              <div className="flex items-center gap-1 px-2 py-1 bg-slate-900 rounded text-[10px] font-mono text-purple-400 border border-slate-700">
                <Clock size={10} />
                {segment.start}s - {segment.end}s
              </div>
            </div>
            <div className="flex-1">
              <p className="text-slate-300 text-sm leading-relaxed">
                {segment.text}
              </p>
            </div>
          </div>
        ))}
      </div>
      
      <style jsx="true">{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #334155;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #475569;
        }
      `}</style>
    </div>
  );
};

export default TranscriptViewer;
