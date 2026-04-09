import React, { useState } from "react";
import axios from "axios";
import "./styles.css";
import EmbeddingPlot from "./components/EmbeddingPlot";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("all");
  const [message, setMessage] = useState(null);
  const [queryId, setQueryId] = useState(null);
  const [view, setView] = useState("main");

  const upload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const resUpload = await axios.post(`${API_BASE}/upload`, formData);

    const newId = resUpload.data.id;

    // set as selected query
    setQueryId(newId);
    setQuery("");

    const resSearch = await axios.post(
      `${API_BASE}/search?query_id=${newId}`
    );

    setResults(resSearch.data);
    //setSelected({ id: newId, filename: file.name });

    setMessage(`Uploaded: ${file.name}`);

    setTimeout(() => setMessage(null), 2500);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  const search = async () => {
    let url = `${API_BASE}/search`;

    if (queryId) {
      url += "?query_id=" + queryId;
    } else {
      url += "?query=" + query;
    }

    const res = await axios.post(url);
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

      <div style={{ marginBottom: 10 }}>
        <button onClick={() => setView("main")}>Search</button>
        <button onClick={() => setView("viz")}>Visualisation</button>
      </div>

      {view === "main" && (
        <>

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

          {/* Search info */}
          <div className="mode">
            {queryId && selected
              ? `Searching by selected file: ${selected.filename}`
              : query
                ? `Searching by text: "${query}"`
                : "No search active"}
          </div>

          {/* Search */}
          <div className="search">
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setQueryId(null); // switch back to text mode
              }}
              placeholder="Search..."
            />
            <button onClick={async () => {
              setQueryId(null);

              const res = await axios.post(
                `${API_BASE}/search?query=${query}`
              );

              setResults(res.data);
            }}>

              Search
            </button>
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
                      onClick={async () => {
                        setSelected(r);
                        setQueryId(r.id);
                        setQuery("");

                        const res = await axios.post(
                          `${API_BASE}/search?query_id=${r.id}`
                        );

                        setResults(res.data);
                      }}
                    >
                      {r.type.includes("image") && (
                        <img
                          className="thumb"
                          src={`${API_BASE}/file/${r.id}`}
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
                        {r.text && (
                          <div
                            className="transcript"
                            title={r.text}  // 👈 tooltip with full text
                          >
                            {r.text.split(" ").slice(0, 10).join(" ")}
                            {r.text.split(" ").length > 10 && "..."}
                          </div>
                        )}

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
                      src={`${API_BASE}/file/${selected.id}`}
                    />
                  )}

                  {selected.type.includes("audio") && (
                    <audio
                      controls
                      src={`${API_BASE}/file/${selected.id}`}
                    />
                  )}

                  {selected.type.includes("pdf") && (
                    <iframe
                      src={`${API_BASE}/file/${selected.id}`}
                    />
                  )}

                  {!isSupported(selected.type) && (
                    <p>Preview not available for this file type.</p>
                  )}
                </>
              )}
            </div>
          </div>
        </>
      )}
      {view === "viz" && (
        <EmbeddingPlot
          onSelect={async (item) => {
            setSelected(item);
            setQueryId(item.id);
            setQuery("");

            const res = await axios.post(
              `${API_BASE}/search?query_id=${item.id}`
            );

            setResults(res.data);
            setView("main");
          }}
        />
      )}
    </div>
  );
}