import React, { useState } from 'react';
import { Play, Download, Video, Smartphone, Type, Info, Gauge } from 'lucide-react';

const ClipGallery = ({ clips, verticalClips, captionedClips, highlights }) => {
  const [showCaptions, setShowCaptions] = useState(true);
  if (!clips || clips.length === 0) return null;

  const baseUrl = 'http://127.0.0.1:8000/';

  return (
    <div className="w-full max-w-6xl mx-auto mt-16 space-y-12">
      <div className="text-center">
        <h2 className="text-4xl font-bold text-white mb-4">Your Repurposed Content</h2>
        <div className="flex items-center justify-center gap-4 mt-6">
          <button 
            onClick={() => setShowCaptions(!showCaptions)}
            className={`flex items-center gap-2 px-6 py-2 rounded-full border transition-all ${
              showCaptions 
              ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-600/20' 
              : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            <Type size={18} />
            {showCaptions ? 'Captions: Enabled' : 'Captions: Disabled'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {clips.map((clip, index) => {
          const highlight = highlights[index];
          return (
            <div key={index} className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl hover:border-purple-500/40 transition-all flex flex-col">
              {/* Video Preview */}
              <div className="aspect-video bg-black relative group">
                <video 
                  key={showCaptions ? 'captioned' : 'standard'}
                  src={showCaptions ? `${baseUrl}${captionedClips[index]}` : `${baseUrl}${clip}`} 
                  className="w-full h-full object-cover"
                  controls
                />
                <div className="absolute top-4 left-4 flex gap-2">
                  <span className="bg-black/60 backdrop-blur-md text-white text-[10px] font-bold px-2 py-1 rounded-full border border-white/10 flex items-center gap-1">
                    <Gauge size={10} className="text-purple-400" />
                    Impact Score: {highlight?.total_score}
                  </span>
                </div>
              </div>

              {/* Clip Info */}
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-4">
                  <h4 className="text-white font-bold text-lg">Clip #{index + 1}</h4>
                  <div className="flex gap-2">
                    <div className="group relative">
                      <Info size={14} className="text-slate-600 hover:text-slate-400 cursor-help" />
                      <div className="absolute bottom-full right-0 mb-2 w-48 p-2 bg-slate-800 rounded-lg text-[10px] text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity border border-slate-700 pointer-events-none z-10">
                        Sentiment: {highlight?.sentiment_score.toFixed(2)} | Keywords: {highlight?.keyword_score}
                      </div>
                    </div>
                  </div>
                </div>
                
                <p className="text-slate-400 text-sm mb-6 line-clamp-2 italic">
                  "{highlight?.text}"
                </p>

                <div className="mt-auto space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <a 
                      href={`${baseUrl}${clip}`} 
                      target="_blank"
                      className="flex items-center justify-center gap-2 p-2.5 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-xs text-slate-300"
                    >
                      <Video size={14} /> 16:9
                    </a>
                    <a 
                      href={`${baseUrl}${verticalClips[index]}`} 
                      target="_blank"
                      className="flex items-center justify-center gap-2 p-2.5 bg-slate-800 rounded-xl hover:bg-slate-700 transition-colors text-xs text-slate-300"
                    >
                      <Smartphone size={14} /> 9:16
                    </a>
                  </div>

                  <a 
                    href={`${baseUrl}${captionedClips[index]}`} 
                    target="_blank"
                    className="flex items-center justify-center gap-2 w-full py-3 bg-purple-500/10 border border-purple-500/20 rounded-xl hover:bg-purple-500/20 transition-colors text-sm text-purple-400 font-bold shadow-sm"
                  >
                    <Download size={16} /> Download Captioned Clip
                  </a>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ClipGallery;
