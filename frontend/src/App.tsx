import { ChakraProvider } from "@chakra-ui/react"
import { defaultSystem } from "@chakra-ui/react"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './login.tsx';
import Dashboard from './dashboard.tsx';
import ForgotPassword from './ForgotPassword';

function App() {

  return (
    // Todo - add validation so that the user can't access /dashboard without being signed in
    <ChakraProvider value={defaultSystem}>
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
      </ChakraProvider>
  )
}

export default App
