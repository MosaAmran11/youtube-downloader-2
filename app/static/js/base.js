// Base JavaScript - Common UI functionality

// Global variables
let currentFilename = "";
let progressInterval = null;

// Utility functions
function formatSize(bytes) {
  if (bytes === 0) return "0B";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)}${units[unitIndex]}`;
}

function formatSpeed(bytesPerSecond) {
  return `${formatSize(bytesPerSecond)}/s`;
}

// Loading overlay functions
function showLoading(message = "Processing...") {
  const overlay = document.getElementById("loading-overlay");
  const text = overlay.querySelector(".loading-text");
  text.textContent = message;
  overlay.style.display = "flex";
}

function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  overlay.style.display = "none";
}

// Status indicator functions
function updateStatus(status, text) {
  const statusDot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");

  if (statusDot && statusText) {
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
  }
}

// Clipboard functions
function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        showSnackbar("Copied to clipboard!", "success");
      })
      .catch(() => {
        fallbackCopyToClipboard(text);
      });
  } else {
    fallbackCopyToClipboard(text);
  }
}

function fallbackCopyToClipboard(text) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  textArea.style.top = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    document.execCommand("copy");
    showSnackbar("Copied to clipboard!", "success");
  } catch (err) {
    showSnackbar("Failed to copy to clipboard", "error");
  }

  document.body.removeChild(textArea);
}

// Share functions
function shareVideo() {
  if (navigator.share) {
    navigator
      .share({
        title: "YouTube Downloader",
        text: "Check out this YouTube video!",
        url: window.location.href,
      })
      .catch(() => {
        showSnackbar("Sharing not supported", "info");
      });
  } else {
    copyToClipboard(window.location.href);
  }
}

// Format info functions
function showFormatInfo() {
  showSnackbar("Format information coming soon!", "info");
}

// Thumbnail size adjustment
function adjustThumbnailSize() {
  const thumbnail = document.querySelector(".video-thumbnail");
  if (thumbnail) {
    thumbnail.onload = function () {
      const wrapper = this.closest(".thumbnail-wrapper");
      if (this.naturalWidth && this.naturalHeight) {
        const aspectRatio = this.naturalWidth / this.naturalHeight;
        // If aspect ratio is close to 1:1 (square), make it smaller
        if (Math.abs(aspectRatio - 1) < 0.1) {
          wrapper.classList.add("square");
        }
      }
    };
    // Trigger onload if image is already loaded
    if (thumbnail.complete) {
      thumbnail.onload();
    }
  }
}

// Initialize base functionality
document.addEventListener("DOMContentLoaded", function () {
  // Adjust thumbnail sizes
  adjustThumbnailSize();

  // Set initial status
  updateStatus("ready", "Ready");

  // Add form submission loading
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", function () {
      showLoading("Processing request...");

      // Auto-hide loading after 10 seconds (fallback)
      setTimeout(() => {
        hideLoading();
      }, 10000);
    });
  });
});

// Error handling
window.addEventListener("error", function (e) {
  console.error("JavaScript error:", e.error);
  showSnackbar("An error occurred. Please try again.", "error");
});

// Network status
window.addEventListener("online", function () {
  updateStatus("ready", "Online");
  showSnackbar("Connection restored", "success");
});

window.addEventListener("offline", function () {
  updateStatus("error", "Offline");
  showSnackbar("No internet connection", "warning");
});
