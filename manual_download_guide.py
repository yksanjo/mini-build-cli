#!/usr/bin/env python3
"""
Manual Download Guide for UI-TARS
"""

import os
import sys

def show_manual_guide():
    """Show manual download instructions"""
    print("=" * 70)
    print("📥 MANUAL DOWNLOAD GUIDE FOR UI-TARS")
    print("=" * 70)
    
    print("\n📊 CURRENT STATUS:")
    print("   • Automatic download: 3GB/14GB (21%) - STUCK")
    print("   • Recommendation: Manual download may be faster")
    
    print("\n" + "=" * 70)
    print("🎯 OPTION 1: DOWNLOAD WITH BROWSER (Easiest)")
    print("=" * 70)
    
    print("\nStep-by-step:")
    print("1. 🌐 Open browser and go to:")
    print("   https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B")
    
    print("\n2. 📁 Click 'Files and versions' tab")
    
    print("\n3. ⬇️ Download these 8 files (click each one):")
    files = [
        "model-00001-of-00007.safetensors",
        "model-00002-of-00007.safetensors", 
        "model-00003-of-00007.safetensors",
        "model-00004-of-00007.safetensors",
        "model-00005-of-00007.safetensors",
        "model-00006-of-00007.safetensors",
        "model-00007-of-00007.safetensors",
        "model.safetensors.index.json"
    ]
    
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    print("\n4. 📂 Place all downloaded files in:")
    print("   UI-TARS-1.5-7B/ directory")
    
    print("\n5. ✅ Verify you have 8 files total")
    
    print("\n" + "=" * 70)
    print("⚡ OPTION 2: DOWNLOAD WITH CURL/WGET (Faster)")
    print("=" * 70)
    
    print("\nRun these commands one by one:")
    
    base_url = "https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B/resolve/main"
    
    commands = [
        f"curl -L {base_url}/model.safetensors.index.json -o UI-TARS-1.5-7B/model.safetensors.index.json",
        f"curl -L {base_url}/model-00001-of-00007.safetensors -o UI-TARS-1.5-7B/model-00001-of-00007.safetensors",
        f"curl -L {base_url}/model-00002-of-00007.safetensors -o UI-TARS-1.5-7B/model-00002-of-00007.safetensors",
        f"curl -L {base_url}/model-00003-of-00007.safetensors -o UI-TARS-1.5-7B/model-00003-of-00007.safetensors",
        f"curl -L {base_url}/model-00004-of-00007.safetensors -o UI-TARS-1.5-7B/model-00004-of-00007.safetensors",
        f"curl -L {base_url}/model-00005-of-00007.safetensors -o UI-TARS-1.5-7B/model-00005-of-00007.safetensors",
        f"curl -L {base_url}/model-00006-of-00007.safetensors -o UI-TARS-1.5-7B/model-00006-of-00007.safetensors",
        f"curl -L {base_url}/model-00007-of-00007.safetensors -o UI-TARS-1.5-7B/model-00007-of-00007.safetensors"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. {cmd}")
    
    print("\n💡 Tip: Use a download manager for faster downloads")
    
    print("\n" + "=" * 70)
    print("🔧 OPTION 3: CONTINUE AUTOMATIC DOWNLOAD")
    print("=" * 70)
    
    print("\nIf you want to continue the automatic download:")
    print("1. Clear the stuck download:")
    print("   rm -rf UI-TARS-1.5-7B/.cache")
    
    print("\n2. Restart download:")
    print("   python download_model.py")
    
    print("\n3. Be patient - 14GB takes time")
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION AFTER DOWNLOAD")
    print("=" * 70)
    
    print("\nAfter downloading (any method), run:")
    print("python ready_when_downloaded.py")
    
    print("\nExpected output:")
    print("✅ Model appears to be downloaded!")
    print("✅ Found X model weight files")
    
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATION:")
    print("=" * 70)
    print("\nFor fastest results:")
    print("1. Use Option 1 (Browser) with a download manager")
    print("2. Download overnight if needed")
    print("3. You already have 21% - just need remaining 79%")

def check_current_files():
    """Check what files we already have"""
    print("\n📋 CURRENT FILES IN UI-TARS-1.5-7B/:")
    
    if not os.path.exists("UI-TARS-1.5-7B"):
        print("   Directory not found")
        return
    
    files = os.listdir("UI-TARS-1.5-7B")
    safetensors = [f for f in files if f.endswith('.safetensors')]
    other_files = [f for f in files if not f.endswith('.safetensors')]
    
    print(f"   • Total files: {len(files)}")
    print(f"   • Model files (.safetensors): {len(safetensors)}")
    
    if safetensors:
        print(f"   • Already have: {', '.join(safetensors[:3])}")
        if len(safetensors) > 3:
            print(f"     ... and {len(safetensors)-3} more")
    
    print(f"   • Config files: {len(other_files)}")

def main():
    show_manual_guide()
    check_current_files()
    
    print("\n" + "=" * 70)
    print("🚀 CHOOSE YOUR METHOD:")
    print("=" * 70)
    print("\n1. 🌐 Browser download (Recommended for most users)")
    print("2. ⚡ Curl commands (Faster, technical)")
    print("3. 🔄 Continue automatic (If you want to wait)")
    
    print("\n💡 You're already 21% done! Just need the remaining files.")

if __name__ == "__main__":
    main()