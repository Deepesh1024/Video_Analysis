import os
import io
import ffmpeg
import tempfile

def compress_video(video_object, size_upper_bound=None, two_pass=True, filename_suffix='cps_'):
    try:
        video_object.seek(0)
    except Exception as e:
        print("Error: Provided video_object is not a valid file-like object.", e)
        return None

    # Read the entire video into memory.
    video_bytes = video_object.read()
    original_size_mb = len(video_bytes) / (1024 * 1024)
    
    # Optionally, skip compression if the file is already small.
    if original_size_mb <= 100:
        print(f'Skipping compression. Video size ({original_size_mb:.2f} MB) is already <= 100 MB.')
        video_object.seek(0)
        return video_object

    # Write the input video bytes to a temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(video_bytes)
        temp_input_path = temp_input.name

    # Create a temporary file path for the output.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
        temp_output_path = temp_output.name

    try:
        ffmpeg.input(temp_input_path).output(
            temp_output_path,
            vcodec='libx264',
            crf=0,
            preset='medium',
            acodec='copy'
        ).overwrite_output().run()

        # Read the compressed output into a BytesIO object.
        with open(temp_output_path, 'rb') as f:
            compressed_bytes = f.read()
        result = io.BytesIO(compressed_bytes)

        # Clean up temporary files.
        os.remove(temp_input_path)
        os.remove(temp_output_path)

        return result

    except Exception as e:
        print('Error during lossless compression:', e)
        try:
            os.remove(temp_input_path)
        except Exception:
            pass
        try:
            os.remove(temp_output_path)
        except Exception:
            pass
        return video_object