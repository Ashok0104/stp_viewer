from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import datetime
from werkzeug.utils import secure_filename
import sys

# Try OCP first (cadquery-ocp - works on Windows)
try:
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    HAS_OCC = True
    OCC_TYPE = 'OCP'
except ImportError:
    # Fallback to pythonocc-core (OCC)
    try:
        from OCC.Core.STEPControl_Reader import STEPControl_Reader
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
        from OCC.Core.StlAPI import StlAPI_Writer
        HAS_OCC = True
        OCC_TYPE = 'OCC'
    except ImportError:
        HAS_OCC = False
        OCC_TYPE = None
        print("Warning: Neither OCP (cadquery-ocp) nor pythonocc-core is available.")
        print("Install cadquery-ocp for Windows: pip install cadquery-ocp")
        print("Or install pythonocc-core for Linux/Mac: conda install -c conda-forge pythonocc-core")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'stp', 'step'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_stp_to_stl(stp_path, stl_path):
    """Convert STP file to STL format using OCP (cadquery-ocp) or pythonocc-core"""
    if not HAS_OCC:
        raise ImportError("OCP (cadquery-ocp) or pythonocc-core is required for STP file conversion")
    
    # Read STEP file
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(stp_path)
    
    if status != IFSelect_RetDone:
        raise ValueError(f"Error reading STEP file. Status: {status}")
    
    # Transfer all roots
    step_reader.TransferRoots()
    
    # Get the shape
    shape = step_reader.OneShape()
    
    if shape.IsNull():
        raise ValueError("No shape found in STEP file")
    
    # Mesh the shape for STL export
    mesh = BRepMesh_IncrementalMesh(shape, 0.1, True)
    mesh.Perform()
    
    # Write STL file
    stl_writer = StlAPI_Writer()
    # OCP uses property, OCC uses method
    if OCC_TYPE == 'OCP':
        stl_writer.ASCIIMode = False  # Binary mode for OCP
    else:
        stl_writer.SetASCIIMode(False)  # Binary mode for OCC
    success = stl_writer.Write(shape, stl_path)
    
    if not success:
        raise ValueError("Failed to write STL file")
    
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload .stp or .step files'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        stp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(stp_path)
        
        # Convert STP to STL
        stl_filename = filename.rsplit('.', 1)[0] + '.stl'
        stl_path = os.path.join('static', stl_filename)
        
        if HAS_OCC:
            convert_stp_to_stl(stp_path, stl_path)
            return jsonify({
                'success': True,
                'stl_file': f'/static/{stl_filename}',
                'filename': filename,
                'message': 'File uploaded and converted successfully'
            })
        else:
            # Fallback: return the STP file path (client-side will need to handle it)
            return jsonify({
                'success': True,
                'stp_file': f'/uploads/{filename}',
                'message': 'File uploaded. Note: pythonocc-core not installed. Install it for STP conversion.',
                'needs_conversion': True
            })
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/static/<filename>')
def static_file(filename):
    return send_file(os.path.join('static', filename))

@app.route('/api/recent-uploads', methods=['GET'])
def get_recent_uploads():
    """Get list of recent uploads from uploads folder"""
    try:
        uploads_dir = app.config['UPLOAD_FOLDER']
        static_dir = 'static'
        
        if not os.path.exists(uploads_dir):
            return jsonify({'files': []})
        
        # Get all STP/STEP files from uploads folder
        files = []
        for filename in os.listdir(uploads_dir):
            if allowed_file(filename):
                file_path = os.path.join(uploads_dir, filename)
                # Get file modification time
                mtime = os.path.getmtime(file_path)
                
                # Check if corresponding STL exists
                stl_filename = filename.rsplit('.', 1)[0] + '.stl'
                stl_path = os.path.join(static_dir, stl_filename)
                stl_file = f'/static/{stl_filename}' if os.path.exists(stl_path) else None
                
                files.append({
                    'filename': filename,
                    'stl_file': stl_file,
                    'date': mtime,
                    'size': os.path.getsize(file_path)
                })
        
        # Sort by modification time (newest first) and take last 4
        files.sort(key=lambda x: x['date'], reverse=True)
        files = files[:4]
        
        # Convert timestamp to ISO format
        for file_info in files:
            file_info['date'] = datetime.datetime.fromtimestamp(file_info['date']).isoformat()
        
        return jsonify({'files': files})
    
    except Exception as e:
        return jsonify({'error': str(e), 'files': []}), 500

if __name__ == '__main__':
    if not HAS_OCC:
        print("\n" + "="*60)
        print("WARNING: OCP (cadquery-ocp) or pythonocc-core is not installed!")
        print("The application will run but STP file conversion won't work.")
        print("To install on Windows, run:")
        print("  pip install cadquery-ocp")
        print("To install on Linux/Mac, run:")
        print("  conda install -c conda-forge pythonocc-core")
        print("="*60 + "\n")
    else:
        print(f"\n✓ STP conversion enabled using {OCC_TYPE}\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

