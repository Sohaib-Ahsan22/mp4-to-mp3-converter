from flask import Flask, request, send_file, render_template_string
import os
import uuid
import ffmpeg

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# HTML, CSS & JS in Python String
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MP4 to MP3 Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            margin-top: 50px;
        }
        #progress-container {
            display: none;
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px;
        }
        .hidden { display: none; }
        video { max-width: 100%; margin-top: 20px; }
    </style>
</head>
<body>

<div class="container">
    <h1>MP4 to MP3 Converter</h1>
    
    <input type="file" id="fileInput" accept="video/mp4">
    <button onclick="uploadFile()">Upload & Convert</button>

    <div id="progress-container">Converting... Please wait</div>

    <div id="video-preview-container" class="hidden">
        <h3>Video Preview:</h3>
        <video id="video-preview" controls></video>
    </div>

    <div id="download-container" class="hidden">
        <h3>Download MP3:</h3>
        <a id="download-link" href="" download>Download MP3</a>
    </div>
</div>

<script>
    function uploadFile() {
        let fileInput = document.getElementById("fileInput");
        if (!fileInput.files.length) {
            alert("Please select an MP4 file first.");
            return;
        }
        
        let file = fileInput.files[0];
        let formData = new FormData();
        formData.append("file", file);

        let videoPreview = document.getElementById("video-preview");
        let videoPreviewContainer = document.getElementById("video-preview-container");
        videoPreview.src = URL.createObjectURL(file);
        videoPreviewContainer.classList.remove("hidden");

        document.getElementById("progress-container").style.display = "block";
        
        fetch("/convert", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("progress-container").style.display = "none";
            if (data.success) {
                let downloadContainer = document.getElementById("download-container");
                let downloadLink = document.getElementById("download-link");
                downloadLink.href = data.download_url;
                downloadContainer.classList.remove("hidden");
            } else {
                alert("Conversion failed.");
            }
        })
        .catch(() => {
            document.getElementById("progress-container").style.display = "none";
            alert("Error during upload.");
        });
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return {"success": False, "error": "No file uploaded"}

    file = request.files['file']
    if file.filename == '':
        return {"success": False, "error": "No selected file"}

    filename = str(uuid.uuid4()) + ".mp4"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = filename.replace(".mp4", ".mp3")
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    file.save(input_path)

    # Convert MP4 to MP3 using ffmpeg
    try:
        ffmpeg.input(input_path).output(output_path, format='mp3').run(overwrite_output=True)
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"success": True, "download_url": f"/download/{output_filename}"}

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
