import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/api";
import Navbar from "../components/Navbar";

function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [images, setImages] = useState([]);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [transforming, setTransforming] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [imageUrls, setImageUrls] = useState({});

  const [editorImage, setEditorImage] = useState(null);
  const [transformedUrl, setTransformedUrl] = useState("");
  const [transformationId, setTransformationId] = useState(null);

  const [resizeWidth, setResizeWidth] = useState("");
  const [resizeHeight, setResizeHeight] = useState("");

  const [cropWidth, setCropWidth] = useState("");
  const [cropHeight, setCropHeight] = useState("");
  const [cropX, setCropX] = useState(0);
  const [cropY, setCropY] = useState(0);

  const [rotate, setRotate] = useState(0);
  const [flip, setFlip] = useState(false);
  const [mirror, setMirror] = useState(false);

  const [grayscale, setGrayscale] = useState(false);
  const [sepia, setSepia] = useState(false);

  const [watermark, setWatermark] = useState("");
  const [format, setFormat] = useState("");
  const [quality, setQuality] = useState(85);

  // --------------------------------------------------
  // Load user
  // --------------------------------------------------

  const loadUser = async () => {
    try {
      const response = await api.get("/auth/me");
      setUser(response.data);
    } catch (err) {
      console.error("Failed to load user:", err);

      localStorage.removeItem("access_token");
      localStorage.removeItem("user");

      navigate("/login");
    }
  };

  // --------------------------------------------------
  // Load images
  // --------------------------------------------------

  const loadImages = async () => {
    try {
      const response = await api.get("/images");
      setImages(response.data.items || []);
    } catch (err) {
      console.error("Failed to load images:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load images."
      );
    }
  };

  // --------------------------------------------------
  // Load image preview
  // --------------------------------------------------

  const loadImagePreview = async (imageId) => {
    try {
      const response = await api.get(
        `/images/${imageId}/file`
      );

      setImageUrls((previous) => ({
        ...previous,
        [imageId]: response.data.url,
      }));
    } catch (err) {
      console.error(
        `Failed to load image ${imageId}:`,
        err
      );
    }
  };

  // --------------------------------------------------
  // Initial load
  // --------------------------------------------------

  useEffect(() => {
    const initializeDashboard = async () => {
      setLoading(true);

      await loadUser();
      await loadImages();

      setLoading(false);
    };

    initializeDashboard();
  }, []);

  // --------------------------------------------------
  // Load previews
  // --------------------------------------------------

  useEffect(() => {
    if (!images.length) return;

    images.forEach((image) => {
      loadImagePreview(image.id);
    });
  }, [images]);

  // --------------------------------------------------
  // Upload
  // --------------------------------------------------

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      await api.post("/images", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage("Image uploaded successfully.");

      await loadImages();
    } catch (err) {
      console.error("Upload failed:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to upload image."
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  // --------------------------------------------------
  // Delete
  // --------------------------------------------------

  const handleDelete = async (imageId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this image?"
    );

    if (!confirmed) return;

    setDeletingId(imageId);
    setMessage("");
    setError("");

    try {
      await api.delete(`/images/${imageId}`);

      setImages((previous) =>
        previous.filter(
          (image) => image.id !== imageId
        )
      );

      setImageUrls((previous) => {
        const updated = { ...previous };
        delete updated[imageId];
        return updated;
      });

      if (editorImage?.id === imageId) {
        closeEditor();
      }

      setMessage("Image deleted successfully.");
    } catch (err) {
      console.error("Delete failed:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to delete image."
      );
    } finally {
      setDeletingId(null);
    }
  };

  // --------------------------------------------------
  // Open editor
  // --------------------------------------------------

  const openEditor = (image) => {
    setEditorImage(image);

    setTransformedUrl("");
    setTransformationId(null);

    setResizeWidth("");
    setResizeHeight("");

    setCropWidth("");
    setCropHeight("");
    setCropX(0);
    setCropY(0);

    setRotate(0);
    setFlip(false);
    setMirror(false);

    setGrayscale(false);
    setSepia(false);

    setWatermark("");
    setFormat("");
    setQuality(85);

    setMessage("");
    setError("");

    setTimeout(() => {
      document
        .getElementById("image-editor")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 100);
  };

  // --------------------------------------------------
  // Close editor
  // --------------------------------------------------

  const closeEditor = () => {
    setEditorImage(null);
    setTransformedUrl("");
    setTransformationId(null);
    setTransforming(false);
  };

  // --------------------------------------------------
  // Apply transformation
  // --------------------------------------------------

  const handleTransform = async () => {
    if (!editorImage) return;

    setTransforming(true);
    setMessage("");
    setError("");
    setTransformedUrl("");
    setTransformationId(null);

    try {
      const transformation = {};

      if (resizeWidth && resizeHeight) {
        transformation.resize = {
          width: Number(resizeWidth),
          height: Number(resizeHeight),
        };
      }

      if (cropWidth && cropHeight) {
        transformation.crop = {
          width: Number(cropWidth),
          height: Number(cropHeight),
          x: Number(cropX) || 0,
          y: Number(cropY) || 0,
        };
      }

      if (Number(rotate) !== 0) {
        transformation.rotate = Number(rotate);
      }

      if (flip) {
        transformation.flip = true;
      }

      if (mirror) {
        transformation.mirror = true;
      }

      if (grayscale || sepia) {
        transformation.filter = {
          grayscale,
          sepia,
        };
      }

      if (watermark.trim()) {
        transformation.watermark =
          watermark.trim();
      }

      if (format) {
        transformation.format = format;
      }

      transformation.quality = Number(quality);

      const response = await api.post(
        `/images/${editorImage.id}/transform`,
        transformation
      );

      const newTransformationId =
        response.data.id;

      setTransformationId(newTransformationId);

      const fileResponse = await api.get(
        `/images/transformations/${newTransformationId}/file`
      );

      setTransformedUrl(
        fileResponse.data.url
      );

      setMessage(
        response.data.cached
          ? "Transformation loaded from cache."
          : "Image transformed successfully."
      );
    } catch (err) {
      console.error(
        "Transformation failed:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to transform image."
      );
    } finally {
      setTransforming(false);
    }
  };

  // --------------------------------------------------
  // Download transformed
  // --------------------------------------------------

  const handleDownloadTransformed = async () => {
    if (!transformationId) {
      setError(
        "Please apply a transformation first."
      );
      return;
    }

    try {
      setError("");

      const response = await api.get(
        `/images/transformations/${transformationId}/download`
      );

      window.location.href = response.data.url;
    } catch (err) {
      console.error(
        "Transformed download failed:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to download transformed image."
      );
    }
  };




  // --------------------------------------------------
  // Download original
  // --------------------------------------------------

  const handlePreviewOriginal = async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}/file`);
  
      const url = response.data.url;
  
      if (!url) {
        throw new Error("Preview URL not returned");
      }
  
      window.open(url, "_blank", "noopener,noreferrer");
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to open image preview."
      );
    }
  };
  
  
  const handleDownloadOriginal = async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}/download`);
  
      const url = response.data.url;
  
      if (!url) {
        throw new Error("Download URL not returned");
      }
  
      const link = document.createElement("a");
  
      link.href = url;
      link.download = response.data.filename || "image";
  
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Failed to download image."
      );
    }
  };

  // --------------------------------------------------
  // Loading
  // --------------------------------------------------

  if (loading) {
    return (
      <>
        <Navbar />

        <main className="dashboard-container">
          <div className="loading-screen">
            <div className="spinner"></div>

            <p>
              Preparing your workspace...
            </p>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <main className="dashboard-container">

        {/* Hero */}

        <section className="dashboard-hero">

          <div className="hero-content">

            <span className="eyebrow">
              YOUR IMAGE WORKSPACE
            </span>

            <h1>
              Welcome back,{" "}
              <span>
                {user?.username || "User"}
              </span>
            </h1>

            <p>
              Upload, transform and manage your
              images from one powerful workspace.
            </p>

          </div>

          <div className="hero-stat">

            <div className="hero-stat-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <rect
                  x="3"
                  y="3"
                  width="18"
                  height="18"
                  rx="3"
                />

                <circle
                  cx="8.5"
                  cy="8.5"
                  r="1.5"
                />

                <path d="m21 15-5-5L5 21" />
              </svg>
            </div>

            <div>
              <strong>
                {images.length}
              </strong>

              <span>
                {images.length === 1
                  ? "Image stored"
                  : "Images stored"}
              </span>
            </div>

          </div>

        </section>

        {/* Messages */}

        {message && (
          <div className="alert alert-success">
            <span className="alert-icon">✓</span>
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">!</span>
            <span>{error}</span>
          </div>
        )}

        {/* Upload */}

        <section className="upload-card">

          <div className="upload-visual">

            <div className="upload-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
              >
                <path d="M12 16V4" />
                <path d="m7 9 5-5 5 5" />
                <path d="M4 20h16" />
              </svg>
            </div>

          </div>

          <div className="upload-content">

            <span className="upload-label">
              ADD NEW IMAGE
            </span>

            <h2>
              Upload an image
            </h2>

            <p>
              JPG, PNG, WEBP and other supported
              image formats.
            </p>

          </div>

          <label className="primary-button upload-button">

            {uploading ? (
              <>
                <span className="button-spinner"></span>
                Uploading...
              </>
            ) : (
              <>
                Choose image
                <span>→</span>
              </>
            )}

            <input
              type="file"
              accept="image/*"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />

          </label>

        </section>

        {/* Library */}

        <section className="images-section">

          <div className="section-heading">

            <div>

              <span className="section-label">
                YOUR LIBRARY
              </span>

              <h2>
                My Images
              </h2>

            </div>

            <div className="image-count">
              {images.length}
              <span>
                {images.length === 1
                  ? " image"
                  : " images"}
              </span>
            </div>

          </div>

          {images.length === 0 ? (

            <div className="empty-state">

              <div className="empty-illustration">

                <div className="empty-image-back"></div>

                <div className="empty-image-front">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  >
                    <rect
                      x="3"
                      y="3"
                      width="18"
                      height="18"
                      rx="3"
                    />

                    <circle
                      cx="8.5"
                      cy="8.5"
                      r="1.5"
                    />

                    <path d="m21 15-5-5L5 21" />
                  </svg>
                </div>

              </div>

              <span className="empty-label">
                NO IMAGES YET
              </span>

              <h3>
                Your library is waiting
              </h3>

              <p>
                Upload your first image and start
                transforming it with CloudImage.
              </p>

            </div>

          ) : (

            <div className="image-grid">

              {images.map((image) => {

                const imageName =
                  image.original_filename ||
                  `Image ${image.id}`;

                const fileSize =
                  image.file_size
                    ? image.file_size / 1024
                    : 0;

                const fileType =
                  image.mime_type
                    ?.split("/")
                    ?.pop()
                    ?.toUpperCase() || "IMAGE";

                return (
                  <article
                    className="image-card"
                    key={image.id}
                  >

                    {/* Image */}

                    <div className="image-preview">

                      {imageUrls[image.id] ? (

                        <img
                          src={
                            imageUrls[image.id]
                          }
                          alt={imageName}
                        />

                      ) : (

                        <div className="image-loading">
                          <div className="spinner"></div>
                        </div>

                      )}

                      <div className="image-overlay">

                        <button
                          type="button"
                          className="preview-button"
                          onClick={() =>
                            openEditor(image)
                          }
                        >
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                          >
                            <path d="M12 5c5.5 0 9 7 9 7s-3.5 7-9 7-9-7-9-7 3.5-7 9-7Z" />
                            <circle
                              cx="12"
                              cy="12"
                              r="2.8"
                            />
                          </svg>

                          Preview & Edit
                        </button>

                      </div>

                      <span className="image-type-badge">
                        {fileType}
                      </span>

                    </div>

                    {/* Details */}

                    <div className="image-card-body">

                      <div className="image-title-row">

                        <h3 title={imageName}>
                          {imageName}
                        </h3>

                        <span className="image-id">
                          #{image.id}
                        </span>

                      </div>

                      <div className="image-meta">

                        <span>
                          {image.width} ×{" "}
                          {image.height}
                        </span>

                        <span className="meta-dot">
                          •
                        </span>

                        <span>
                          {fileSize.toFixed(1)} KB
                        </span>

                      </div>

                      <div className="image-actions">

                        <button
                          type="button"
                          className="action-primary"
                          onClick={() =>
                            openEditor(image)
                          }
                        >
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                          >
                            <path d="M12 20h9" />
                            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
                          </svg>

                          Edit
                        </button>

                        <button
                          type="button"
                          className="action-secondary"
                          onClick={() =>
                            handleDownloadOriginal(
                              image.id
                            )
                          }
                        >
                          <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                          >
                            <path d="M12 3v12" />
                            <path d="m7 10 5 5 5-5" />
                            <path d="M4 21h16" />
                          </svg>

                          Download
                        </button>

                        <button
                          type="button"
                          className="action-danger"
                          onClick={() =>
                            handleDelete(image.id)
                          }
                          disabled={
                            deletingId === image.id
                          }
                          title="Delete image"
                        >
                          {deletingId === image.id ? (
                            <span className="mini-spinner"></span>
                          ) : (
                            <svg
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.8"
                            >
                              <path d="M4 7h16" />
                              <path d="M10 11v6" />
                              <path d="M14 11v6" />
                              <path d="M6 7l1 14h10l1-14" />
                              <path d="M9 7V4h6v3" />
                            </svg>
                          )}
                        </button>

                      </div>

                    </div>

                  </article>
                );
              })}

            </div>
          )}

        </section>

        {/* Editor */}

        {editorImage && (

          <section
            id="image-editor"
            className="editor-card"
          >

            <div className="editor-topbar">

              <div>

                <span className="section-label">
                  IMAGE EDITOR
                </span>

                <h2>
                  Transform your image
                </h2>

                <p>
                  {editorImage.original_filename ||
                    `Image ${editorImage.id}`}
                </p>

              </div>

              <button
                type="button"
                className="close-button"
                onClick={closeEditor}
                aria-label="Close editor"
              >
                ×
              </button>

            </div>

            <div className="editor-workspace">

              {/* Preview */}

              <div className="preview-panel">

                <div className="preview-header">

                  <div>
                    <span className="preview-kicker">
                      LIVE PREVIEW
                    </span>

                    <h3>
                      Before & after
                    </h3>
                  </div>

                  {transformedUrl && (
                    <span className="ready-badge">
                      <span>✓</span>
                      Ready
                    </span>
                  )}

                </div>

                <div className="preview-images">

                  <div className="preview-box">

                    <span className="preview-label">
                      ORIGINAL
                    </span>

                    {imageUrls[editorImage.id] ? (
                      <img
                        src={
                          imageUrls[
                            editorImage.id
                          ]
                        }
                        alt="Original"
                      />
                    ) : (
                      <div className="preview-placeholder">
                        No preview
                      </div>
                    )}

                  </div>

                  <div className="preview-box">

                    <span className="preview-label">
                      TRANSFORMED
                    </span>

                    {transformedUrl ? (
                      <img
                        src={transformedUrl}
                        alt="Transformed"
                      />
                    ) : (
                      <div className="preview-placeholder">
                        <span>+</span>
                        Apply a transformation
                      </div>
                    )}

                  </div>

                </div>

                {transformedUrl && (
                  <div className="preview-actions">

                    <a
                      href={transformedUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="secondary-button"
                    >
                      Open preview
                    </a>

                    <button
                      type="button"
                      className="primary-button"
                      onClick={
                        handleDownloadTransformed
                      }
                    >
                      Download
                    </button>

                  </div>
                )}

              </div>

              {/* Controls */}

              <div className="editor-controls">

                <div className="control-group">
                  <h3>Resize</h3>

                  <div className="input-grid">

                    <input
                      type="number"
                      min="1"
                      placeholder="Width"
                      value={resizeWidth}
                      onChange={(event) =>
                        setResizeWidth(
                          event.target.value
                        )
                      }
                    />

                    <input
                      type="number"
                      min="1"
                      placeholder="Height"
                      value={resizeHeight}
                      onChange={(event) =>
                        setResizeHeight(
                          event.target.value
                        )
                      }
                    />

                  </div>
                </div>

                <div className="control-group">
                  <h3>Crop</h3>

                  <div className="input-grid">

                    <input
                      type="number"
                      min="1"
                      placeholder="Width"
                      value={cropWidth}
                      onChange={(event) =>
                        setCropWidth(
                          event.target.value
                        )
                      }
                    />

                    <input
                      type="number"
                      min="1"
                      placeholder="Height"
                      value={cropHeight}
                      onChange={(event) =>
                        setCropHeight(
                          event.target.value
                        )
                      }
                    />

                    <input
                      type="number"
                      min="0"
                      placeholder="X"
                      value={cropX}
                      onChange={(event) =>
                        setCropX(
                          event.target.value
                        )
                      }
                    />

                    <input
                      type="number"
                      min="0"
                      placeholder="Y"
                      value={cropY}
                      onChange={(event) =>
                        setCropY(
                          event.target.value
                        )
                      }
                    />

                  </div>
                </div>

                <div className="control-group">
                  <h3>Rotation</h3>

                  <input
                    type="number"
                    min="-360"
                    max="360"
                    value={rotate}
                    onChange={(event) =>
                      setRotate(
                        event.target.value
                      )
                    }
                  />
                </div>

                <div className="control-group">
                  <h3>Orientation</h3>

                  <label className="toggle-row">
                    <input
                      type="checkbox"
                      checked={flip}
                      onChange={(event) =>
                        setFlip(
                          event.target.checked
                        )
                      }
                    />

                    <span>Flip vertically</span>
                  </label>

                  <label className="toggle-row">
                    <input
                      type="checkbox"
                      checked={mirror}
                      onChange={(event) =>
                        setMirror(
                          event.target.checked
                        )
                      }
                    />

                    <span>Mirror horizontally</span>
                  </label>
                </div>

                <div className="control-group">
                  <h3>Filters</h3>

                  <label className="toggle-row">
                    <input
                      type="checkbox"
                      checked={grayscale}
                      onChange={(event) =>
                        setGrayscale(
                          event.target.checked
                        )
                      }
                    />

                    <span>Grayscale</span>
                  </label>

                  <label className="toggle-row">
                    <input
                      type="checkbox"
                      checked={sepia}
                      onChange={(event) =>
                        setSepia(
                          event.target.checked
                        )
                      }
                    />

                    <span>Sepia</span>
                  </label>
                </div>

                <div className="control-group">
                  <h3>Watermark</h3>

                  <input
                    type="text"
                    placeholder="Enter watermark text"
                    value={watermark}
                    onChange={(event) =>
                      setWatermark(
                        event.target.value
                      )
                    }
                  />
                </div>

                <div className="control-group">
                  <h3>Output format</h3>

                  <select
                    value={format}
                    onChange={(event) =>
                      setFormat(
                        event.target.value
                      )
                    }
                  >
                    <option value="">
                      Original format
                    </option>

                    <option value="JPEG">
                      JPEG
                    </option>

                    <option value="PNG">
                      PNG
                    </option>

                    <option value="WEBP">
                      WEBP
                    </option>

                    <option value="JPG">
                      JPG
                    </option>

                    <option value="GIF">
                      GIF
                    </option>
                  </select>
                </div>

                <div className="control-group">

                  <div className="quality-header">
                    <h3>Quality</h3>
                    <strong>{quality}%</strong>
                  </div>

                  <input
                    className="quality-slider"
                    type="range"
                    min="1"
                    max="100"
                    value={quality}
                    onChange={(event) =>
                      setQuality(
                        event.target.value
                      )
                    }
                  />

                </div>

                <button
                  type="button"
                  className="transform-button"
                  onClick={handleTransform}
                  disabled={transforming}
                >
                  {transforming ? (
                    <>
                      <span className="button-spinner"></span>
                      Processing image...
                    </>
                  ) : (
                    <>
                      Apply transformation
                      <span>→</span>
                    </>
                  )}
                </button>

              </div>

            </div>

          </section>

        )}

      </main>
    </>
  );
}

export default Dashboard;