import React from "react";
import { ClipLoader } from "react-spinners";

export default function Spinner({ loading, text = "Loading..." }) {
  if (!loading) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.card}>
        <ClipLoader color="#000" size={48} />
        <div style={styles.text}>{text}</div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: "fixed",
    inset: 0,
    backgroundColor: "rgba(255,255,255,0.85)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
    animation: "fadeIn 0.2s ease-in-out"
  },
  card: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "14px",
    padding: "28px 32px",
    borderRadius: "14px",
    backgroundColor: "white",
    boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
  },
  text: {
    fontSize: "14px",
    color: "#444",
    fontWeight: "500"
  }
};
