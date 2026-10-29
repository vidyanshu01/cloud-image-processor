import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

function Navbar() {
  const navigate = useNavigate();
  const profileRef = useRef(null);

  const user = JSON.parse(
    localStorage.getItem("user") || "null"
  );

  const [showProfile, setShowProfile] = useState(false);
  const [showPasswordModal, setShowPasswordModal] =
    useState(false);

  const [showCurrentPassword, setShowCurrentPassword] =
    useState(false);
  const [showNewPassword, setShowNewPassword] =
    useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] =
    useState("");
  const [changingPassword, setChangingPassword] =
    useState(false);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target)
      ) {
        setShowProfile(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
    };
  }, []);

  const resetPasswordForm = () => {
    setPasswordForm({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });

    setPasswordError("");
    setPasswordSuccess("");

    setShowCurrentPassword(false);
    setShowNewPassword(false);
    setShowConfirmPassword(false);
  };

  const goHome = () => {
    setShowProfile(false);
    navigate("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setShowProfile(false);

    navigate("/login");
  };

  const openPasswordModal = () => {
    setShowProfile(false);
    resetPasswordForm();
    setShowPasswordModal(true);
  };

  const closePasswordModal = () => {
    if (changingPassword) return;

    setShowPasswordModal(false);
    resetPasswordForm();
  };

  const handlePasswordChange = (event) => {
    setPasswordForm((previous) => ({
      ...previous,
      [event.target.name]: event.target.value,
    }));

    setPasswordError("");
    setPasswordSuccess("");
  };

  const handleChangePassword = async (event) => {
    event.preventDefault();

    setPasswordError("");
    setPasswordSuccess("");

    if (!passwordForm.current_password) {
      setPasswordError(
        "Please enter your current password."
      );
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError(
        "New password must be at least 8 characters long."
      );
      return;
    }

    if (
      passwordForm.new_password !==
      passwordForm.confirm_password
    ) {
      setPasswordError(
        "New passwords do not match."
      );
      return;
    }

    if (
      passwordForm.current_password ===
      passwordForm.new_password
    ) {
      setPasswordError(
        "New password must be different from your current password."
      );
      return;
    }

    setChangingPassword(true);

    try {
      await api.post("/auth/change-password", {
        current_password:
          passwordForm.current_password,
        new_password: passwordForm.new_password,
      });

      setPasswordSuccess(
        "Password changed successfully."
      );

      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });

      setShowCurrentPassword(false);
      setShowNewPassword(false);
      setShowConfirmPassword(false);
    } catch (error) {
      console.error(error);

      setPasswordError(
        error.response?.data?.detail ||
          "Unable to change password. Please try again."
      );
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <>
      <nav className="navbar">
        {/* Brand */}
        <button
          type="button"
          className="navbar-brand-button"
          onClick={goHome}
          aria-label="Go to CloudImage dashboard"
        >
          <div className="navbar-logo">
            <span className="navbar-logo-icon">
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M7.5 19h9a4.5 4.5 0 0 0 .7-8.95A5.5 5.5 0 0 0 6.65 8.7 4.2 4.2 0 0 0 7.5 19Z"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>

            <span className="navbar-brand">
              CloudImage
            </span>
          </div>
        </button>

        <div className="navbar-right">
          {user && (
            <div
              className="profile-wrapper"
              ref={profileRef}
            >
              {/* Profile button */}
              <button
                type="button"
                className="navbar-user-button"
                onClick={() =>
                  setShowProfile((previous) => !previous)
                }
                aria-expanded={showProfile}
                aria-haspopup="menu"
              >
                <div className="navbar-avatar">
                  {user.username
                    ?.charAt(0)
                    ?.toUpperCase()}
                </div>

                <div className="navbar-user-info">
                  <span className="navbar-username">
                    {user.username}
                  </span>

                  <span className="navbar-email">
                    {user.email}
                  </span>
                </div>

                <span
                  className={`profile-arrow ${
                    showProfile
                      ? "profile-arrow-open"
                      : ""
                  }`}
                  aria-hidden="true"
                >
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="m7 10 5 5 5-5"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
              </button>

              {/* Profile dropdown */}
              {showProfile && (
                <div
                  className="profile-dropdown"
                  role="menu"
                >
                  <div className="profile-dropdown-header">
                    <div className="profile-large-avatar">
                      {user.username
                        ?.charAt(0)
                        ?.toUpperCase()}
                    </div>

                    <div className="profile-dropdown-user">
                      <strong>{user.username}</strong>
                      <span>{user.email}</span>
                    </div>
                  </div>

                  <div className="profile-divider" />

                  <button
                    type="button"
                    className="profile-menu-item"
                    onClick={openPasswordModal}
                    role="menuitem"
                  >
                    <span
                      className="profile-menu-icon"
                      aria-hidden="true"
                    >
                      <svg viewBox="0 0 24 24">
                        <rect
                          x="5"
                          y="10"
                          width="14"
                          height="10"
                          rx="2"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                        />

                        <path
                          d="M8 10V7a4 4 0 0 1 8 0v3"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                        />
                      </svg>
                    </span>

                    <span>
                      <strong>Change Password</strong>
                      <small>
                        Update your account password
                      </small>
                    </span>
                  </button>

                  <button
                    type="button"
                    className="profile-menu-item logout-menu-item"
                    onClick={logout}
                    role="menuitem"
                  >
                    <span
                      className="profile-menu-icon"
                      aria-hidden="true"
                    >
                      <svg viewBox="0 0 24 24">
                        <path
                          d="M10 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                        />

                        <path
                          d="M13 8l4 4-4 4M17 12H9"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </span>

                    <span>
                      <strong>Logout</strong>
                      <small>
                        Sign out of your account
                      </small>
                    </span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* Change Password Modal */}
      {showPasswordModal && (
        <div
          className="password-modal-overlay"
          onClick={closePasswordModal}
        >
          <div
            className="password-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="password-modal-header">
              <div>
                <span
                  className="password-modal-icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 24 24">
                    <rect
                      x="5"
                      y="10"
                      width="14"
                      height="10"
                      rx="2"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    />

                    <path
                      d="M8 10V7a4 4 0 0 1 8 0v3"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>

                <h2>Change Password</h2>

                <p>
                  Keep your CloudImage account secure.
                </p>
              </div>

              <button
                type="button"
                className="password-modal-close"
                onClick={closePasswordModal}
                disabled={changingPassword}
                aria-label="Close password dialog"
              >
                ×
              </button>
            </div>

            {passwordError && (
              <div
                className="password-alert password-alert-error"
                role="alert"
              >
                {passwordError}
              </div>
            )}

            {passwordSuccess && (
              <div
                className="password-alert password-alert-success"
                role="status"
              >
                {passwordSuccess}
              </div>
            )}

            <form onSubmit={handleChangePassword}>
              {/* Current Password */}
              <label htmlFor="current_password">
                Current Password
              </label>

              <div className="password-input-wrapper">
                <input
                  id="current_password"
                  type={
                    showCurrentPassword
                      ? "text"
                      : "password"
                  }
                  name="current_password"
                  value={
                    passwordForm.current_password
                  }
                  onChange={handlePasswordChange}
                  placeholder="Enter current password"
                  required
                  autoComplete="current-password"
                />

                <button
                  type="button"
                  className="password-eye-button"
                  onClick={() =>
                    setShowCurrentPassword(
                      (previous) => !previous
                    )
                  }
                  aria-label={
                    showCurrentPassword
                      ? "Hide current password"
                      : "Show current password"
                  }
                >
                  {showCurrentPassword ? (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 6.2A10.8 10.8 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-3.1 3.7M6.2 6.8C3.5 8.6 2 12 2 12s3.5 6 10 6c1.1 0 2.1-.2 3-.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </button>
              </div>

              {/* New Password */}
              <label htmlFor="new_password">
                New Password
              </label>

              <div className="password-input-wrapper">
                <input
                  id="new_password"
                  type={
                    showNewPassword
                      ? "text"
                      : "password"
                  }
                  name="new_password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                  placeholder="Enter new password"
                  required
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="password-eye-button"
                  onClick={() =>
                    setShowNewPassword(
                      (previous) => !previous
                    )
                  }
                  aria-label={
                    showNewPassword
                      ? "Hide new password"
                      : "Show new password"
                  }
                >
                  {showNewPassword ? (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 6.2A10.8 10.8 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-3.1 3.7M6.2 6.8C3.5 8.6 2 12 2 12s3.5 6 10 6c1.1 0 2.1-.2 3-.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </button>
              </div>

              <p className="password-hint">
                Use at least 8 characters.
              </p>

              {/* Confirm Password */}
              <label htmlFor="confirm_password">
                Confirm New Password
              </label>

              <div className="password-input-wrapper">
                <input
                  id="confirm_password"
                  type={
                    showConfirmPassword
                      ? "text"
                      : "password"
                  }
                  name="confirm_password"
                  value={
                    passwordForm.confirm_password
                  }
                  onChange={handlePasswordChange}
                  placeholder="Confirm new password"
                  required
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="password-eye-button"
                  onClick={() =>
                    setShowConfirmPassword(
                      (previous) => !previous
                    )
                  }
                  aria-label={
                    showConfirmPassword
                      ? "Hide confirmation password"
                      : "Show confirmation password"
                  }
                >
                  {showConfirmPassword ? (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24">
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 6.2A10.8 10.8 0 0 1 12 6c6.5 0 10 6 10 6a18 18 0 0 1-3.1 3.7M6.2 6.8C3.5 8.6 2 12 2 12s3.5 6 10 6c1.1 0 2.1-.2 3-.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </button>
              </div>

              {/* Actions */}
              <div className="password-modal-actions">
                <button
                  type="button"
                  className="password-cancel-button"
                  onClick={closePasswordModal}
                  disabled={changingPassword}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="password-save-button"
                  disabled={changingPassword}
                >
                  {changingPassword ? (
                    <>
                      <span className="button-spinner" />
                      Changing...
                    </>
                  ) : (
                    "Change Password"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default Navbar;