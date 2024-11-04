import { BrowserRouter, Route } from "react-router-dom";
import Login from './login.tsx';
import Dashboard from './dashboard.tsx';

function App() {

  return (
    // Todo - add validation so that the user can't access /dashboard without being signed in
      <BrowserRouter>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </BrowserRouter>
  )
}

export default App
