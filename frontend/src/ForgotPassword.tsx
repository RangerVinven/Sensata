import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function ForgotPassword() {
  const [email, setEmail] = useState<string>("");
  const [emailError, setEmailError] = useState<string>("");
  const navigate = useNavigate();

  const validateEmail = (email: string): boolean => {
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(email)) {
      setEmailError("Please enter a valid email address.");
      return false;
    }
    setEmailError("");
    return true;
  };

  const handleForgotPassword = (e: React.FormEvent) => {
    e.preventDefault();
    const isEmailValid = validateEmail(email);

    if (!isEmailValid) {
      return; // Stop form submission if validation fails
    }

    // Mock API call logic (can be replaced with actual API integration)
    console.log("Forgot password form submitted:", { email });

    // Navigate to another route upon successful submission
    navigate("/reset-password"); // Replace '/reset-password' with your desired route
  };

  return (
    <div className="login-container">
      <form onSubmit={handleForgotPassword} className="login-form">
        <h2 className="login-heading">Forgot Password</h2>
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
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default ForgotPassword;
