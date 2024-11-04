import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './login.tsx';
import Dashboard from './dashboard.tsx';

function App() {

  return (
    // Todo - add validation so that the user can't access /dashboard without being signed in
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
  )
}

export default App
