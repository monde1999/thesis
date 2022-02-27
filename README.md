# Expected Process
1. Connect the phone to the server (through a website) to convert the phone as a web camera.
2. In real-time, the phone sends the frames captured by an RGBD camera.
3. (Optional) The server must send a message to stop the scan. This means, the phone already rotated in 360 degrees (horizontally | vertically).
4. The user must wait the result in the website unique to the phone ID.
    The website must have this process:
        a. Connecting to a device. ---> Connected
        b. Scanning. ---> Scan Complete
        c. Generating model. ---> Model Generated
    Download Options:
        a. Download Mesh (?)
        b. Download Point Cloud (PCD)
        c. Download Scans (ZIP)