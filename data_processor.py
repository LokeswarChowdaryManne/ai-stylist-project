# data_processor.py - Final version for extracting images
import h5py
import json
import numpy as np
from PIL import Image
import os
from tqdm import tqdm # For the progress bar

# Define the paths to your files
HDF5_FILE_PATH = r"FISB Dataset\Img.h5"
CROPS_JSON_PATH = r"FISB Dataset\crops.json"
OUTPUT_FOLDER = r"processed_images"

def extract_and_save_images(h5_path, crops_path, output_dir):
    """
    Reads the dataset, crops each image according to the JSON data,
    and saves them as JPEGs in the output directory.
    """
    print("Starting image extraction process...")
    
    # 1. Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        # 2. Open the data files
        h5_file = h5py.File(h5_path, 'r')
        with open(crops_path, 'r') as f:
            crops_data = json.load(f)

        # Assuming the image data is in the 'ih' key
        image_dataset = h5_file['ih']
        
        # Verify that counts match before starting
        if len(image_dataset) != len(crops_data):
            print("Error: Mismatch between image count and crop data count. Aborting.")
            return

        print(f"Found {len(image_dataset)} images to process. This may take a while.")

        # 3. Loop through all images with a progress bar
        for i in tqdm(range(len(image_dataset)), desc="Processing Images"):
            # Get the image data and crop info for the current index
            image_array = image_dataset[i]
            crop_info = crops_data[i]

            # The data is in (channels, height, width) format.
            # We need to convert it to (height, width, channels) for Pillow.
            # np.transpose changes the order of the dimensions.
            image_array = np.transpose(image_array, (1, 2, 0))
            
            # The data is in float32 format (0.0 to 1.0).
            # We need to convert it to uint8 format (0 to 255) for saving as JPEG.
            image_array = (image_array * 255).astype(np.uint8)

            # Create a Pillow Image object from the numpy array
            pil_image = Image.fromarray(image_array)

            # Get the crop coordinates
            h_from = crop_info['h_from']
            h_until = crop_info['h_until']
            w_from = crop_info['w_from']
            w_until = crop_info['w_until']
            
            # Crop the image. The box is (left, upper, right, lower).
            cropped_image = pil_image.crop((w_from, h_from, w_until, h_until))

            # Generate a filename
            output_filename = f"image_{i:06d}.jpg" # e.g., image_000000.jpg, image_000001.jpg
            output_path = os.path.join(output_dir, output_filename)

            # Save the cropped image
            cropped_image.save(output_path, "JPEG")

        print("\nProcessing complete!")
        print(f"All {len(image_dataset)} cropped images have been saved to the '{output_dir}' folder.")

    except FileNotFoundError as e:
        print(f"Error: A file was not found. Please check your paths. Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'h5_file' in locals() and h5_file:
            h5_file.close()


if __name__ == "__main__":
    extract_and_save_images(HDF5_FILE_PATH, CROPS_JSON_PATH, OUTPUT_FOLDER)