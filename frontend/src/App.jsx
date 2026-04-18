import React, { useState } from 'react';
import UploadCard from './components/UploadCard';
import TranscriptViewer from './components/TranscriptViewer';
import ClipGallery from './components/ClipGallery';
import { Sparkles } from 'lucide-react';

function App() {
  const [result, setResult] = useState(null);

  const handleUploadSuccess = (data) => {
    console.log("Upload Success:", data);
    setResult(data);
  };

  return (
    <div className="min-h-screen bg-[#08060d] text-slate-300 font-sans selection:bg-purple-500/30">
      {/* Header */}
      <nav className="border-b border-slate-800 bg-[#08060d]/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles size={18} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">AttentionX</span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium">
            <a href="#" className="hover:text-white transition-colors">Documentation</a>
            <a href="#" className="bg-white text-black px-4 py-1.5 rounded-full hover:bg-slate-200 transition-colors">Sign In</a>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-20 flex flex-col items-center">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
            Repurpose your content <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              with AI intelligence.
            </span>
          </h1>
          <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto">
            Transform long videos into engaging short-form clips automatically. 
            Upload, transcribe, and extract the best moments in seconds.
          </p>
        </div>

        <UploadCard onUploadSuccess={handleUploadSuccess} />

        {result && (
          <>
            <ClipGallery 
              clips={result.clips} 
              verticalClips={result.vertical_clips} 
              captionedClips={result.captioned_clips} 
              highlights={result.highlights}
            />
            <TranscriptViewer 
              segments={result.segments} 
              filename={result.filename} 
            />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-20 py-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-500 text-sm">
          &copy; 2026 AttentionX - Automated Content Repurposing Engine. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;
