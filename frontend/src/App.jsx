import React, { useState } from "react";
import axios from "axios";
import "./styles.css";

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("all");
  const [message, setMessage] = useState(null);

  const upload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    await axios.post("http://localhost:8000/upload", formData);

    setMessage(`Uploaded: ${file.name}`);
    setTimeout(() => setMessage(null), 2500);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  const search = async () => {
    const res = await axios.post(
      "http://localhost:8000/search?query=" + query
    );
    setResults(res.data);
  };

  const getTypeLabel = (type) => {
    if (type.includes("image")) return "image";
    if (type.includes("audio")) return "audio";
    if (type.includes("pdf")) return "pdf";
    return "unsupported";
  };

  const isSupported = (type) =>
    type.includes("image") ||
    type.includes("audio") ||
    type.includes("pdf");

  return (
    <div className="container">
      <h2>Multimodal POC</h2>

      {/* Toast */}
      {message && <div className="toast">{message}</div>}

      {/* Upload */}
      <div
        className="dropzone"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        Drag & drop or{" "}
        <input
          type="file"
          onChange={(e) => upload(e.target.files[0])}
        />
      </div>

      {/* Search */}
      <div className="search">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search..."
        />
        <button onClick={search}>Search</button>
      </div>

      {/* Filters */}
      <div className="filters">
        {["all", "image", "audio", "pdf"].map((f) => (
          <button
            key={f}
            className={filter === f ? "active" : ""}
            onClick={() => setFilter(f)}
          >
            {f.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="layout">
        {/* Results */}
        <div className="results">
          {results
            .filter((r) => {
              if (filter === "all") return true;
              return r.type.includes(filter);
            })
            .map((r, idx) => {
              const isTop = idx === 0;

              return (
                <div
                  key={r.id}
                  className={`card ${isTop ? "top-result" : ""}`}
                  onClick={() => setSelected(r)}
                >
                  {r.type.includes("image") && (
                    <img
                      className="thumb"
                      src={`http://localhost:8000/file/${r.id}`}
                    />
                  )}

                  <div className="card-content">
                    <div className="card-header">
                      <span
                        className={`badge ${getTypeLabel(
                          r.type
                        )}`}
                      >
                        {getTypeLabel(r.type).toUpperCase()}
                      </span>

                      <span className="filename">
                        {r.filename}
                      </span>

                      {isTop && (
                        <span className="top-badge">
                          Top Result
                        </span>
                      )}
                    </div>

                    {!isSupported(r.type) && (
                      <div className="unsupported">
                        File type not supported for preview
                      </div>
                    )}

                    <div className="progress">
                      <div
                        className="bar"
                        style={{
                          width:
                            Math.min(r.score * 100, 100) + "%",
                        }}
                      />
                    </div>

                    <div className="score">
                      Score: {r.score.toFixed(3)}
                    </div>
                  </div>
                </div>
              );
            })}
        </div>

        {/* Preview */}
        <div className="preview">
          {selected && (
            <>
              <h3>{selected.filename}</h3>

              {selected.type.includes("image") && (
                <img
                  src={`http://localhost:8000/file/${selected.id}`}
                />
              )}

              {selected.type.includes("audio") && (
                <audio
                  controls
                  src={`http://localhost:8000/file/${selected.id}`}
                />
              )}

              {selected.type.includes("pdf") && (
                <iframe
                  src={`http://localhost:8000/file/${selected.id}`}
                />
              )}

              {!isSupported(selected.type) && (
                <p>Preview not available for this file type.</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}