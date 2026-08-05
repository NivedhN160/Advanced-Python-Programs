import cv2

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Error: Could not open the default camera.")
    exit()

cv2.namedWindow("Color Controls")
cv2.createTrackbar("Blue", "Color Controls", 0, 255, nothing)
cv2.createTrackbar("Green", "Color Controls", 255, 255, nothing)
cv2.createTrackbar("Red", "Color Controls", 0, 255, nothing)

# Read the first frame to initialize motion comparison
ret, prev_frame = cap.read()
if not ret:
    print("Error: Failed to grab initial frame.")
    cap.release()
    exit()

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to safely grab a frame.")
        break

    # Convert current frame to grayscale and blur it
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Compute difference between current frame and previous frame
    delta_frame = cv2.absdiff(prev_gray, gray_blurred)
    thresh = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours of moving objects
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get current trackbar colors
    b = cv2.getTrackbarPos("Blue", "Color Controls")
    g = cv2.getTrackbarPos("Green", "Color Controls")
    r = cv2.getTrackbarPos("Red", "Color Controls")
    box_color = (b, g, r)

    # Loop through contours and draw bounding boxes around motion
    for c in contours:
        if cv2.contourArea(c) < 500:  # Ignore small movements
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

    # Update previous frame
    prev_gray = gray_blurred

    # Display feeds
    cv2.imshow("Default Camera - Full Feed", frame)
    cv2.imshow("Black and White Feed", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
