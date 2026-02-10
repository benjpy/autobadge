import os
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw

def detect_and_crop_square(img):
    """
    Detects faces in an image and crops a square around the largest face detected.
    If no face is found, performs a center Square crop.
    """
    width, height = img.size
    
    # Square validation - skip if already square
    if width == height:
        return img

    # Convert PIL Image to OpenCV format (BGR)
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Load Haar Cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # Find the largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        
        # Calculate center of face
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Target size for square crop is the smaller dimension of the original image
        side = min(width, height)
        
        # Calculate crop bounds centered on face
        left = max(0, center_x - side // 2)
        top = max(0, center_y - side // 2)
        right = left + side
        bottom = top + side
        
        # Adjust if out of bounds
        if right > width:
            right = width
            left = right - side
        if bottom > height:
            bottom = height
            top = bottom - side
            
        print(f"Face detected! Cropping square at ({left}, {top}, {right}, {bottom})")
        return img.crop((left, top, right, bottom))
    
    else:
        # Fallback: Center Square Crop
        print("No face detected. Performing center square crop.")
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        right = left + side
        bottom = top + side
        return img.crop((left, top, right, bottom))

def create_composite_card(input_path, output_path, base_image_path):
    """
    Processes an image (detects face and crops to square if needed),
    resizes it, applies a circular mask, and pastes it onto the 
    bottom-left quadrant of the base image.
    """
    try:
        with Image.open(base_image_path).convert("RGBA") as base_img:
            base_width, base_height = base_img.size
            # 90% of half size (0.9 * 425 = 374 as defined in code)
            target_size = (374, 374)

            with Image.open(input_path).convert("RGBA") as img:
                # Face-aware Square Cropping
                img = detect_and_crop_square(img)

                # Now the image is guaranteed to be square.
                # Resize using LANCZOS
                img = img.resize(target_size, Image.Resampling.LANCZOS)

                # Circular Masking
                mask = Image.new("L", target_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, target_size[0], target_size[1]), fill=255)

                # Paste onto base image (Centered in Bottom-Left Quadrant)
                # Position (26, 451) for 374x374 on 850x850 base
                x_offset = (base_width // 2 - target_size[0]) // 2 + 1 
                y_offset = base_height // 2 + (base_height // 2 - target_size[1]) // 2 + 1 
                paste_position = (x_offset, y_offset)
                
                base_img.paste(img, paste_position, mask=mask)

                # Save to results/
                base_img.save(output_path, "PNG")
                print(f"Generated composite: {output_path} at {paste_position}")

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
