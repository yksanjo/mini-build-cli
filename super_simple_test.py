#!/usr/bin/env python3
"""
Super simple test - just check if we can access the model files
"""

import os
import sys

def check_model_files():
    """Check if model files exist locally"""
    print("Checking for UI-TARS model files...")
    
    # Check the directory we already have
    model_dir = "UI-TARS-1.5-7B"
    
    if os.path.exists(model_dir):
        print(f"✓ Found model directory: {model_dir}")
        files = os.listdir(model_dir)
        print(f"  Files found: {len(files)}")
        for f in files:
            print(f"  - {f}")
        
        # Check for model weight files
        weight_files = [f for f in files if f.endswith(('.safetensors', '.bin', '.pt', '.pth'))]
        if weight_files:
            print(f"\n✓ Found model weights: {weight_files}")
            return True
        else:
            print("\n⚠️  Model directory exists but no weight files found")
            print("   Need to download the model weights")
            return False
    else:
        print(f"✗ Model directory not found: {model_dir}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = ['torch', 'transformers', 'PIL']
    missing = []
    
    for package in required:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'torch':
                import torch
                print(f"✓ PyTorch: {torch.__version__}")
            elif package == 'transformers':
                import transformers
                print(f"✓ Transformers: {transformers.__version__}")
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\n✗ Missing packages: {missing}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✓ All dependencies installed")
    return True

def main():
    print("=" * 60)
    print("UI-TARS SUPER SIMPLE CHECK")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check model files
    if not check_model_files():
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("\nYou need to download the model weights.")
        print("\nOption 1: Download manually (recommended):")
        print("1. Visit: https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B")
        print("2. Click 'Files and versions'")
        print("3. Download all .safetensors files")
        print("4. Place them in the UI-TARS-1.5-7B directory")
        
        print("\nOption 2: Use huggingface-hub:")
        print("```python")
        print("from huggingface_hub import snapshot_download")
        print("snapshot_download('ByteDance-Seed/UI-TARS-1.5-7B',")
        print("                  local_dir='UI-TARS-1.5-7B',")
        print("                  local_dir_use_symlinks=False)")
        print("```")
        
        print("\nOption 3: Use git-lfs:")
        print("```bash")
        print("git lfs install")
        print("git clone https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B")
        print("```")
        
        print("\n⚠️  Warning: Model is ~14GB")
        print("   Download may take a while!")
    
    print("\n" + "=" * 60)
    print("QUICK START ONCE MODEL IS DOWNLOADED:")
    print("=" * 60)
    print("\n1. Basic usage:")
    print("```python")
    print("from transformers import AutoProcessor, AutoModelForVision2Seq")
    print("import torch")
    print("from PIL import Image")
    print("")
    print("# Load model")
    print('model = AutoModelForVision2Seq.from_pretrained("ByteDance-Seed/UI-TARS-1.5-7B")')
    print('processor = AutoProcessor.from_pretrained("ByteDance-Seed/UI-TARS-1.5-7B")')
    print("")
    print("# Create test image")
    print('image = Image.new("RGB", (800, 600), color="blue")')
    print("")
    print("# Ask about image")
    print('response = model.generate_response(image, "What color is this?")')
    print('print(f"UI-TARS: {response}")')
    print("```")
    
    print("\n2. For GUI automation, also install:")
    print("   pip install pyautogui pynput mss opencv-python")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())