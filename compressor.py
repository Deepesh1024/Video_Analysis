import os
import subprocess

def compress_video_target(input_path, target_size_mb, crf_min=20, crf_max=50, max_iterations=5,
                          preset='ultrafast', audio_bitrate='128k', scale='640:360'):
    """
    Compress a video by iteratively adjusting the CRF value (using binary search)
    to approach a target file size in MB.
    
    Parameters:
      input_path (str): Path to the input video file.
      target_size_mb (float): Desired target file size in MB.
      crf_min (int): Lower bound for CRF (better quality).
      crf_max (int): Upper bound for CRF (worse quality).
      max_iterations (int): Maximum iterations for adjustment.
      preset (str): ffmpeg preset for speed (default 'ultrafast').
      audio_bitrate (str): Audio bitrate (e.g., '128k').
      scale (str or None): Downscale resolution as "width:height" (e.g., "640:360"). If None, no scaling.
    
    Returns:
      str: Path to the compressed video file, or False on error.
    """
    base, _ = os.path.splitext(input_path)
    best_output = None
    best_diff = float('inf')
    current_min = crf_min
    current_max = crf_max
    best_crf = None

    for i in range(max_iterations):
        current_crf = (current_min + current_max) / 2
        output_path = f"{base}_compressed_{int(current_crf)}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-c:v', 'libx264',
            '-crf', str(current_crf),
            '-preset', preset,
            '-c:a', 'aac',
            '-b:a', audio_bitrate
        ]
        if scale is not None:
            cmd.extend(['-vf', f'scale={scale}'])
        cmd.append(output_path)
        
        print(f"Iteration {i+1}: Running ffmpeg with CRF={current_crf:.1f}...")
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            print("FFmpeg error:", e.stderr.decode())
            return False
        
        if not os.path.exists(output_path):
            print("Output file was not created.")
            return False
        
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        diff = size_mb - target_size_mb
        print(f"Iteration {i+1}: CRF={current_crf:.1f}, output size = {size_mb:.2f} MB (target {target_size_mb} MB)")
        
        if abs(diff) < best_diff:
            best_diff = abs(diff)
            best_crf = current_crf
            best_output = output_path
        
        # If within 5% tolerance, finish early.
        if abs(diff) / target_size_mb < 0.05:
            print("Target achieved within 5% tolerance.")
            return output_path
        
        if diff > 0:
            # Output is too big; increase CRF (i.e., lower quality)
            current_min = current_crf
        else:
            # Output is too small; decrease CRF (i.e., higher quality)
            current_max = current_crf

    print(f"Iteration complete. Best CRF: {best_crf:.1f}, best output file: {best_output}")
    return best_output

if __name__ == '__main__':
    file_path = '22962_SomnathThandercps_.mp4'  # Replace with your video file path.
    # Target file size: 100 MB.
    compressed = compress_video_target(file_path, target_size_mb=100, crf_min=20, crf_max=50, max_iterations=5, scale='640:360')
    if compressed:
        orig_size = os.path.getsize(file_path) / (1024 * 1024)
        comp_size = os.path.getsize(compressed) / (1024 * 1024)
        print(f"Original: {orig_size:.2f} MB, Compressed: {comp_size:.2f} MB")
    else:
        print("Compression failed.")
