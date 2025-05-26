from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# ডাউনলোড ফোল্ডার
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    # Render-এর URL ডায়নামিকভাবে পাওয়া
    base_url = request.host_url
    if request.method == "POST":
        url = request.form.get("url")
        try:
            # yt-dlp দিয়ে ভিডিও তথ্য আনা
            ydl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                # ফরম্যাট তালিকা তৈরি
                stream_list = [
                    (
                        f"{f.get('format_note', 'N/A')} - {f.get('ext', 'N/A')} "
                        f"(vcodec: {f.get('vcodec', 'N/A')}, acodec: {f.get('acodec', 'N/A')})",
                        f['format_id']
                    )
                    for f in formats
                    if f.get('ext') in ['mp4', 'webm', 'm4a', 'mp3']  # শুধু নির্দিষ্ট ফরম্যাট
                ]
                return render_template(
                    "formats.html",
                    streams=stream_list,
                    url=url,
                    title=info.get("title", "Unknown Title"),
                    base_url=base_url
                )
        except Exception as e:
            message = f"Error: {str(e)}"
    return render_template("index.html", message=message, base_url=base_url)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_id = request.form.get("format_id")
    try:
        # yt-dlp দিয়ে ফাইল ডাউনলোড
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "format": format_id,
            "noplaylist": True,
            "merge_output_format": "mp4",  # ভিডিও + অডিও মার্জ করার জন্য
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # ডাউনলোড করা ফাইলের পাথ
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{info['title']}.{info['ext']}")
            return send_file(file_path, as_attachment=True)
    except Exception as e:
        return render_template("index.html", message=f"Error: {str(e)}", base_url=request.host_url)

if __name__ == "__main__":
    app.run(debug=True)
