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
        <script>
            async function uploadFile() {
                let formData = new FormData();
                let fileInput = document.getElementById("fileInput");
                formData.append("file", fileInput.files[0]);
                
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
                } else {
                    alert("File conversion failed");
                }
            }
        </script>
    </head>
    <body>
        <h2>Upload MP4 to Convert to MP3</h2>
        <input type="file" id="fileInput" accept="video/mp4">
        <button onclick="uploadFile()">Convert & Download</button>
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
    
    # Convert MP4 to MP3 using ffmpeg
    ffmpeg.input(input_path).output(output_path, format='mp3').run()
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
