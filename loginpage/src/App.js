
import './App.css';
import LoginForm from './components/Loginform/Login_form';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Loginform/Home';


function App() {
  return (
      <Router>
          <Routes>
              <Route path="/" element={<LoginForm />} />
              <Route path="/home" element={<Home />} />
          </Routes>
      </Router>
  );
}

export default App;
