# Draw Geometrical shapes using OpenCV libraries
import cv2
import numpy as np

# Create a black image
img = np.ones((700, 900, 3), np.uint8) * 255

print("Choose a shape to draw:")
print("1. Line")
print("2. Rectangle")
print("3. Circle")
print("4. Ellipse")
print("5. Polygon")
print("6. Text")
print("7. Arrowed Line")

choice = input("Enter your choice (1-7): ")

if choice == '1':
    cv2.line(img, (150, 350), (750, 350), (255, 0, 0), 5)
elif choice == '2':
    cv2.rectangle(img, (250, 200), (650, 500), (0, 255, 0), 3)
elif choice == '3':
    cv2.circle(img, (450, 350), 150, (0, 0, 255), -1)
elif choice == '4':
    cv2.ellipse(img, (450, 350), (200, 100), 0, 0, 360, (255, 128, 0), -1)
elif choice == '5':
    pts = np.array([[450, 150], [650, 450], [250, 450]], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (0, 150, 150), 3)
elif choice == '6':
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'OpenCV', (280, 380), font, 3, (0, 0, 0), 3, cv2.LINE_AA)
elif choice == '7':
    cv2.arrowedLine(img, (200, 350), (700, 350), (0, 0, 0), 5, tipLength=0.1)
else:
    print("Invalid choice. Showing blank image.")

cv2.imshow('Geometrical Shapes', img)

print("\n--- Image Controls ---")
print("Press 's' to save the image")
print("Press 'c' to clear the canvas")
print("Press 'q' or ESC to exit")

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == ord('s'):
        cv2.imwrite('saved_shape.jpg', img)
        print("Image saved as 'saved_shape.jpg'")
    elif key == ord('c'):
        img = np.ones((700, 900, 3), np.uint8) * 255
        cv2.imshow('Geometrical Shapes', img)
        print("Canvas cleared")
    elif key == ord('q') or key == 27: # 27 is the ESC key
        print("Exiting...")
        break

cv2.destroyAllWindows()