import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/api";

function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", form);

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));

      navigate("/dashboard");
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-shell">
        {/* Left Graphic Panel */}
        <div className="auth-visual">
          <div className="visual-glow visual-glow-one"></div>
          <div className="visual-glow visual-glow-two"></div>

          <div className="visual-content">
            <div className="brand-mark">C</div>

            <p className="visual-eyebrow">CLOUDIMAGE</p>

            <h2>
              Your images.
              <br />
              <span>Beautifully managed.</span>
            </h2>

            <p className="visual-description">
              Upload, transform, preview and manage your images from one
              simple cloud platform.
            </p>

            <div className="visual-preview">
              <div className="preview-window-top">
                <div className="preview-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

                <div className="preview-url">cloudimage / dashboard</div>
              </div>

              <div className="preview-window-body">
                <div className="mock-sidebar">
                  <div className="mock-logo"></div>
                  <div className="mock-line active"></div>
                  <div className="mock-line"></div>
                  <div className="mock-line"></div>
                  <div className="mock-line small"></div>
                </div>

                <div className="mock-content">
                  <div className="mock-heading"></div>

                  <div className="mock-image-grid">
                    <div className="mock-image image-one">
                      <span>IMG</span>
                    </div>

                    <div className="mock-image image-two">
                      <span>IMG</span>
                    </div>

                    <div className="mock-image image-three">
                      <span>IMG</span>
                    </div>

                    <div className="mock-image image-four">
                      <span>IMG</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="visual-features">
              <div>
                <strong>01</strong>
                <span>Secure storage</span>
              </div>

              <div>
                <strong>02</strong>
                <span>Smart transformations</span>
              </div>

              <div>
                <strong>03</strong>
                <span>Fast delivery</span>
              </div>
            </div>
          </div>
        </div>

        {/* Login Form */}
        <div className="auth-form-section">
          <div className="auth-card">
            <div className="mobile-brand">
              <div className="brand-mark">C</div>
              <span>CloudImage</span>
            </div>

            <div className="auth-heading">
              <p className="auth-kicker">WELCOME BACK</p>

              <h1>Sign in to CloudImage</h1>

              <p className="auth-subtitle">
                Access your image workspace and continue creating.
              </p>
            </div>

            {error && (
              <div className="error-message">
                <span className="error-icon">!</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-field">
                <label htmlFor="login-username">Username</label>

                <div className="input-wrapper">
                  <span className="input-icon">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <path d="M20 21a8 8 0 0 0-16 0" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </span>

                  <input
                    id="login-username"
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <div className="label-row">
                  <label htmlFor="login-password">Password</label>
                </div>

                <div className="input-wrapper">
                  <span className="input-icon">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <rect x="4" y="10" width="16" height="11" rx="2" />
                      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
                    </svg>
                  </span>

                  <input
                    id="login-password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      >
                        <path d="M3 3l18 18" />
                        <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                        <path d="M9.9 4.2A10.7 10.7 0 0 1 12 4c5.5 0 9.5 4 10.8 8a12.5 12.5 0 0 1-3.1 4.8" />
                        <path d="M6.6 6.6C4.8 7.7 3.5 9.4 1.2 12c1.3 4 5.3 8 10.8 8 1.5 0 2.9-.3 4.1-.8" />
                      </svg>
                    ) : (
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      >
                        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign in
                    <span className="button-arrow">→</span>
                  </>
                )}
              </button>
            </form>

            <div className="auth-divider">
              <span>OR</span>
            </div>

            <p className="auth-footer">
              Don't have an account?
              <Link to="/register">Create an account</Link>
            </p>

            <p className="auth-security">
              <span>●</span>
              Your connection is secure
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;