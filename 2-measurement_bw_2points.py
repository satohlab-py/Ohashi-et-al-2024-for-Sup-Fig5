import os
import cv2
import csv
import numpy as np

def draw_lines_and_save(folder=".", output_folder="LinedImages"):
    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all JPEG/JPG files in the current folder
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpeg', '.jpg'))]

    if not files:
        print("No JPEG files found in the current folder.")
        return

    def mouse_callback(event, x, y, flags, param):
        nonlocal points, img_copy
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            if len(points) == 2:
                # Draw line and mark points
                cv2.line(img_copy, points[0], points[1], (255, 0, 255), 2)  # Purple line
                cv2.drawMarker(img_copy, points[0], (255, 0, 255), cv2.MARKER_CROSS, 10, 2)
                cv2.drawMarker(img_copy, points[1], (255, 0, 255), cv2.MARKER_CROSS, 10, 2)
                
                # Calculate line distance
                distance = np.linalg.norm(np.array(points[0]) - np.array(points[1]))

                # Extract G-channel intensity along the line
                g_values = []
                num_points = max(abs(points[1][0] - points[0][0]), abs(points[1][1] - points[0][1])) + 1
                for t in np.linspace(0, 1, num_points):
                    x_interp = int(points[0][0] * (1 - t) + points[1][0] * t)
                    y_interp = int(points[0][1] * (1 - t) + points[1][1] * t)
                    g_value = int(img[y_interp, x_interp, 1])  # Convert to Python int
                    g_values.append(g_value)

                # Save data for current line to CSV
                csv_filename = os.path.splitext(current_file)[0] + ".csv"
                csv_path = os.path.join(output_folder, csv_filename)
                with open(csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Distance", "G Values"])
                    writer.writerow([distance, g_values])

                points = []  # Reset points for next line

    for current_file in files:
        input_path = os.path.join(folder, current_file)
        img = cv2.imread(input_path)

        # Resize image to half size for display
        img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))
        img_copy = img.copy()

        points = []  # Store two points clicked
        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", mouse_callback)

        while True:
            cv2.imshow("Image", img_copy)
            key = cv2.waitKey(1)
            if key == ord('q'):  # Quit and save
                break

        # Save the annotated image
        output_path = os.path.join(output_folder, current_file)
        cv2.imwrite(output_path, img_copy, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    cv2.destroyAllWindows()
    print(f"Annotated images and data saved to '{output_folder}'.")

# Execute the function
draw_lines_and_save()
