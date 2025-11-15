"use client";

import { useState } from "react";
import axios from "axios";
import { FiUploadCloud, FiFile, FiCopy } from "react-icons/fi";

interface MetadataResponse {
  file: string;
  type: string;
  metadata: Record<string, any>;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<MetadataResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"visual" | "json">("visual");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const extract = async () => {
    if (!file) {
      setError("Select a file first.");
      return;
    }
    setLoading(true);
    setError("");

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await axios.post<MetadataResponse>("https://8fef0bdee70b.ngrok-free.app/extract", form);
      setResult(res.data);
    } catch {
      setError("Backend error. Check FastAPI.");
    }
    setLoading(false);
  };

  const copyJSON = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result.metadata, null, 2));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-4 md:p-10">
      <div className="w-full max-w-5xl mx-auto">

        {/* HEADER */}
        <h1 className="text-3xl md:text-5xl font-extrabold text-center mb-4 md:mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
          FOCA Mini – OSINT Metadata Extractor
        </h1>

        <p className="text-center text-gray-300 mb-6 md:mb-10 text-sm md:text-base">
          Upload documents, images, videos & extract forensic metadata
        </p>

        {/* UPLOAD BOX */}
        <div className="bg-white/10 border border-white/10 rounded-2xl p-6 md:p-10 backdrop-blur-lg shadow-xl">
          <label className="cursor-pointer flex flex-col items-center border-2 border-dashed border-gray-600 p-6 md:p-10 rounded-xl hover:bg-white/5 transition w-full">
            <FiUploadCloud className="text-5xl md:text-6xl text-blue-400 mb-3" />
            <p className="text-gray-300 text-sm md:text-lg text-center break-all">
              {file ? <span className="text-green-400">{file.name}</span> : "Tap to upload a file"}
            </p>

            <input
              type="file"
              className="hidden"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                }
              }}
            />
          </label>

          <button
            onClick={extract}
            className="mt-4 md:mt-6 w-full bg-gradient-to-r from-blue-600 to-cyan-500 py-2.5 md:py-3 rounded-xl font-semibold hover:opacity-90 transition text-sm md:text-base"
          >
            {loading ? "Extracting..." : "Extract Metadata"}
          </button>

          {error && <p className="text-red-400 mt-3 text-center text-sm">{error}</p>}
        </div>

        {/* RESULTS */}
        {result && (
          <div className="mt-8 md:mt-10 bg-white/10 border border-white/20 rounded-2xl p-6 md:p-8 backdrop-blur-xl shadow-xl">
            {/* FILE INFO */}
            <h2 className="text-2xl md:text-3xl font-bold flex items-center gap-2 mb-4">
              <FiFile className="text-blue-300 text-2xl md:text-3xl" />
              Metadata Report
            </h2>

            <p className="text-blue-400 text-sm md:text-lg">
              File: <span className="text-gray-200 break-all">{result.file}</span>
            </p>
            <p className="text-blue-400 text-sm md:text-lg mb-6">
              Type: <span className="text-gray-200">{result.type}</span>
            </p>

            {/* TABS */}
            <div className="flex gap-3 mb-6">
              <button
                onClick={() => setActiveTab("visual")}
                className={`px-3 py-2 md:px-4 md:py-2 text-sm rounded-lg ${
                  activeTab === "visual" ? "bg-blue-600" : "bg-gray-700"
                } transition w-full md:w-auto`}
              >
                Visual View
              </button>

              <button
                onClick={() => setActiveTab("json")}
                className={`px-3 py-2 md:px-4 md:py-2 text-sm rounded-lg ${
                  activeTab === "json" ? "bg-blue-600" : "bg-gray-700"
                } transition w-full md:w-auto`}
              >
                Raw JSON
              </button>
            </div>

            {/* VISUAL VIEW */}
            {activeTab === "visual" && (
              <div className="space-y-6">

                {/* HASHES */}
                {result.metadata.hashes && (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10">
                    <h3 className="text-lg font-semibold mb-3">🔐 File Hashes</h3>

                    <div className="space-y-3">
                      {Object.entries(result.metadata.hashes).map(([key, value]) => (
                        <div
                          key={key}
                          className="flex flex-col bg-gray-900/60 p-3 rounded-lg border border-gray-700/40 break-all"
                        >
                          <span className="text-blue-400 text-xs md:text-sm font-semibold">{key.toUpperCase()}</span>
                          <span className="text-gray-300 text-xs md:text-sm break-all">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* GPS */}
                {result.metadata.gps_map && (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10">
                    <h3 className="text-lg font-semibold mb-3">📍 GPS Location</h3>
                    <a
                      href={result.metadata.gps_map}
                      target="_blank"
                      className="text-cyan-400 underline break-all text-sm md:text-base"
                    >
                      Open in Google Maps
                    </a>
                  </div>
                )}

                {/* ORIGIN */}
                {result.metadata.osint_guess && (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10">
                    <h3 className="text-lg font-semibold mb-3">🕵️ Possible Origin</h3>
                    <p className="text-gray-300 text-sm md:text-base">{result.metadata.osint_guess}</p>
                  </div>
                )}

                {/* DOCUMENT PROPERTIES */}
                {result.metadata.properties && (
                  <div className="bg-black/30 p-4 rounded-xl border border-white/10">
                    <h3 className="text-lg font-semibold mb-3">📄 Document Properties</h3>
                    <ul className="space-y-2 text-sm md:text-base">
                      {Object.entries(result.metadata.properties).map(([k, v]) => (
                        <li key={k} className="break-all">
                          <span className="text-blue-400">{k}:</span> {String(v)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* RAW JSON VIEW */}
            {activeTab === "json" && (
              <div>
                <button
                  onClick={copyJSON}
                  className="mb-4 flex items-center gap-2 bg-gray-700 px-3 py-2 md:px-4 md:py-2 rounded-lg hover:bg-gray-600 text-xs md:text-sm w-full md:w-auto justify-center"
                >
                  <FiCopy /> Copy JSON
                </button>

                <pre className="bg-gray-900 p-3 md:p-4 rounded-xl text-green-400 text-xs md:text-sm overflow-x-auto whitespace-pre-wrap break-all max-w-full">
                  {JSON.stringify(result.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
