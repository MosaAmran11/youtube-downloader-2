let currentFilename = "";
let progressInterval = null;

// Function to detect and adjust square thumbnails
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

function updateProgress() {
  fetch("/progress")
    .then((response) => response.json())
    .then((data) => {
      console.log("Progress data:", data); // Debug log

      if (data.status === "downloading") {
        const progressBar = document.getElementById("progressBar");
        const downloadSize = document.getElementById("downloadSize");
        const downloadSpeed = document.getElementById("downloadSpeed");

        // Remove % symbol and convert to number
        const percentage = parseFloat(data.percentage.replace("%", ""));
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = data.percentage;

        downloadSize.textContent = `${formatSize(
          data.downloaded_bytes
        )} / ${formatSize(data.total_bytes)}`;
        downloadSpeed.textContent = formatSpeed(data.speed);
      } else if (data.status === "finished") {
        clearInterval(progressInterval);
        currentFilename = data.filename;
        document.getElementById("progressContainer").style.display = "none";
        document.getElementById("fileActions").style.display = "block";
      } else if (data.status === "error") {
        clearInterval(progressInterval);
        alert("Error during download: " + data.error);
        document.getElementById("progressContainer").style.display = "none";
        document.getElementById("downloadOptions").style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error fetching progress:", error);
    });
}

document
  .getElementById("downloadForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    document.getElementById("downloadOptions").style.display = "none";
    document.getElementById("progressContainer").style.display = "block";
    document.getElementById("fileActions").style.display = "none";

    // Clear any existing interval
    if (progressInterval) {
      clearInterval(progressInterval);
    }

    fetch("/download", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "started") {
          // Start progress updates
          progressInterval = setInterval(updateProgress, 500);
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred during download");
      });
  });

document
  .getElementById("openLocationBtn")
  .addEventListener("click", function () {
    fetch(`/open_location/${encodeURIComponent(currentFilename)}`)
      .then((response) => response.json())
      .catch((error) => console.error("Error:", error));
  });

document.getElementById("openFileBtn").addEventListener("click", function () {
  fetch(`/open_file/${encodeURIComponent(currentFilename)}`)
    .then((response) => response.json())
    .catch((error) => console.error("Error:", error));
});

// Adjust thumbnail size when page loads
document.addEventListener("DOMContentLoaded", adjustThumbnailSize);
