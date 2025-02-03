from flask import Flask, jsonify, send_file, request
from yt_dlp import YoutubeDL
import tempfile
import os

app = Flask(__name__)

def get_ydl_opts(format):
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '320'
        }],
        'ffmpeg_location': '/usr/bin/ffmpeg',  # Update based on your server setup
    }

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format')

    if not url or not format:
        return jsonify({'error': 'No URL or format provided'}), 400

    try:
        with YoutubeDL(get_ydl_opts(format)) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            base, ext = os.path.splitext(file_path)
            file_path = base + f'.{format}'
            
            return jsonify({
                'file_path': file_path,
                'title': info_dict.get('title', 'output'),
                'size': os.path.getsize(file_path) / (1024 * 1024),
                'type': format.upper()
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-file', methods=['GET'])
def download_file():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
