import React, { useState, useEffect } from 'react';
import { Upload, FileVideo, Loader2, CheckCircle2 } from 'lucide-react';

const LOADING_STAGES = [
  "Uploading video to server...",
  "Extracting audio track...",
  "Transcribing with AI (OpenAI Whisper)...",
  "Analyzing sentiment and keywords...",
  "Detecting high-impact moments...",
  "Generating social media clips...",
  "Adding caption overlays...",
  "Finalizing results..."
];

const UploadCard = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setStageIndex((prev) => (prev < LOADING_STAGES.length - 1 ? prev + 1 : prev));
      }, 8000); // Progress stage every 8 seconds (typical processing time)
    } else {
      setStageIndex(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid video file.');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setStageIndex(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload-video', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed. Processing large videos might take longer.');
      }

      const data = await response.json();
      onUploadSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl w-full max-w-md mx-auto relative overflow-hidden">
      <div className="flex flex-col items-center gap-6">
        <div className="w-16 h-16 bg-purple-500/10 rounded-full flex items-center justify-center text-purple-500">
          <FileVideo size={32} />
        </div>
        
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Repurpose Video</h2>
          <p className="text-slate-400 text-sm">Convert long-form to short-form in one click</p>
        </div>

        <div className="w-full">
          {!loading ? (
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-700 rounded-xl cursor-pointer hover:border-purple-500/50 hover:bg-slate-800/50 transition-all">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="text-slate-500 mb-2" size={24} />
                <p className="text-sm text-slate-500 px-4 text-center">
                  {file ? (
                    <span className="text-purple-400 font-medium truncate max-w-[200px] block">{file.name}</span>
                  ) : (
                    "Choose video file"
                  )}
                </p>
              </div>
              <input type="file" className="hidden" accept="video/*" onChange={handleFileChange} />
            </label>
          ) : (
            <div className="flex flex-col items-center justify-center w-full h-32 bg-slate-800/30 border border-slate-700 rounded-xl p-4">
              <Loader2 className="animate-spin text-purple-500 mb-3" size={32} />
              <div className="text-center">
                <p className="text-white text-sm font-medium animate-pulse">{LOADING_STAGES[stageIndex]}</p>
                <div className="mt-2 flex gap-1 justify-center">
                  {LOADING_STAGES.map((_, i) => (
                    <div 
                      key={i} 
                      className={`h-1 w-4 rounded-full transition-colors ${i <= stageIndex ? 'bg-purple-500' : 'bg-slate-700'}`}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="text-red-400 text-sm bg-red-400/10 p-3 rounded-lg w-full text-center">
            {error}
          </div>
        )}

        {!loading && (
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              !file || loading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-xl shadow-purple-600/20'
            }`}
          >
            Start Magic Engine
          </button>
        )}
      </div>
    </div>
  );
};

export default UploadCard;
