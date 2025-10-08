import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import HomePage from "./pages/HomePage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/rankings" element={<div className="min-h-screen bg-[#141414] flex items-center justify-center text-white text-2xl">Rankings Page - Coming Soon</div>} />
          <Route path="/contribute" element={<div className="min-h-screen bg-[#141414] flex items-center justify-center text-white text-2xl">Contribute Page - Coming Soon</div>} />
        </Routes>
        <Footer />
      </BrowserRouter>
    </div>
  );
}

export default App;