from flask import Flask, request, send_file, render_template
import os
import uuid
import ffmpeg

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def upload_page():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MP4 to MP3 Converter</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .container { max-width: 500px; margin-top: 50px; }
            .card { padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card shadow">
                <h2 class="text-center">MP4 to MP3 Converter</h2>
                <input type="file" id="fileInput" class="form-control my-3" accept="video/mp4">
                <button class="btn btn-primary w-100" onclick="uploadFile()">Convert & Download</button>
                <div id="status" class="text-center mt-3"></div>
            </div>
        </div>
        <script>
            async function uploadFile() {
                let formData = new FormData();
                let fileInput = document.getElementById("fileInput");
                let statusDiv = document.getElementById("status");
                if (fileInput.files.length === 0) {
                    statusDiv.innerHTML = "<p class='text-danger'>Please select a file!</p>";
                    return;
                }
                
                formData.append("file", fileInput.files[0]);
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
        </script>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if not file.filename.endswith('.mp4'):
        return "Invalid file format. Only MP4 allowed", 400
    
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    output_path = input_path.replace("uploads", "output").replace(".mp4", ".mp3")
    
    file.save(input_path)
    
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='mp3', audio_bitrate='192k')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return send_file(output_path, as_attachment=True)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode()
        print("FFmpeg Error:", error_message)
        return f"Conversion error: {error_message}", 500

if __name__ == '__main__':
    app.run(debug=True)
