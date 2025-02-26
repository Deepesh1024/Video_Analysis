import os
import ffmpeg

def compress_video(video_full_path, size_upper_bound, two_pass=True, filename_suffix='cps_'):
    filename, _ = os.path.splitext(video_full_path)
    extension = '.mp4'
    output_file_name = filename + filename_suffix + extension

    # Minimum requirements (in bps)
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        # Check the size of the original video file
        original_size = os.path.getsize(video_full_path) / (1024 * 1024)  # Convert to MB
        if original_size <= 40:
            print(f'Skipping compression. Video size ({original_size:.2f} MB) is already <= 40 MB.')
            return video_full_path

        # Retrieve file information using ffmpeg.probe.
        probe = ffmpeg.probe(video_full_path)
        duration = float(probe['format']['duration'])

        # Retrieve the audio stream and its bitrate.
        audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        if audio_stream is None or 'bit_rate' not in audio_stream:
            raise ValueError("No audio stream or audio bitrate found in the video file.")
        audio_bitrate = float(audio_stream['bit_rate'])

        # Retrieve the video stream and its original bitrate.
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if video_stream is None or 'bit_rate' not in video_stream:
            raise ValueError("No video stream or video bitrate found in the video file.")
        original_video_bitrate = float(video_stream['bit_rate'])

        # Calculate target total bitrate (in bps) based on desired file size.
        target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print('Target bitrate is extremely low! Stop compressing.')
            return False

        # Adjust the audio bitrate if needed.
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate and target_total_bitrate > min_audio_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Compute the target video bitrate.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            print('Computed video bitrate is extremely low! Stop compressing.')
            return False

        # If the computed video bitrate is higher than the original, adjust it down.
        if original_video_bitrate and video_bitrate > original_video_bitrate:
            print("Computed video bitrate is higher than the original. Adjusting to the original bitrate.")
            video_bitrate = original_video_bitrate

        # Build the FFmpeg input.
        i = ffmpeg.input(video_full_path)
        if two_pass:
            # First pass: encode to a dummy output (discarded) for statistics.
            ffmpeg.output(i, os.devnull, **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}).overwrite_output().run()
            # Second pass: actual encoding.
            ffmpeg.output(i, output_file_name, **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}).overwrite_output().run()
        else:
            # Single-pass encoding.
            ffmpeg.output(i, output_file_name, **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}).overwrite_output().run()

        # Check if the output file meets the size target.
        output_size = os.path.getsize(output_file_name) / 1024  # Convert to KB
        if output_size <= size_upper_bound:
            return output_file_name
        elif output_size < os.path.getsize(video_full_path):  # If smaller than original, try compressing further.
            return compress_video(output_file_name, size_upper_bound, two_pass=two_pass, filename_suffix=filename_suffix)
        else:
            return False

    except FileNotFoundError as e:
        print('FFmpeg not installed or not found!', e)
        return False
    except Exception as e:
        print('Error during compression:', e)
        return False

if __name__ == '__main__':
    # Example: compressing only if video is above 40 MB, targeting 50 MB size
    file_name = compress_video('video_file', 50 * 1000)
    if file_name:
        print('Compression successful. Output file:', file_name)
    else:
        print('Compression failed.')
