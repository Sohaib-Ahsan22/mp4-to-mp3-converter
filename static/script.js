async function uploadFile() {
    let formData = new FormData();
    let fileInput = document.getElementById("fileInput");
    let statusDiv = document.getElementById("status");
    let videoPreview = document.getElementById("videoPreview");

    if (fileInput.files.length === 0) {
        statusDiv.innerHTML = "<p class='text-danger'>Please select a file!</p>";
        return;
    }

    let file = fileInput.files[0];
    formData.append("file", file);

    // Show video preview
    let videoURL = URL.createObjectURL(file);
    videoPreview.src = videoURL;
    videoPreview.style.display = "block";

    statusDiv.innerHTML = "<p class='text-warning'>Converting...</p>";

    let response = await fetch("/convert", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        let blob = await response.blob();
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement("a");
        a.href = url;
        a.download = "converted.mp3";
        document.body.appendChild(a);
        a.click();
        a.remove();
        statusDiv.innerHTML = "<p class='text-success'>Conversion Successful!</p>";
    } else {
        let errorMessage = await response.text();
        statusDiv.innerHTML = `<p class='text-danger'>File conversion failed: ${errorMessage}</p>`;
    }
}
