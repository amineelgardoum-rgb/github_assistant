import React, { useState } from "react";
import LandingPage from "./components/LandingPage";
import ChatPage from "./components/ChatPage";

function App() {
  const [page, setPage] = useState("landing");
  const [repoId, setRepoId] = useState("");

  return page === "landing" ? (
    <LandingPage setRepoId={setRepoId} setPage={setPage} />
  ) : (
    <ChatPage repoId={repoId} />
  );
}

export default App;
