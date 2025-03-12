
#!/bin/bash
apt-get update && apt-get install -y ffmpeg
gunicorn -b 0.0.0.0:5000 app:app
