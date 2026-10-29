import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
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
      const response = await api.post("/auth/register", form);

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));

      navigate("/dashboard");
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Registration failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-shell">
        {/* Left Graphic Panel */}
        <div className="auth-visual register-visual">
          <div className="visual-glow visual-glow-one"></div>
          <div className="visual-glow visual-glow-two"></div>

          <div className="visual-content">
            <div className="brand-mark">C</div>

            <p className="visual-eyebrow">WELCOME TO CLOUDIMAGE</p>

            <h2>
              Build your
              <br />
              <span>visual workspace.</span>
            </h2>

            <p className="visual-description">
              Create your account and start managing, transforming and
              organizing your images effortlessly.
            </p>

            <div className="feature-stack">
              <div className="feature-card">
                <div className="feature-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <path d="M4 7h16v13H4z" />
                    <path d="M4 7l3-4h10l3 4" />
                    <circle cx="12" cy="13" r="3" />
                  </svg>
                </div>

                <div>
                  <strong>Upload with ease</strong>
                  <span>Keep your images organized in one place.</span>
                </div>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <path d="M4 4h16v16H4z" />
                    <path d="M8 16l3-4 2 2 3-4 3 6" />
                  </svg>
                </div>

                <div>
                  <strong>Transform instantly</strong>
                  <span>Resize, crop, rotate and optimize images.</span>
                </div>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <path d="M12 3v12" />
                    <path d="M7 10l5 5 5-5" />
                    <path d="M5 21h14" />
                  </svg>
                </div>

                <div>
                  <strong>Download anywhere</strong>
                  <span>Get your processed images whenever you need.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Register Form */}
        <div className="auth-form-section">
          <div className="auth-card register-card">
            <div className="mobile-brand">
              <div className="brand-mark">C</div>
              <span>CloudImage</span>
            </div>

            <div className="auth-heading">
              <p className="auth-kicker">GET STARTED</p>

              <h1>Create your account</h1>

              <p className="auth-subtitle">
                Start building your personal image workspace today.
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
                <label htmlFor="register-username">Username</label>

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
                    id="register-username"
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="Choose a username"
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="register-email">Email address</label>

                <div className="input-wrapper">
                  <span className="input-icon">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    >
                      <rect x="3" y="5" width="18" height="14" rx="2" />
                      <path d="m3 7 9 6 9-6" />
                    </svg>
                  </span>

                  <input
                    id="register-email"
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="register-password">Password</label>

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
                    id="register-password"
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Create a strong password"
                    autoComplete="new-password"
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

                <span className="field-hint">
                  Use a password you don't use elsewhere.
                </span>
              </div>

              <button
                type="submit"
                className="auth-submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    Creating account...
                  </>
                ) : (
                  <>
                    Create account
                    <span className="button-arrow">→</span>
                  </>
                )}
              </button>
            </form>

            <div className="auth-divider">
              <span>OR</span>
            </div>

            <p className="auth-footer">
              Already have an account?
              <Link to="/login">Sign in</Link>
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

export default Register;