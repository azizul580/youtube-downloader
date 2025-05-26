from flask import Flask, render_template, request, send_file, request
from pytube import YouTube
import os

app = Flask(__name__)

# ডাউনলোড ফোল্ডার
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    # Render-এর URL বা লোকাল URL ডায়নামিকভাবে পাওয়া
    base_url = request.host_url
    if request.method == "POST":
        url = request.form.get("url")
        try:
            yt = YouTube(url)
            # সকল উপলব্ধ স্ট্রিম তালিকাভুক্ত করা
            streams = yt.streams.filter(progressive=True)  # শুধু প্রোগ্রেসিভ স্ট্রিম (ভিডিও + অডিও)
            audio_streams = yt.streams.filter(only_audio=True)  # শুধু অডিও স্ট্রিম
            stream_list = [(str(stream), stream.itag) for stream in streams] + [(str(stream), stream.itag) for stream in audio_streams]
            return render_template("formats.html", streams=stream_list, url=url, title=yt.title, base_url=base_url)
        except Exception as e:
            message = f"Error: {str(e)}"
    return render_template("index.html", message=message, base_url=base_url)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    itag = request.form.get("itag")
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        file_path = stream.download(output_path=DOWNLOAD_FOLDER)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return render_template("index.html", message=f"Error: {str(e)}", base_url=request.host_url)

if __name__ == "__main__":
    app.run(debug=True)