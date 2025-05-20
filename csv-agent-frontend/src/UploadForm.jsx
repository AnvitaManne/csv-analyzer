// src/UploadForm.jsx
import React, { useState } from "react";
import axios from "axios";

export default function UploadForm() {
  const [selectedFile, setSelectedFile] = useState(null); // State to hold the selected file
  const [summary, setSummary] = useState("");
  const [image, setImage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // To show loading state

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]); // Update selectedFile state
    setSummary(""); // Clear previous results
    setImage("");
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a CSV file first!");
      return;
    }

    setLoading(true); // Start loading
    setError(""); // Clear previous errors
    setSummary(""); // Clear previous summary
    setImage(""); // Clear previous image

    const formData = new FormData();
    formData.append("file", selectedFile); // Use selectedFile here

    try {
      const res = await axios.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSummary(res.data.summary);
      setImage("http://localhost:5000" + res.data.image); // Ensure correct URL for the image
    } catch (err) {
      setError("Upload failed. Please check the backend and try again.");
      console.error("Upload error:", err.response ? err.response.data : err.message);
    } finally {
      setLoading(false); // End loading
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h1>CSV Data Analyzer</h1>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }} disabled={loading}>
        {loading ? "Uploading..." : "Upload & Analyze"}
      </button>

      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

      {summary && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Data Summary:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', border: '1px solid #ccc', padding: '10px' }}>
            {summary}
          </pre>
        </div>
      )}

      {image && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Data Visualization:</h3>
          <img src={image} alt="CSV Plot" style={{ maxWidth: "100%", height: "auto", border: '1px solid #ccc' }} />
        </div>
      )}

      {loading && <p style={{ marginTop: '10px' }}>Processing data...</p>}
    </div>
  );
}