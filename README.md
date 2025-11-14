# STP File Viewer

A complete web-based application for viewing STP (STEP) 3D CAD files in your browser.

## Features

- 📤 **File Upload**: Easy drag-and-drop or click to upload STP/STEP files
- 🔄 **Automatic Conversion**: Converts STP files to STL format for web viewing
- 🎨 **3D Visualization**: Interactive 3D viewer with rotation, zoom, and pan controls
- 🎛️ **View Controls**: Reset view, toggle wireframe, and toggle axes
- 💻 **Modern UI**: Beautiful, responsive interface

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note:** `pythonocc-core` installation may take some time and requires:
   - Visual C++ Build Tools (on Windows)
   - CMake
   - A C++ compiler

   If you encounter issues installing `pythonocc-core`, you can try:
   ```bash
   pip install pythonocc-core --no-cache-dir
   ```

   Or use conda (recommended for pythonocc-core):
   ```bash
   conda install -c conda-forge pythonocc-core
   ```

3. **Create necessary directories:**
   The application will automatically create `uploads/` and `static/` directories on first run.

## Usage

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Upload a STP file:**
   - Click "Choose File" and select your .stp or .step file
   - Click "Upload & View"
   - The file will be converted and displayed in the 3D viewer

## Controls

- **Mouse Drag**: Rotate the 3D model
- **Mouse Wheel**: Zoom in/out
- **Right Click + Drag**: Pan the view
- **Reset View**: Reset camera to default position
- **Toggle Wireframe**: Switch between solid and wireframe view
- **Toggle Axes**: Show/hide coordinate axes

## File Size Limits

- Maximum file size: 100 MB
- Supported formats: .stp, .step

## Troubleshooting

### pythonocc-core Installation Issues

If you're having trouble installing `pythonocc-core`:

1. **Windows**: Install Visual Studio Build Tools with C++ support
2. **Linux**: Install build-essential and cmake
3. **macOS**: Install Xcode Command Line Tools

Alternatively, you can use conda which handles dependencies better:
```bash
conda create -n stp_viewer python=3.9
conda activate stp_viewer
conda install -c conda-forge pythonocc-core
pip install Flask Werkzeug
```

### Application Runs But Conversion Fails

- Make sure `pythonocc-core` is properly installed
- Check that your STP file is valid and not corrupted
- Try a different STP file to rule out file-specific issues

## Project Structure

```
stp_viewer/
├── app.py              # Flask backend application
├── templates/
│   └── index.html      # Frontend HTML with Three.js viewer
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── uploads/           # Uploaded STP files (auto-created)
└── static/            # Converted STL files (auto-created)
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **3D Processing**: pythonocc-core (OpenCASCADE)
- **Frontend**: HTML5, CSS3, JavaScript
- **3D Rendering**: Three.js
- **File Format**: STP → STL conversion

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions, please check:
- pythonocc-core documentation: https://github.com/tpaviot/pythonocc-core
- Three.js documentation: https://threejs.org/docs/

