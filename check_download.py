#!/usr/bin/env python3
"""
Check UI-TARS download progress
"""

import os
import time
import sys

def get_download_size():
    """Calculate total downloaded size"""
    cache_dir = "UI-TARS-1.5-7B/.cache"
    total_size = 0
    
    if not os.path.exists(cache_dir):
        return 0, 0
    
    # Count completed files
    completed_files = 0
    
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            filepath = os.path.join(root, file)
            # Skip lock files and incomplete files
            if file.endswith('.lock') or file.endswith('.incomplete'):
                continue
            if os.path.getsize(filepath) > 1000:  # Only count real files
                total_size += os.path.getsize(filepath)
                completed_files += 1
    
    return total_size, completed_files

def main():
    print("🔍 Checking UI-TARS download progress...")
    
    total_size, completed_files = get_download_size()
    total_gb = 14  # Total model size in GB
    downloaded_gb = total_size / (1024**3)  # Convert bytes to GB
    percent = (downloaded_gb / total_gb) * 100
    
    print(f"\n📊 Download Status:")
    print(f"   Downloaded: {downloaded_gb:.2f} GB / {total_gb} GB")
    print(f"   Progress: {percent:.1f}%")
    print(f"   Completed files: {completed_files}")
    
    if percent == 0:
        print("\n⚠️  Download just starting or not yet begun")
        print("   This is normal - it takes time to start")
    elif percent < 10:
        print("\n⏳ Download in early stages")
        print("   Check back in 30 minutes")
    elif percent < 50:
        print("\n🚀 Download progressing")
        print("   Making good progress!")
    elif percent < 90:
        print("\n🎯 Download more than halfway")
        print("   Almost there!")
    else:
        print("\n🎉 Download nearly complete!")
        print("   Ready to use soon!")
    
    # Check for actual model files in the main directory
    model_files = []
    if os.path.exists("UI-TARS-1.5-7B"):
        for file in os.listdir("UI-TARS-1.5-7B"):
            if file.endswith('.safetensors'):
                model_files.append(file)
    
    if model_files:
        print(f"\n✅ Found {len(model_files)} model files in UI-TARS-1.5-7B/")
        print("   Model is being assembled")
    else:
        print("\n📁 Model files not yet in main directory")
        print("   They're still in cache, will move when complete")
    
    print("\n" + "=" * 50)
    print("Next check:")
    print(f"   Run: python {sys.argv[0]}")
    print("   Or wait and check back later")
    print("=" * 50)

if __name__ == "__main__":
    main()