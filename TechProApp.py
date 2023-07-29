import cv2
import numpy as np
import tkinter as tk
import time
import csv
import os
import subprocess
import sys
from pyzbar.pyzbar import decode

def quit_app():
    os._exit(0)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

def text_display(window,text, xvalue, yvalue):
    texttile = tk.Label(window,text="{}".format(text), font=('calibre', 17, 'normal'))
    texttile.place(x=int(xvalue), y=int(yvalue))

def log_in(serial_number):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # Append the login information to the CSV file
    file_path = "C:/Users/tpsgr/Documents/logs/login_log.csv"
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([serial_number, current_time])

def scan_qr_code(video):
    quit_key = ord('q')  # Key code for 'q' key
    authenticated = False

    directory = load_directory()
    file_names = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_names.append(filename)

    while True:
        success, image = video.read()
        for barcode in decode(image):
            qr_text = barcode.data.decode('utf-8')
            file_name = str(qr_text) + ".xlsx"
            if file_name not in file_names:
                color = (0, 0, 255)
                display_message = "Denied Access"
            else:
                color = (0, 255, 0)
                display_message = "Access Granted"
                authenticated = True
            polygon_points = np.array([barcode.polygon], np.int32)
            polygon_points = polygon_points.reshape(-1, 1, 2)
            rect_points = barcode.rect
            cv2.polylines(image, [polygon_points], True, color, 3)
            cv2.putText(image, display_message, (rect_points[0], rect_points[1]), cv2.FONT_HERSHEY_PLAIN, 3, color, 2)
        
        cv2.imshow("Video", image)
        key = cv2.waitKey(1)
        if key == quit_key or authenticated:
            break

    video.release()
    cv2.destroyAllWindows()
    if authenticated:
        file_path = os.path.join(directory, file_name)
        open_file(file_path)
        cv2.destroyAllWindows()

def load_directory():
    file_path = "C:/Users/tpsgr/Documents/logs/directory.txt"
    try:
        with open(file_path, 'r') as file:
            directory = file.read().strip()
            return directory
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        return []

def open_file(file_path):
    if os.name == 'nt':  # Windows
        os.startfile(file_path)
    elif os.name == 'posix':  # macOS
        subprocess.call(['open', file_path])

def scanningjobqr():
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW if sys.platform == 'win32' else 0)
    video.set(3, 640)
    video.set(4, 740)

    scan_qr_code(video)

def homewindow():
    root = tk.Tk()
    root.title("Homepage")
    root.geometry("400x300")
    center_window(root)
    window_label = tk.Label(root, text="TechPro Login", bg='#fff', fg='blue', font=('Times', '30', 'bold italic'))
    window_label.pack()

    text_display(root, "Version 1.0.0", 290, 270)

    login_button = tk.Button(root, text="Scan Employee ID", command=scanninglogin)
    login_button.pack()
    login_button.place(x=125, y=200)

    quit_button = tk.Button(root, text="Quit", command=quit_app)
    quit_button.pack()

    root.mainloop()

def scanningjobsheet():
    def logout():
        window.destroy()

    window = tk.Toplevel()
    window.title("Homepage")
    window.geometry("500x300")
    center_window(window)

    window_label = tk.Label(window, text="Job Sheet Scanner", bg='#fff', fg='blue', font=('Times', '30', 'bold'))
    window_label.pack()

    login_button = tk.Button(window, text="Scan", command=scanningjobqr)
    login_button.pack()

    logout_button = tk.Button(window, text="Logout", command=logout)
    logout_button.pack()

    window.mainloop()

def load_authorised_employee():
    file_path = "C:/Users/tpsgr/Documents/logs/authorised_employee.txt"
    try:
        with open(file_path, 'r') as file:
            authorised_list = file.read().strip()
        return authorised_list
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        return []

def scanninglogin():

    authorised_list = load_authorised_employee()

    # Scanning QR Code from the camera feed
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW if sys.platform == 'win32' else 0)
    video.set(3, 640)
    video.set(4, 740)

    quit_key = ord('q')  # Key code for 'q' key
    authenticated = False

    while True:
        success, image = video.read()
        for barcode in decode(image):
            qr_text = barcode.data.decode('utf-8')
            qr_text = str(qr_text)
            if qr_text not in authorised_list:
                color = (0, 0, 255)
                display_message = "Wrong QR"
            else:
                color = (0, 255, 0)
                display_message = "Access Granted"
                log_in(qr_text)
                authenticated = True
                # Exit the loop after authentication

            polygon_points = np.array([barcode.polygon], np.int32)
            polygon_points = polygon_points.reshape(-1, 1, 2)
            rect_points = barcode.rect
            cv2.polylines(image, [polygon_points], True, color, 3)
            cv2.putText(image, display_message, (rect_points[0], rect_points[1]), cv2.FONT_HERSHEY_PLAIN, 3, color, 2)
        
        cv2.imshow("Video", image)
        key = cv2.waitKey(1)
        if key == quit_key or authenticated:
            break

    video.release()
    cv2.destroyAllWindows()
    if authenticated:
        scanningjobsheet()

homewindow()
