// src/CsvUploader.js
import React, { useState } from "react";
import axios from "axios";

function CsvUploader() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a CSV file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSummary(res.data.summary);
      setError("");
    } catch (err) {
      setError("Upload failed, try again!");
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Upload your CSV file</h2>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {summary && (
        <div style={{ marginTop: "1rem" }}>
          <h3>Summary:</h3>
          <pre>{summary}</pre>
        </div>
      )}
    </div>
  );
}

export default CsvUploader;
