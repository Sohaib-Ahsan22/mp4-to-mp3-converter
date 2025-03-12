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
        process = (
            ffmpeg
            .input(input_path)
            .output(output_path, format='mp3', audio_bitrate='192k')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        print("FFmpeg output:", process)  # Debugging line
        return send_file(output_path, as_attachment=True)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode()
        print("FFmpeg Error:", error_message)  # Print error logs
        return f"Conversion error: {error_message}", 500
