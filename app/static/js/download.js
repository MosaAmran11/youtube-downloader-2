// Download JavaScript - Download-specific functionality

// Download form handling
document.addEventListener("DOMContentLoaded", function () {
  const downloadForm = document.getElementById("downloadForm");
  if (downloadForm) {
    downloadForm.addEventListener("submit", handleDownload);
  }

  // File action buttons
  const openLocationBtn = document.getElementById("openLocationBtn");
  const openFileBtn = document.getElementById("openFileBtn");

  if (openLocationBtn) {
    openLocationBtn.addEventListener("click", handleOpenLocation);
  }

  if (openFileBtn) {
    openFileBtn.addEventListener("click", handleOpenFile);
  }
});

function handleDownload(e) {
  e.preventDefault();

  const formData = new FormData(this);
  const formatSelect = this.querySelector('select[name="format"]');

  if (!formatSelect.value) {
    showSnackbar("Please select a format", "warning");
    return;
  }

  // Hide download form and show progress
  document
    .getElementById("downloadForm")
    .closest(".download-form").style.display = "none";
  document.getElementById("progressSection").style.display = "block";
  document.getElementById("fileActionsSection").style.display = "none";

  // Update status
  updateStatus("downloading", "Downloading...");

  // Clear any existing interval
  if (progressInterval) {
    clearInterval(progressInterval);
  }

  // Start download
  fetch("/api/download", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "started") {
        // Start progress updates
        progressInterval = setInterval(updateProgress, 500);
        showSnackbar("Download started successfully", "success");
      } else {
        throw new Error(data.error || "Download failed to start");
      }
    })
    .catch((error) => {
      console.error("Download error:", error);
      showSnackbar(
        error.message || "An error occurred during download",
        "error"
      );

      // Show download form again
      document
        .getElementById("downloadForm")
        .closest(".download-form").style.display = "block";
      document.getElementById("progressSection").style.display = "none";
      updateStatus("error", "Download failed");
    });
}

function updateProgress() {
  fetch("/api/progress")
    .then((response) => response.json())
    .then((data) => {
      console.log("Progress data:", data);

      if (data.status === "downloading") {
        const progressBar = document.getElementById("progressBar");
        const downloadSize = document.getElementById("downloadSize");
        const downloadSpeed = document.getElementById("downloadSpeed");

        // Update progress bar
        const percentage = parseFloat(data.percentage.replace("%", ""));
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = data.percentage;

        // Update size and speed
        downloadSize.textContent = `${formatSize(
          data.downloaded_bytes
        )} / ${formatSize(data.total_bytes)}`;
        downloadSpeed.textContent = formatSpeed(data.speed);

        // Update status
        updateStatus("downloading", `Downloading... ${data.percentage}`);
      } else if (data.status === "finished") {
        clearInterval(progressInterval);
        currentFilename = data.filename;

        // Hide progress and show file actions
        document.getElementById("progressSection").style.display = "none";
        document.getElementById("fileActionsSection").style.display = "block";

        // Update status
        updateStatus("success", "Download complete");

        // Show success message
        showSnackbar("Download completed successfully!", "success");
      } else if (data.status === "error") {
        clearInterval(progressInterval);

        // Show error and restore download form
        showSnackbar(`Download error: ${data.error}`, "error");
        document
          .getElementById("downloadForm")
          .closest(".download-form").style.display = "block";
        document.getElementById("progressSection").style.display = "none";
        updateStatus("error", "Download failed");
      }
    })
    .catch((error) => {
      console.error("Error fetching progress:", error);
      // Don't show error for network issues during progress updates
    });
}

function handleOpenLocation() {
  if (!currentFilename) {
    showSnackbar("No file to open", "warning");
    return;
  }

  fetch(`/api/open_location/${encodeURIComponent(currentFilename)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        showSnackbar("File location opened", "success");
      } else {
        showSnackbar(data.error || "Failed to open file location", "error");
      }
    })
    .catch((error) => {
      console.error("Error opening location:", error);
      showSnackbar("Failed to open file location", "error");
    });
}

function handleOpenFile() {
  if (!currentFilename) {
    showSnackbar("No file to open", "warning");
    return;
  }

  fetch(`/api/open_file/${encodeURIComponent(currentFilename)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        showSnackbar("File opened successfully", "success");
      } else {
        showSnackbar(data.error || "Failed to open file", "error");
      }
    })
    .catch((error) => {
      console.error("Error opening file:", error);
      showSnackbar("Failed to open file", "error");
    });
}

// URL form handling
document.addEventListener("DOMContentLoaded", function () {
  const urlForm = document.getElementById("urlForm");
  if (urlForm) {
    urlForm.addEventListener("submit", function (e) {
      // Show loading state
      showLoading("Fetching video information...");
      updateStatus("loading", "Loading...");
    });
  }
});

// Format selection enhancement
document.addEventListener("DOMContentLoaded", function () {
  const formatSelect = document.querySelector('select[name="format"]');
  if (formatSelect) {
    formatSelect.addEventListener("change", function () {
      const selectedOption = this.options[this.selectedIndex];
      const formatType = selectedOption.dataset.type;

      // Update download button text based on format type
      const downloadBtn = document.getElementById("downloadBtn");
      if (downloadBtn) {
        if (formatType === "audio") {
          downloadBtn.innerHTML = '<i class="fas fa-music"></i> Download Audio';
        } else {
          downloadBtn.innerHTML = '<i class="fas fa-video"></i> Download Video';
        }
      }
    });
  }
});

// Auto-refresh progress when tab becomes visible
document.addEventListener("visibilitychange", function () {
  if (!document.hidden && progressInterval) {
    // Refresh progress immediately when tab becomes visible
    updateProgress();
  }
});

// Cleanup on page unload
window.addEventListener("beforeunload", function () {
  if (progressInterval) {
    clearInterval(progressInterval);
  }
});
