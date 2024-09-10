import time
import cv2
import RPi.GPIO as GPIO

# Set up GPIO pin
GPIO_PIN = 10  # Change this to the GPIO pin you are using
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Define GPIO pins
coil_A_1_pin = 17 # GPIO pin 0
coil_A_2_pin = 18 # GPIO pin 1
coil_B_1_pin = 27 # GPIO pin 2
coil_B_2_pin = 22 # GPIO pin 3

# Define step sequence
step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

step_sequence2 = [
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0]
   
]

# Setup GPIO
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# Function to set the motor coils
def set_motor_coils(step):
    GPIO.output(coil_A_1_pin, step[0])
    GPIO.output(coil_B_1_pin, step[1])
    GPIO.output(coil_A_2_pin, step[2])
    GPIO.output(coil_B_2_pin, step[3])

# Function to rotate motor
def rotate_motor(steps, delay):
    steps = int((steps/360)*50)
    for _ in range(steps):
   
        for step in step_sequence:
            set_motor_coils(step)
            time.sleep(delay)
    time.sleep(1)
    for _ in range(steps):
       
        for step in step_sequence2:
            set_motor_coils(step)
            time.sleep(delay)



# Function to detect squares
def detect_squares(frame):
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            print("width = ",w,"height = ",h)
            if (0.9 <= aspect_ratio <= 1.1) and w>30 and w<80:
                cv2.drawContours(frame, [approx], -1, (0, 255, 0), 2)
                print("correct")
                #rotate motor
#                 time.sleep(1)
                return True

    GPIO.output(GPIO_PIN, GPIO.LOW)# Signal that no square is detected
    print("Incorrect")
    return False

# Main function
def main():
   
    cap = cv2.VideoCapture(0)
    #cap.set(cv2.CAP_PROP_FPS, 1)  # Set to 15 frames per second

   
    # Delay between frames (in seconds)
    frame_delay = 0.005
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for faster processing
        resized_frame = cv2.resize(frame, (160, 120))

        # Detect squares
        detected = detect_squares(resized_frame)
        if(detected):
            counter += 1
            if(counter == 1):
                print("Remover Enabled")
                rotate_motor(180, 0.005)
                print("Removed Biscuit")
            elif(counter>5):
                counter = 0
        else:
            counter = 0

        cv2.imshow('Square Detection', resized_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Introduce delay between frames
        time.sleep(frame_delay)

    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()


