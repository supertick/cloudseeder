import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import AudioRecorder from './Recorder';
import Home from './pages/Home';
import About from './pages/About';

function App() {
  return (
    <Router>
      <nav>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/about">About</Link></li>
          <li><Link to="/recorder">Audio Recorder</Link></li>
        </ul>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/recorder" element={<AudioRecorder />} />
      </Routes>
    </Router>
  );
}

export default App;
