from flask import Flask, request, send_file
from pytube import YouTube
from io import BytesIO
import os

app = Flask(__name__)

# Server ka woh route (address) jahan se download shuru hoga
@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    
    if not video_url:
        # Agar URL nahi mila to error
        return "Error: Video URL nahi diya gaya.", 400

    try:
        # YouTube video object banao
        yt = YouTube(video_url)
        
        # Sabse achhi quality ka progressive stream (video aur audio ek saath) chuno
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not video_stream:
             # Agar progressive stream nahi mila, toh high resolution progressive stream chuno
             video_stream = yt.streams.get_highest_resolution()

        # Download ko server ki disk par save kiye bina seedha memory mein load karo
        buffer = BytesIO()
        video_stream.stream_to_buffer(buffer)
        buffer.seek(0)
        
        # File ka naam tayar karo
        filename = yt.title.replace(' ', '_').replace('/', '_') + "." + video_stream.extension
        
        # File ko user ke browser tak bhejo
        return send_file(
            buffer,
            mimetype=f'video/{video_stream.extension}',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        # Koi bhi error hone par message dikhao
        print(f"Download Error: {e}")
        return f"Download mein koi gadbadi ho gayi: {str(e)}", 500

if __name__ == '__main__':
    # Yeh development ke liye hai, production mein Render/Gunicorn isko khud manage karega

    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
