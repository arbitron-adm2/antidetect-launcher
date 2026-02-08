#!/usr/bin/env python3
"""Generate application icons from SVG for all platforms."""

import io
import sys
from pathlib import Path

try:
    from PIL import Image
    import cairosvg
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install: pip install pillow cairosvg")
    sys.exit(1)


def svg_to_png(svg_path: Path, png_path: Path, size: int):
    """Convert SVG to PNG at specified size."""
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=size,
        output_height=size,
    )
    print(f"  ✓ Generated {png_path.name} ({size}x{size})")


def generate_windows_ico(svg_path: Path, output_path: Path):
    """Generate Windows .ico file with multiple sizes."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )
        img = Image.open(io.BytesIO(png_data))
        images.append(img)
    
    # Save multi-size ICO
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"  ✓ Generated {output_path.name} (multi-size ICO)")


def generate_macos_icns(svg_path: Path, output_dir: Path):
    """Generate macOS .icns iconset (requires iconutil on macOS)."""
    import subprocess
    import shutil
    
    iconset_dir = output_dir / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)
    
    # macOS icon sizes
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    
    for size, filename in sizes:
        svg_to_png(svg_path, iconset_dir / filename, size)
    
    # Convert to .icns (only on macOS)
    if sys.platform == "darwin":
        icns_path = output_dir / "icon.icns"
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
            capture_output=True
        )
        if result.returncode == 0:
            print(f"  ✓ Generated {icns_path.name}")
            shutil.rmtree(iconset_dir)
        else:
            print(f"  ⚠ iconutil failed (macOS only). Iconset saved to {iconset_dir}")
    else:
        print(f"  ⚠ .icns generation requires macOS. Iconset saved to {iconset_dir}")


def generate_linux_icons(svg_path: Path, output_dir: Path):
    """Generate Linux icons (PNG) at standard sizes."""
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    
    for size in sizes:
        png_path = output_dir / f"icon_{size}x{size}.png"
        svg_to_png(svg_path, png_path, size)


def main():
    """Generate all platform icons."""
    project_root = Path(__file__).parent.parent
    svg_path = project_root / "src/antidetect_playwright/resources/icon.svg"
    
    if not svg_path.exists():
        print(f"ERROR: SVG icon not found: {svg_path}")
        sys.exit(1)
    
    # Create icons directory
    icons_dir = project_root / "build/icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== Generating Application Icons ===\n")
    print(f"Source: {svg_path.name}\n")
    
    # Windows
    print("Windows icons:")
    try:
        ico_path = icons_dir / "icon.ico"
        generate_windows_ico(svg_path, ico_path)
    except Exception as e:
        print(f"  ✗ Failed to generate Windows icon: {e}")
    
    # macOS
    print("\nmacOS icons:")
    try:
        generate_macos_icns(svg_path, icons_dir)
    except Exception as e:
        print(f"  ✗ Failed to generate macOS icons: {e}")
    
    # Linux
    print("\nLinux icons:")
    try:
        linux_dir = icons_dir / "linux"
        linux_dir.mkdir(exist_ok=True)
        generate_linux_icons(svg_path, linux_dir)
    except Exception as e:
        print(f"  ✗ Failed to generate Linux icons: {e}")
    
    # Copy SVG for fallback
    import shutil
    shutil.copy(svg_path, icons_dir / "icon.svg")
    print(f"\n  ✓ Copied {svg_path.name} to {icons_dir}")
    
    print("\n=== Icon generation complete! ===")
    print(f"\nIcons saved to: {icons_dir}")
    print("\nGenerated files:")
    for file in sorted(icons_dir.rglob("*")):
        if file.is_file():
            print(f"  - {file.relative_to(icons_dir)}")


if __name__ == "__main__":
    main()
