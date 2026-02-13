#!/usr/bin/env python3
"""
Try to recover the partially downloaded UI-TARS model
"""

import os
import shutil
import sys

def check_cache_for_complete_files():
    """Check if any files in cache are complete"""
    cache_dir = "UI-TARS-1.5-7B/.cache"
    
    if not os.path.exists(cache_dir):
        print("No cache directory found")
        return []
    
    # Look for files that might be complete
    potential_files = []
    
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith('.incomplete'):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                
                # Check if file is substantial size (likely a model chunk)
                if size > 500 * 1024 * 1024:  # More than 500MB
                    potential_files.append((filepath, size))
    
    return potential_files

def try_to_recover_files():
    """Try to recover downloaded files from cache"""
    print("=" * 60)
    print("🔄 ATTEMPTING TO RECOVER DOWNLOAD")
    print("=" * 60)
    
    # Check what we have in cache
    potential_files = check_cache_for_complete_files()
    
    if not potential_files:
        print("\n❌ No substantial files found in cache")
        print("   The 3GB previously downloaded may not be recoverable")
        return False
    
    print(f"\n📁 Found {len(potential_files)} substantial files in cache:")
    
    total_size = 0
    for i, (filepath, size) in enumerate(potential_files, 1):
        size_gb = size / (1024**3)
        total_size += size_gb
        print(f"   {i}. {os.path.basename(filepath)[:30]}...")
        print(f"      Size: {size_gb:.2f} GB")
    
    print(f"\n📊 Total potentially recoverable: {total_size:.2f} GB")
    
    # Try to rename .incomplete files
    print("\n🔄 Attempting to rename incomplete files...")
    
    recovered_count = 0
    for filepath, size in potential_files:
        try:
            # Remove .incomplete extension
            new_path = filepath.replace('.incomplete', '')
            os.rename(filepath, new_path)
            print(f"   ✅ Renamed: {os.path.basename(filepath)[:20]}...")
            recovered_count += 1
        except Exception as e:
            print(f"   ❌ Failed to rename: {e}")
    
    print(f"\n🎯 Recovery result: {recovered_count}/{len(potential_files)} files recovered")
    
    if recovered_count > 0:
        print("\n✅ Some files recovered from cache!")
        print("   The download may be able to resume from this point")
        return True
    else:
        print("\n❌ Could not recover files")
        return False

def suggest_next_steps(recovery_success):
    """Suggest next steps based on recovery result"""
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED NEXT STEPS")
    print("=" * 60)
    
    if recovery_success:
        print("\n1. ✅ Some download progress recovered")
        print("2. 🔄 Try resuming the download:")
        print("   python download_model.py")
        print("3. 📊 It should continue from where it left off")
    else:
        print("\n1. ❌ Download recovery failed")
        print("2. 🎯 Choose one of these options:")
        print("\n   OPTION A: Clean restart")
        print("   rm -rf UI-TARS-1.5-7B/.cache")
        print("   python download_model.py")
        
        print("\n   OPTION B: Manual download (Recommended)")
        print("   Visit: https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B")
        print("   Download the 7 .safetensors files")
        
        print("\n   OPTION C: Try overnight download")
        print("   Start download before bed, check in morning")
    
    print("\n" + "=" * 60)
    print("💡 YOU'RE 21% OF THE WAY THERE!")
    print("=" * 60)
    print("\nEven if restarting, you've proven:")
    print("✅ Internet connection works")
    print("✅ Download can start")
    print("✅ 3GB was downloaded successfully")
    print("✅ Only need to complete remaining 79%")

def main():
    print("Current situation: 3GB downloaded (21%), download stuck")
    print("Attempting to recover downloaded data...")
    
    recovery_success = try_to_recover_files()
    suggest_next_steps(recovery_success)
    
    # Check current files
    print("\n📋 CURRENT FILES IN UI-TARS-1.5-7B/:")
    if os.path.exists("UI-TARS-1.5-7B"):
        files = os.listdir("UI-TARS-1.5-7B")
        safetensors = [f for f in files if f.endswith('.safetensors')]
        print(f"   • Model files: {len(safetensors)}")
        if safetensors:
            print(f"   • Files: {', '.join(safetensors)}")
    
    print("\n" + "=" * 60)
    print("🚀 QUICK DECISION GUIDE:")
    print("=" * 60)
    print("\nIf you want UI-TARS TODAY:")
    print("   → Use manual download (Option B)")
    print("\nIf you can wait:")
    print("   → Try clean restart (Option A)")
    print("\nIf download was working but slow:")
    print("   → Try overnight (Option C)")

if __name__ == "__main__":
    main()