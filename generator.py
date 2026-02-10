import os
from PIL import Image, ImageOps, ImageDraw

def create_composite_card(input_path, output_path, base_image_path):
    """
    Processes a square image, resizes it, applies a circular mask, 
    and pastes it onto the bottom-left of the base image.
    """
    try:
        with Image.open(base_image_path).convert("RGBA") as base_img:
            base_width, base_height = base_img.size
            profile_size = base_width // 2
            target_size = (profile_size, profile_size)

            with Image.open(input_path) as img:
                # Square validation
                width, height = img.size
                if width != height:
                    print(f"Skipping non-square image: {input_path} ({width}x{height})")
                    return

                # Convert to RGBA
                img = img.convert("RGBA")

                # Resize using LANCZOS
                img = img.resize(target_size, Image.Resampling.LANCZOS)

                # Circular Masking
                mask = Image.new("L", target_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, profile_size, profile_size), fill=255)

                # Paste onto base image (Bottom-Left)
                # Position (0, base_height - profile_size)
                paste_position = (0, base_height - profile_size)
                base_img.paste(img, paste_position, mask=mask)

                # Save to results/
                base_img.save(output_path, "PNG")
                print(f"Generated composite: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    input_folder = "images"
    output_folder = "results"
    reference_file = "card-energy-v2.png"

    # Create results folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Check if reference file exists
    if not os.path.exists(reference_file):
        print(f"Reference file {reference_file} not found. Cannot proceed.")
        return

    # Iterate through images folder
    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} not found.")
        return

    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Safe image check (extension-based)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_card.png"
            output_path = os.path.join(output_folder, output_filename)
            
            create_composite_card(input_path, output_path, reference_file)

if __name__ == "__main__":
    main()
