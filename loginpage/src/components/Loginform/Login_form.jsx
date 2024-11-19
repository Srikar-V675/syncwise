import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios"; // Import Axios
import "./Loginform.css";

function Login() {
  const [username, setUsername] = useState(""); // Changed to username
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // For error messages
  const [loading, setLoading] = useState(false); // For loading state
  const navigate = useNavigate();

  // Check if user is already logged in
  useEffect(() => {
    if (localStorage.getItem("user")) {
      navigate("/home");
    }
  }, [navigate]);

  async function login(e) {
    e.preventDefault(); // Prevent default form submission behavior

    // Field validation
    if (!username || !password) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true); // Start loading
    setError(""); // Clear any existing error messages

    const item = { username, password }; // Use lowercase for consistency
    console.log(item)

    try {
      const response = await axios.post("http://127.0.0.1:8050/api/token/", item, {
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      // Assuming the API returns a token and user info
      localStorage.setItem("user", JSON.stringify(response.data)); // Store user data/token securely

      // Redirect to home page
      navigate("/home");
    } catch (error) {
      console.error('Login failed:', error); // Log detailed error information
      setError("Login failed. Please check your credentials."); // Display error message
    } finally {
      setLoading(false); // Stop loading
    }
  }

  return (
    <div className="wrapper">
      <form onSubmit={login}>
        <h1>Login</h1>

        <div className="input-container">
          <div className="input-box">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div className="input-box">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
        </div>

        {error && <p style={{ color: "red" }}>{error}</p>} {/* Display error */}

        <div className="remember-forget">
          <label>
            <input type="checkbox" />
            Remember me
          </label>
          <a href="#">Forgot password?</a>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}

export default Login;
