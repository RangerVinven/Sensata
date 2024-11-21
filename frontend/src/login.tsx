import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [emailError, setEmailError] = useState<string>("");
  const [passwordError, setPasswordError] = useState<string>("");
  const [invalidCredentials, setInvalidCredentials] = useState<string>("");

  const [time, setTime] = useState<string>(
    new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
  );
  const navigate = useNavigate();

  useEffect(() => {
    const timerId = setInterval(() => {
      setTime(
        new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
      );
    }, 1000);

    return () => clearInterval(timerId);
  }, []);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(email)) {
      setEmailError("Please enter a valid email address.");
      return false;
    }
    setEmailError("");
    return true;
  };

  const validatePassword = (password: string): boolean => {
    if (password.length < 6) {
      setPasswordError("Password must be at least 6 characters long.");
      return false;
    }
    setPasswordError("");
    return true;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    setInvalidCredentials("Invalid credentials");

    if (!isEmailValid || !isPasswordValid) {
      return; // Stop form submission if validation fails
    }

    // Sends the login request
    const response = await fetch("https://idp_api.arfff.dog/api/v1/login", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    });

    // Checks if the reponse was successful
    if (!response.ok) {
      setInvalidCredentials("Invalid credentials");
    } else {
      navigate("/dashboard");
    }

    // Navigate to another route upon successful login
  };

  const handleForgotPassword = () => {
    navigate("/forgot-password");
  };

  return (
    <div className="login-container">
      <form onSubmit={handleLogin} className="login-form">
        <h2 className="login-heading">Login to Sensata</h2>
        <div className="digital-clock">
          <div className="time-display">{time}</div>
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => validateEmail(email)}
            required
          />
          {emailError && <p className="error-message">{emailError}</p>}
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => validatePassword(password)}
            required
          />
          {passwordError && <p className="error-message">{passwordError}</p>}
        </div>
        <button type="submit">Login</button>
        {invalidCredentials && (
          <p className="error-message">{invalidCredentials}</p>
        )}
        <p className="forgot-password" onClick={handleForgotPassword}>
          Forgot password?
        </p>
      </form>
    </div>
  );
}

export default Login;
