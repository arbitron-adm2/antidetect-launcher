#!/usr/bin/env python3
"""Generate platform-specific icons from SVG source."""

import sys
from pathlib import Path

try:
    from PIL import Image
    import cairosvg
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install pillow cairosvg")
    sys.exit(1)


def generate_windows_icon(svg_path: Path, output_path: Path) -> None:
    """Generate Windows .ico file with multiple sizes."""
    # Icon sizes for Windows
    sizes = [16, 24, 32, 48, 64, 128, 256]

    # Convert SVG to PNG images at different sizes
    images = []
    for size in sizes:
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )

        # Load PNG data into PIL Image
        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        images.append(img)

    # Save as ICO with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:],
    )
    print(f"Created Windows icon: {output_path}")


def generate_macos_icon(svg_path: Path, output_path: Path) -> None:
    """Generate macOS .icns file."""
    # macOS iconset requires specific sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    # Create iconset directory
    iconset_dir = output_path.parent / f"{output_path.stem}.iconset"
    iconset_dir.mkdir(exist_ok=True)

    for size in sizes:
        # Standard resolution
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )

        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        img.save(iconset_dir / f"icon_{size}x{size}.png")

        # Retina resolution (@2x)
        if size <= 512:
            png_data_2x = cairosvg.svg2png(
                url=str(svg_path),
                output_width=size * 2,
                output_height=size * 2,
            )
            img_2x = Image.open(BytesIO(png_data_2x))
            img_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")

    # Convert iconset to icns using iconutil (macOS only)
    import subprocess
    try:
        subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)],
            check=True
        )
        print(f"Created macOS icon: {output_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: iconutil not available (macOS required for .icns generation)")
        print(f"Iconset created at: {iconset_dir}")


def generate_png_icons(svg_path: Path, output_dir: Path) -> None:
    """Generate PNG icons for Linux."""
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]

    for size in sizes:
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )

        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        output_path = output_dir / f"icon_{size}x{size}.png"
        img.save(output_path)

    print(f"Created PNG icons in: {output_dir}")


def main() -> None:
    """Main icon generation function."""
    # Paths
    project_root = Path(__file__).parent.parent
    svg_path = project_root / "src/antidetect_playwright/resources/icon.svg"
    icons_dir = project_root / "build/icons"

    # Create icons directory
    icons_dir.mkdir(parents=True, exist_ok=True)

    if not svg_path.exists():
        print(f"Error: SVG icon not found at {svg_path}")
        sys.exit(1)

    print(f"Generating icons from: {svg_path}")
    print()

    # Generate platform-specific icons
    try:
        # Windows
        print("Generating Windows icon...")
        generate_windows_icon(svg_path, icons_dir / "icon.ico")

        # macOS
        if sys.platform == "darwin":
            print("\nGenerating macOS icon...")
            generate_macos_icon(svg_path, icons_dir / "icon.icns")

        # Linux/PNG
        print("\nGenerating PNG icons...")
        generate_png_icons(svg_path, icons_dir)

        print("\n✓ All icons generated successfully!")

    except Exception as e:
        print(f"\n✗ Error generating icons: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
