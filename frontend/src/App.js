import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import './App.css';

function App() {
  return (
    <main className="main">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
        </Routes>
      </BrowserRouter>
    </main>
  );
}

export default App;
