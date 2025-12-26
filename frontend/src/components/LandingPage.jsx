import React, { useState } from "react";
import Spinner from "./Spinner";
import { loadRepo } from "../job/api";
import "../style/landingpage.css"

export default function LandingPage({ setRepoId, setPage }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!repoUrl) return;
    setLoading(true);

    try {
      const data = await loadRepo(repoUrl);
      setRepoId(data.repo_id);
      setPage("chat"); // switch to chat page
    } catch (err) {
      console.error(err);
      alert("Failed to load repo");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spinner loading={true} />;

  return (
    <div className="landing-container">
      <form className="landing-form" onSubmit={handleSubmit}>
        <input 
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Enter GitHub repo URL"
          className="repo-input"
        />
        <button 
          type="submit" 
          className="load-btn"
          disabled={!repoUrl.trim()}
        >
          Load Repo
        </button>
      </form>
    </div>
  );
}
