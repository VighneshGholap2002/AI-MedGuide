import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import CaseForm from "./components/CaseForm";
import PatientCases from "./components/PatientCases";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/create-case" element={<CaseForm />} />
            <Route path="/patient-cases" element={<PatientCases />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
