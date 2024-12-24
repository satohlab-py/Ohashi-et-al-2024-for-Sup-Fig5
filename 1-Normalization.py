import os
import cv2
import numpy as np

def adjust_red_channel_based_on_background(folder=".", output_folder="CorrectedImages"):
    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all JPEG/JPG files in the current folder
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpeg', '.jpg'))]

    if not files:
        print("No JPEG files found in the current folder.")
        return

    # Read the first image to determine the target minimum red channel value
    # autofluorescent causes Yello signals. Thus, R-channel is the best for normalization 
    first_image_path = os.path.join(folder, files[0])
    first_image = cv2.imread(first_image_path)
    min_red = np.min(first_image[:, :, 2].astype(np.float32))  # Convert to float for safe subtraction

    for file in files:
        input_path = os.path.join(folder, file)
        image = cv2.imread(input_path)

        # Calculate the minimum red value for the current image
        current_min_red = np.min(image[:, :, 2].astype(np.float32))  # Convert to float for safe subtraction

        # Calculate the adjustment value
        adjustment_value = min_red - current_min_red

        # Apply the adjustment to all channels
        for i in range(3):  # BGR channels
            image[:, :, i] = np.clip(image[:, :, i].astype(np.float32) + adjustment_value, 0, 255).astype(np.uint8)

        # Save the corrected image to the output folder
        output_path = os.path.join(output_folder, file)
        cv2.imwrite(output_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    print(f"Corrected images saved to '{output_folder}'.")

# Execute the function
adjust_red_channel_based_on_background()
