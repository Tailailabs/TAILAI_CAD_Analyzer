import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from openai import OpenAI
from collections import defaultdict
import os
import io
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image
from gradio_client import Client, handle_file
import fitz # PyMuPDF for PDF handling
from dotenv import load_dotenv # <--- ADD THIS LINE

# --- Configuration and Initialization ---

# Load environment variables from .env file
load_dotenv() # <--- ADD THIS LINE

# Set Streamlit page configuration
st.set_page_config(
    page_title="TAILAI CAD & Vectorization Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables */
    :root {
        --primary-color: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-light: #3b82f6;
        --secondary-color: #10b981;
        --accent-color: #f59e0b;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --success-color: #10b981;
        --info-color: #3b82f6;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-accent: #f1f5f9;
        --border-color: #e2e8f0;
        --border-light: #f1f5f9;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --gradient-primary: linear-gradient(135deg, #4B0082 0%, #800080 100%);
        --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Container */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main Content Area */
    # .main .block-container {
    #     background: var(--bg-primary);
    #     border-radius: 20px;
    #     padding: 2rem;
    #     margin: 1rem;
    #     box-shadow: var(--shadow-xl);
    #     max-width: 1200px;
    #     margin-left: auto;
    #     margin-right: auto;
    # }
            
            
    /* General Styling */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit default header/footer */
    #MainMenu, footer, header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
    padding: 0;
}

            .section-header, .sub-header, p {
    color: #333 !important;
}

            .section-header {
    color: #fff;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
}


    /* Container */
    .main .block-container {
        background-color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem auto;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        max-width: 1000px;
    }

    /* Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 60%);
    color: white;
    display: flex;
    align-items: center;
    padding: 0 2rem;
    font-size: 1.5rem;
    font-weight: 700;
    z-index: 9999;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.main .block-container {
    padding-top: 5rem !important;  /* Add space below fixed navbar */
}


    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        cursor: pointer;
        transition: 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }

    /* Header Styling */
    .main-header {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        line-height: 1.1;
        color: var(--text-primary); /* Ensure fallback for visibility */
    }
    
    .sub-header {
        color: #000000;
        font-size: 1.2rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Section Headers */
    .section-header {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header::before {
        content: '';
        width: 4px;
        height: 2rem;
        background: var(--gradient-primary);
        border-radius: 2px;
    }

    /* Cards */
    .feature-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }

    /* Buttons */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        cursor: pointer;
        text-transform: none;
        letter-spacing: 0.025em;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box_shadow: var(--shadow-lg);
        background: var(--gradient-secondary);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary Buttons */
    .stButton > button[kind="secondary"] {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-accent);
        border-color: var(--primary-color);
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        background: var(--bg-secondary);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary-color);
        background: var(--bg-accent);
    }
    
    .stFileUploader label {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.1rem;
    }
    .stFileUploader div[data-testid="stFileUploaderDropzone"] p { /* Target text inside dropzone */
        color: var(--text-primary); /* Ensure text is visible */
        font-weight: 500;
    }


    /* Metrics */
    .stMetric {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid var(--border-light);
    }

    /* Alerts */
    .stAlert {
        border-radius: 12px;
        border: none;
        padding: 1rem 1.5rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .stAlert > div {
        border-radius: 8px;
    }

    /* Success Alert */
    .stAlert[data-baseweb-type="success"] {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
        border-left: 4px solid var(--success-color);
    }

    /* Error Alert */
    .stAlert[data-baseweb-type="error"] {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
        border-left: 4px solid var(--danger-color);
    }

    /* Warning Alert */
    .stAlert[data-baseweb-type="warning"] {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
        border-left: 4px solid var(--warning-color);
    }

    /* Info Alert */
    .stAlert[data-baseweb-type="info"] {
        background: rgba(59, 130, 246, 0.1);
        color: var(--info-color);
        border-left: 4px solid var(--info-color);
    }



    # /* Sidebar Navigation */
    # .css-1d391kg .stRadio > label {
    #     color: var(--text-primary);
    #     font-weight: 600;
    #     font-size: 1.1rem;
    #     margin-bottom: 0.5rem;
    # }

    # .css-1d391kg .stRadio > div {
    #     gap: 0.5rem;
    # }

    # .css-1d391kg .stRadio > div > label {
    #     background: var(--bg-secondary);
    #     border-radius: 12px;
    #     padding: 0.75rem 1rem;
    #     margin-bottom: 0.5rem;
    #     cursor: pointer;
    #     transition: all 0.3s ease;
    #     border: 1px solid var(--border-color);
    #     color: var(--text-primary); /* Ensure radio button text is visible */
    # }

    # .css-1d391kg .stRadio > div > label:hover {
    #     background: var(--bg-accent);
    #     border-color: var(--primary-color);
    # }

            # --- Navbar ---
st.markdown('<div class="navbar">TAILAI LABS PVT LTD</div>', unsafe_allow_html=True)

# --- Buttons ---
col1, col2 = st.columns(2)

with col1:
    cad_clicked = st.button("CAD Drawing Analyzer")
with col2:
    raster_clicked = st.button("Raster to Vector Converter")

# --- Content Section ---
if cad_clicked:
    st.subheader("📐 CAD Drawing Analyzer")
    st.info("CAD Analyzer functionality will be implemented here...")

elif raster_clicked:
    st.subheader("🖼️ Raster to Vector Converter")
    st.info("Raster to Vector Converter functionality will be implemented here...")

else:
    st.write("👋 Please select a tool above to get started.")
    /* Code Blocks */
    .stCode {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
        color: var(--text-primary); /* Ensure code text is visible */
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        font-weight: 600;
        padding: 1rem;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-accent);
        border-color: var(--primary-color);
    }

    .streamlit-expanderContent {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1rem;
    }

    /* Chat Messages */
    .stChatMessage {
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }

    .stChatMessage[data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
        border: none;
    }

    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: var(--bg-secondary);
        color: var(--text-primary);
        margin-right: 2rem;
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: var(--gradient-primary);
        border-radius: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 0.25rem;
        gap: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-accent);
        color: var(--text-primary);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--gradient-primary);
        color: white;
    }

    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .status-indicator.success {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
    }

    .status-indicator.error {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
    }

    .status-indicator.warning {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
    }

    /* Loading Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .loading {
        animation: pulse 2s ease-in-out infinite;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .section-header {
            font-size: 1.5rem;
        }
        
        .main .block-container {
            padding: 1rem;
            margin: 0.5rem;
        }
    }

    # /* Custom Scrollbar */
    # ::-webkit-scrollbar {
    #     width: 8px;
    # }

    # ::-webkit-scrollbar-track {
    #     background: var(--bg-secondary);
    #     border-radius: 4px;
    # }

    # ::-webkit-scrollbar-thumb {
    #     background: var(--primary-color);
    #     border-radius: 4px;
    # }

    # ::-webkit-scrollbar-thumb:hover {
    #     background: var(--primary-dark);
    # }

    /* Download Button Special Style */
    .stDownloadButton > button {
        background: var(--gradient-accent);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }

    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.9rem;
        border-top: 1px solid var(--border-light);
        background: var(--bg-secondary);
        border-radius: 12px;
    }

    .footer a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }

    .footer a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Get Groq API key from environment variable
groq_api_key = os.getenv("GROQ_API_KEY") # <--- MODIFIED LINE

# Initialize LLM Client (from CAD_GUI.py)
try:
    if groq_api_key: # <--- ADDED CHECK
        llm_client = OpenAI(
            api_key=groq_api_key, # <--- MODIFIED LINE
            base_url="https://api.groq.com/openai/v1"
        )
        st.session_state.llm_client_ready = True
    else: # <--- ADDED ELSE BLOCK
        st.error("GROQ_API_KEY environment variable not found. Please set it to enable AI services.")
        st.session_state.llm_client_ready = False
except Exception as e:
    st.error("Failed to initialize AI services. Please check your internet connection or try again later.")
    st.session_state.llm_client_ready = False

# Initialize Gradio Client (from SVG_Converter.py)
try:
    gradio_client = Client("openfree/image-to-vector")
    st.session_state.gradio_client_ready = True
except Exception as e:
    st.error("Failed to initialize vectorization services. Please check your internet connection or try again later.")
    st.session_state.gradio_client_ready = False

# --- Helper Functions ---

def get_entity_summary(msp):
    """Generates a summary of DXF entities."""
    entity_summary = defaultdict(int)
    layers = set()
    for e in msp:
        etype = e.dxftype()
        entity_summary[etype] += 1
        layers.add(e.dxf.layer)
    return entity_summary, layers

def get_entity_details(msp):
    """Generates detailed information about each DXF entity."""
    detail_text = "🔍 Entity Details:\n"
    for i, e in enumerate(msp):
        etype = e.dxftype()
        detail_text += f"\n--- Entity {i+1}: {etype} (Layer: {e.dxf.layer}) ---\n"
        try:
            if etype == 'LINE':
                detail_text += f"  Start: ({e.dxf.start.x:.2f}, {e.dxf.start.y:.2f}, {e.dxf.start.z:.2f})\n"
                detail_text += f"  End:   ({e.dxf.end.x:.2f}, {e.dxf.end.y:.2f}, {e.dxf.end.z:.2f})\n"
            elif etype == 'CIRCLE':
                detail_text += f"  Center: ({e.dxf.center.x:.2f}, {e.dxf.center.y:.2f}, {e.dxf.center.z:.2f}), Radius: {e.dxf.radius:.2f}\n"
            elif etype == 'ARC':
                detail_text += f"  Center: ({e.dxf.center.x:.2f}, {e.dxf.center.y:.2f}, {e.dxf.center.z:.2f}), Radius: {e.dxf.radius:.2f}, Start Angle: {e.dxf.start_angle:.2f}, End Angle: {e.dxf.end_angle:.2f}\n"
            elif etype == 'TEXT':
                detail_text += f"  Text: '{e.dxf.text}'\n"
                detail_text += f"  Location: ({e.dxf.insert.x:.2f}, {e.dxf.insert.y:.2f}, {e.dxf.insert.z:.2f})\n"
            elif etype == 'MTEXT':
                detail_text += f"  Text: '{e.dxf.text}'\n"
                detail_text += f"  Location: ({e.dxf.insert.x:.2f}, {e.dxf.insert.y:.2f}, {e.dxf.insert.z:.2f})\n"
            elif etype == 'LWPOLYLINE':
                points = e.get_points()
                detail_text += f"  Points ({len(points)}):\n"
                for p in points:
                    detail_text += f"    ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f})\n"
            elif etype == 'POLYLINE':
                detail_text += f"  Vertices ({len(e.vertices)}):\n"
                for v in e.vertices:
                    loc = v.dxf.location
                    detail_text += f"    ({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f})\n"
            elif etype == '3DFACE':
                pts = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx2, e.dxf.vtx3]
                detail_text += f"  Vertices:\n"
                for p in pts:
                    detail_text += f"    ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})\n"
            elif etype == 'INSERT':
                detail_text += f"  Block Name: {e.dxf.name}\n"
                detail_text += f"  Insertion Point: ({e.dxf.insert.x:.2f}, {e.dxf.insert.y:.2f}, {e.dxf.insert.z:.2f})\n"
                detail_text += f"  Scale: X={e.dxf.xscale:.2f}, Y={e.dxf.yscale:.2f}, Z={e.dxf.zscale:.2f}\n"
        except Exception as ex:
            detail_text += f"  (Error extracting details for {etype}: {ex})\n"
    return detail_text

def plot_dxf_drawing(msp):
    """Visualizes the DXF drawing using matplotlib."""
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor('#f8fafc')
    
    has_3d = any(e.dxftype() in ["3DFACE", "POLYLINE"] or getattr(e.dxf, 'z', 0) != 0 for e in msp)
    ax = fig.add_subplot(111, projection='3d' if has_3d else None)
    ax.set_facecolor('#ffffff')

    # Modern color palette
    colors = {
        'LINE': '#2563eb',
        'CIRCLE': '#10b981',
        'ARC': '#f59e0b',
        'POLYLINE': '#8b5cf6',
        'LWPOLYLINE': '#ef4444',
        '3DFACE': '#06b6d4',
        'TEXT': '#6b7280',
        'MTEXT': '#ec4899',
        'INSERT': '#64748b'
    }

    visualization_summary_parts = []
    entity_counts = defaultdict(int)
    min_x, max_x, min_y, max_y, min_z, max_z = float('inf'), float('-inf'), float('inf'), float('-inf'), float('inf'), float('-inf')
    plotted_entities_count = 0

    for e in msp:
        try:
            etype = e.dxftype()
            color = colors.get(etype, '#374151')
            
            if etype == 'LINE':
                s, ept = e.dxf.start, e.dxf.end
                ax.plot([s.x, ept.x], [s.y, ept.y], [s.z, ept.z] if has_3d else None, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, s.x, ept.x), max(max_x, s.x, ept.x)
                min_y, max_y = min(min_y, s.y, ept.y), max(max_y, s.y, ept.y)
                min_z, max_z = min(min_z, s.z, ept.z), max(max_z, s.z, ept.z)
                plotted_entities_count += 1
            elif etype == 'CIRCLE':
                center, r = e.dxf.center, e.dxf.radius
                theta = np.linspace(0, 2 * np.pi, 100)
                x = center.x + r * np.cos(theta)
                y = center.y + r * np.sin(theta)
                z = np.full_like(x, center.z) if has_3d else None
                ax.plot(x, y, z, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, center.x - r), max(max_x, center.x + r)
                min_y, max_y = min(min_y, center.y - r), max(max_y, center.y + r)
                min_z, max_z = min(min_z, center.z), max(max_z, center.z)
                plotted_entities_count += 1
            elif etype == 'ARC':
                center, r = e.dxf.center, e.dxf.radius
                start_angle_rad = np.deg2rad(e.dxf.start_angle)
                end_angle_rad = np.deg2rad(e.dxf.end_angle)
                if start_angle_rad > end_angle_rad:
                    end_angle_rad += 2 * np.pi
                theta = np.linspace(start_angle_rad, end_angle_rad, 100)
                x = center.x + r * np.cos(theta)
                y = center.y + r * np.sin(theta)
                z = np.full_like(x, center.z) if has_3d else None
                ax.plot(x, y, z, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, np.min(x)), max(max_x, np.max(x))
                min_y, max_y = min(min_y, np.min(y)), max(max_y, np.max(y))
                min_z, max_z = min(min_z, center.z), max(max_z, center.z)
                plotted_entities_count += 1
            elif etype == 'POLYLINE':
                x, y, z = [], [], []
                for v in e.vertices:
                    x.append(v.dxf.location.x)
                    y.append(v.dxf.location.y)
                    z.append(v.dxf.location.z)
                ax.plot(x, y, z if has_3d else None, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, np.min(x)), max(max_x, np.max(x))
                min_y, max_y = min(min_y, np.min(y)), max(max_y, np.max(y))
                min_z, max_z = min(min_z, np.min(z)), max(max_z, np.min(z))
                plotted_entities_count += 1
            elif etype == 'LWPOLYLINE':
                points = e.get_points(format='xy')
                x = [p[0] for p in points]
                y = [p[1] for p in points]
                lwpolyline_z = e.dxf.elevation if has_3d else 0
                z = np.full_like(x, lwpolyline_z) if has_3d else None
                ax.plot(x, y, z, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, np.min(x)), max(max_x, np.max(x))
                min_y, max_y = min(min_y, np.min(y)), max(max_y, np.max(y))
                min_z, max_z = min(min_z, lwpolyline_z), max(max_z, lwpolyline_z)
                plotted_entities_count += 1
            elif etype == '3DFACE':
                pts = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx2, e.dxf.vtx3]
                face_x = [p.x for p in pts] + [pts[0].x]
                face_y = [p.y for p in pts] + [pts[0].y]
                face_z = [p.z for p in pts] + [pts[0].z]
                ax.plot(face_x, face_y, face_z, c=color, linewidth=1.5)
                min_x, max_x = min(min_x, np.min(face_x)), max(max_x, np.max(face_x))
                min_y, max_y = min(min_y, np.min(face_y)), max(max_y, np.max(face_y))
                min_z, max_z = min(min_z, np.min(face_z)), max(max_z, np.max(face_z))
                plotted_entities_count += 1
            elif etype == 'TEXT' or etype == 'MTEXT':
                insert_point = e.dxf.insert
                text_content = e.dxf.text
                if has_3d:
                    ax.text(insert_point.x, insert_point.y, insert_point.z, text_content, color=color, fontsize=10, weight='bold')
                else:
                    ax.text(insert_point.x, insert_point.y, text_content, color=color, fontsize=10, weight='bold')
                
                min_x, max_x = min(min_x, insert_point.x), max(max_x, insert_point.x)
                min_y, max_y = min(min_y, insert_point.y), max(max_y, insert_point.y)
                min_z, max_z = min(min_z, insert_point.z), max(max_z, insert_point.z)
                plotted_entities_count += 1
            
            entity_counts[etype] += 1

        except Exception as ex:
            st.warning(f"Skipping entity {etype} due to plotting error: {ex}")
            continue

    if plotted_entities_count == 0:
        plt.close(fig)
        return None, "No plottable geometric entities were found in the DXF file. Visualization cannot be generated."

    if min_x != float('inf'):
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        bbox_depth = max_z - min_z if has_3d else 0
        visualization_summary_parts.append(f"The drawing spans from approximately ({min_x:.1f}, {min_y:.1f}{f', {min_z:.1f}' if has_3d else ''}) to ({max_x:.1f}, {max_y:.1f}{f', {max_z:.1f}' if has_3d else ''}).")
        visualization_summary_parts.append(f"Overall dimensions are approximately Width: {bbox_width:.1f}, Height: {bbox_height:.1f}{f', Depth: {bbox_depth:.1f}' if has_3d else ''}.")
    else:
        visualization_summary_parts.append("No bounding box could be determined for the visualized entities.")

    if has_3d:
        visualization_summary_parts.append("The visualization is a 3D plot.")
        ax.set_xlabel('X-axis', color='#374151')
        ax.set_ylabel('Y-axis', color='#374151')
        ax.set_zlabel('Z-axis', color='#374151')
        ax.tick_params(axis='x', colors='#374151')
        ax.tick_params(axis='y', colors='#374151')
        ax.tick_params(axis='z', colors='#374151')
    else:
        visualization_summary_parts.append("The visualization is a 2D plot.")
        ax.set_xlabel('X-axis', color='#374151')
        ax.set_ylabel('Y-axis', color='#374151')
        ax.tick_params(axis='x', colors='#374151')
        ax.tick_params(axis='y', colors='#374151')

    entity_viz_counts = ", ".join([f"{count} {etype.lower()}(s)" for etype, count in entity_counts.items()])
    if entity_viz_counts:
        visualization_summary_parts.append(f"It visually represents: {entity_viz_counts}.")
    else:
        visualization_summary_parts.append("No geometric entities were visualized.")

    plt.title("DXF Geometry Visualization", fontsize=16, color='#1f2937', weight='bold')
    plt.grid(True, linestyle='--', alpha=0.7, color='#e2e8f0') # Lighter grid
    plt.tight_layout()
    return fig, " ".join(visualization_summary_parts)

def generate_llm_summary(msp, entity_summary, visualization_description):
    """Generates a professional summary of the DXF drawing using the LLM."""
    if not st.session_state.llm_client_ready:
        return "AI services are not available. Cannot generate summary."

    geom = "\n".join([f"- {k}: {v}" for k, v in entity_summary.items()])

    annots = ""
    for e in msp:
        if e.dxftype() in ['TEXT', 'MTEXT']:
            annots += f"- '{e.dxf.text}' at ({e.dxf.insert.x:.2f}, {e.dxf.insert.y:.2f})\n"
    if not annots:
        annots = "No text annotations found."

    prompt = f"""
You are a highly experienced CAD expert and analyst. Your task is to provide a comprehensive, professional summary of a DXF drawing.
Consider the following information:

1.  **Geometric Entity Breakdown:**
    {geom}

2.  **Text Annotations/Labels:**
    {annots}

3.  **Visual Characteristics (from Visualization):**
    {visualization_description if visualization_description else 'No geometric visualization could be generated for this drawing, possibly due to a lack of plottable entities.'}

Based on the above data, generate a professional summary describing:
-   What the drawing most likely represents (e.g., a mechanical part, an architectural floor plan, an electrical schematic, an electrical schematic, a site layout).
-   Its key features, components, or design elements.
-   Any notable dimensions, patterns, or arrangements inferred from the entity types and their quantities.
-   If it's 3D, mention its spatial nature.
-   If there are text annotations, integrate their meaning into the summary.
-   Keep the summary concise yet informative, suitable for an engineering or design review.
"""
    with st.spinner("Generating AI summary... This may take a moment."):
        try:
            response = llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a CAD expert providing professional summaries of DXF drawings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Summary Generation Failed: {e}"

def generate_chatbot_response(user_question, entity_summary, layers, visualization_description, chat_history):
    """Generates a chatbot response using the LLM based on the current DXF context."""
    if not st.session_state.llm_client_ready:
        return "AI services are not available. Cannot respond."

    context_prompt = f"""
Current DXF Context:
- Entity Summary: {dict(entity_summary)}
- Layers: {list(layers)}
- Visualization Description: {visualization_description if visualization_description else 'No geometric visualization available for context.'}
- User Question: {user_question}

Based on the provided DXF context, answer the user's question concisely and helpfully.
If the question cannot be answered from the provided DXF data, state that.
"""
    messages_for_llm = chat_history + [{"role": "user", "content": context_prompt}]

    with st.spinner("Bot thinking..."):
        try:
            response = llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_llm,
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Chatbot Error: {e}"

def extract_image_from_pdf(pdf_file):
    """Extracts the first page as an image from a PDF file-like object."""
    doc = None
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if not doc.page_count == 1:
            st.warning("PDF contains more than one page. Only the first page will be processed.")

        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Render at 2x resolution

        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        return image
    except Exception as e:
        st.error(f"Error extracting image from PDF. Please ensure it's a valid PDF.")
        return None
    finally:
        if doc:
            doc.close()

def convert_image_to_svg(image_pil):
    """Converts a PIL Image to SVG using the Hugging Face Gradio API."""
    if not st.session_state.gradio_client_ready:
        st.error("Vectorization services are not available. Cannot convert to SVG.")
        return None

    temp_image_path = None
    temp_svg_from_api_path = None
    svg_string = None

    with st.spinner("Converting image to SVG... This may take a moment."):
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_image_path = temp_file.name
                image_pil.save(temp_image_path)

            result = gradio_client.predict(
                image=handle_file(temp_image_path),
                colormode="color", hierarchical="stacked", mode="spline",
                filter_speckle=4, color_precision=6, layer_difference=16,
                corner_threshold=60, length_threshold=4, max_iterations=10,
                splice_threshold=45, path_precision=3,
                api_name="/convert_to_vector_1"
            )

            if isinstance(result, tuple) and len(result) > 1 and isinstance(result[1], str) and os.path.exists(result[1]):
                temp_svg_from_api_path = result[1]
                with open(temp_svg_from_api_path, "r") as f:
                    svg_string = f.read()
            elif isinstance(result, str):
                svg_string = result
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], str):
                svg_string = result[0]
            else:
                st.error("SVG conversion failed: Unexpected response from conversion service.")
                return None

            if svg_string:
                st.success("Image successfully converted to SVG!")
                return svg_string
            else:
                st.error("SVG conversion failed: No SVG content received.")
                return None

        except Exception as e:
            st.error(f"Error during SVG conversion. Please ensure the image is valid and try again.")
            return None
        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            if temp_svg_from_api_path and os.path.exists(temp_svg_from_api_path):
                os.remove(temp_svg_from_api_path)

def convert_svg_to_dxf(svg_content):
    """Converts SVG content to DXF using ezdxf."""
    if ezdxf is None:
        st.error("The 'ezdxf' library is not available. Cannot export to DXF. Please ensure it's installed.")
        return None

    temp_dxf_path = None
    dxf_bytes = None

    with st.spinner("Exporting SVG to DXF..."):
        try:
            doc = ezdxf.new("R2010")
            msp = doc.modelspace()
            root = ET.fromstring(svg_content)
            svg_ns = "{http://www.w3.org/2000/svg}"

            # Basic parsing for <path> elements
            for path_element in root.findall(f".//{svg_ns}path"):
                d_attr = path_element.get("d")
                if d_attr:
                    points = []
                    current_x, current_y = 0.0, 0.0
                    path_commands = d_attr.replace(',', ' ').split()

                    i = 0
                    while i < len(path_commands):
                        command = path_commands[i]
                        i += 1

                        if command == 'M' or command == 'm':
                            x = float(path_commands[i])
                            y = float(path_commands[i+1])
                            i += 2
                            if command == 'm':
                                current_x += x
                                current_y += y
                            else:
                                current_x = x
                                current_y = y
                            if points:
                                msp.add_lwpolyline(points)
                                points = []
                            points.append((current_x, current_y))

                        elif command == 'L' or command == 'l':
                            x = float(path_commands[i])
                            y = float(path_commands[i+1])
                            i += 2
                            if command == 'l':
                                current_x += x
                                current_y += y
                            else:
                                current_x = x
                                current_y = y
                            points.append((current_x, current_y))

                        elif command == 'H' or command == 'h':
                            val = float(path_commands[i])
                            i += 1
                            if command == 'h':
                                current_x += val
                            else:
                                current_x = val
                            points.append((current_x, current_y))

                        elif command == 'V' or command == 'v':
                            val = float(path_commands[i])
                            i += 1
                            if command == 'v':
                                current_y += val
                            else:
                                current_y = val
                            points.append((current_x, current_y))

                        elif command == 'Z' or command == 'z':
                            if points:
                                if points[0] != points[-1]:
                                    points.append(points[0])
                                msp.add_lwpolyline(points, close=True)
                                points = []
                        else:
                            while i < len(path_commands) and (path_commands[i][0].isdigit() or path_commands[i][0] == '-' or path_commands[i][0] == '.'):
                                i += 1

                    if points:
                        msp.add_lwpolyline(points)

            # Handle <rect> elements
            for rect_element in root.findall(f".//{svg_ns}rect"):
                x = float(rect_element.get('x', 0))
                y = float(rect_element.get('y', 0))
                width = float(rect_element.get('width', 0))
                height = float(rect_element.get('height', 0))
                if width > 0 and height > 0:
                    points = [
                        (x, y),
                        (x + width, y),
                        (x + width, y + height),
                        (x, y + height),
                        (x, y)
                    ]
                    msp.add_lwpolyline(points, close=True)

            # Handle <circle> elements
            for circle_element in root.findall(f".//{svg_ns}circle"):
                cx = float(circle_element.get('cx', 0))
                cy = float(circle_element.get('cy', 0))
                r = float(circle_element.get('r', 0))
                if r > 0:
                    msp.add_circle((cx, cy), r)

            # Handle <ellipse> elements
            for ellipse_element in root.findall(f".//{svg_ns}ellipse"):
                cx = float(ellipse_element.get('cx', 0))
                cy = float(ellipse_element.get('cy', 0))
                rx = float(ellipse_element.get('rx', 0))
                ry = float(ellipse_element.get('ry', 0))
                if rx > 0 and ry > 0:
                    msp.add_ellipse(center=(cx, cy), major_axis=(rx, 0), ratio=ry/rx)

            # Handle <line> elements
            for line_element in root.findall(f".//{svg_ns}line"):
                x1 = float(line_element.get('x1', 0))
                y1 = float(line_element.get('y1', 0))
                x2 = float(line_element.get('x2', 0))
                y2 = float(line_element.get('y2', 0))
                msp.add_line((x1, y1), (x2, y2))

            # Handle <polyline> elements
            for polyline_element in root.findall(f".//{svg_ns}polyline"):
                points_str = polyline_element.get('points', '')
                if points_str:
                    points = []
                    for pair in points_str.split():
                        coords = pair.split(',')
                        if len(coords) == 2:
                            points.append((float(coords[0]), float(coords[1])))
                    if points:
                        msp.add_lwpolyline(points)

            # Handle <polygon> elements
            for polygon_element in root.findall(f".//{svg_ns}polygon"):
                points_str = polygon_element.get('points', '')
                if points_str:
                    points = []
                    for pair in points_str.split():
                        coords = pair.split(',')
                        if len(coords) == 2:
                            points.append((float(coords[0]), float(coords[1])))
                    if points:
                        msp.add_lwpolyline(points, close=True)

            # Handle <text> elements
            for text_element in root.findall(f".//{svg_ns}text"):
                x = float(text_element.get('x', 0))
                y = float(text_element.get('y', 0))
                text_content = text_element.text or ""
                font_size = float(text_element.get('font-size', '12').replace('px', ''))
                msp.add_text(text_content, dxfattribs={
                    'height': font_size,
                    'insert': (x, y),
                    'halign': 0,
                    'valign': 0
                })

            with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as temp_dxf_file:
                temp_dxf_file.write(doc.getvalue().encode('utf-8')) # Save DXF content to bytes
                temp_dxf_path = temp_dxf_file.name

            with open(temp_dxf_path, "rb") as f:
                dxf_bytes = f.read()

            st.success("SVG successfully exported to DXF!")
            return dxf_bytes

        except ET.ParseError as e:
            st.error(f"DXF export failed: The SVG content is malformed or contains unsupported features.")
            return None
        except Exception as e:
            st.error(f"An error occurred during DXF export. Ensure the SVG content is suitable for DXF conversion.")
            return None
        finally:
            if temp_dxf_path and os.path.exists(temp_dxf_path):
                os.remove(temp_dxf_path)

# --- Streamlit UI Functions ---

def cad_analyzer_section():
    """Renders the CAD Drawing Analyzer section."""
    st.markdown("<h3 class='section-header'>🛠️ CAD Drawing Analyzer</h3>", unsafe_allow_html=True)
    st.markdown("Upload a DXF file to analyze its entities, layers, visualize its geometry, and get an AI-powered summary and chat support.")

    uploaded_file = st.file_uploader("Upload DXF File", type=["dxf"], key="dxf_uploader")

    if uploaded_file is not None:
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            doc = ezdxf.readfile(temp_file_path)
            msp = doc.modelspace()

            st.session_state.doc = doc
            st.session_state.msp = msp
            st.session_state.entity_summary, st.session_state.layers = get_entity_summary(msp)
            st.session_state.visualization_description = ""
            st.session_state.chat_history = []  # No system message

            st.success(f"Successfully loaded DXF file: **{uploaded_file.name}**")

            st.markdown("<h4 class='section-header'>📊 Entity Summary</h4>", unsafe_allow_html=True)
            summary_text = "Entity Count:\n"
            for k, v in st.session_state.entity_summary.items():
                summary_text += f"- {k}: {v}\n"
            st.code(summary_text, language="text")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔍 View Entity Details", key="view_details_btn"):
                    with st.expander("Detailed Entity Information", expanded=True):
                        st.text_area("Details", get_entity_details(msp), height=300)

            with col2:
                if st.button("📄 Show Layers", key="show_layers_btn"):
                    with st.expander("Layers in Drawing", expanded=True):
                        if st.session_state.layers:
                            st.write(", ".join(sorted(st.session_state.layers)))
                        else:
                            st.info("No layers found in the DXF file.")

            st.markdown("<h4 class='section-header'>📈 Drawing Visualization</h4>", unsafe_allow_html=True)
            if st.button("Visualize Drawing", key="visualize_btn"):
                fig, viz_desc = plot_dxf_drawing(msp)
                st.session_state.visualization_description = viz_desc
                if fig:
                    st.pyplot(fig)
                    st.info("Drawing visualized.")
                else:
                    st.warning(viz_desc)
                plt.close(fig)

            st.markdown("<h4 class='section-header'>🤖 AI-Powered Analysis</h4>", unsafe_allow_html=True)
            if st.session_state.llm_client_ready:
                if st.button("Generate AI Summary", key="llm_summary_btn"):
                    summary = generate_llm_summary(
                        msp,
                        st.session_state.entity_summary,
                        st.session_state.visualization_description
                    )
                    st.markdown("---")
                    st.subheader("AI Summary:")
                    st.write(summary)
                    st.markdown("---")
            else:
                st.warning("AI services not available. AI summary generation disabled.")

            st.markdown("<h4 class='section-header'>💬 CAD Chatbot</h4>", unsafe_allow_html=True)

            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Type your question here..."):
                if not st.session_state.llm_client_ready:
                    st.warning("AI services not available. Chatbot disabled.")
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    with st.chat_message("assistant"):
                        st.markdown("Chatbot is currently unavailable.")
                    return

                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                bot_response = generate_chatbot_response(
                    prompt,
                    st.session_state.entity_summary,
                    st.session_state.layers,
                    st.session_state.visualization_description,
                    st.session_state.chat_history
                )
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                with st.chat_message("assistant"):
                    st.markdown(bot_response)

        except ezdxf.DXFStructureError as e:
            st.error("Error reading DXF file: The file might be corrupted or invalid. Please ensure it's a valid DXF.")
            st.session_state.doc = None
            st.session_state.msp = None
            st.session_state.entity_summary = {}
            st.session_state.layers = set()
            st.session_state.visualization_description = ""
        except UnicodeDecodeError as e:
            st.error("Encoding error while reading DXF file. The DXF file might contain unsupported characters. Please check the file's integrity.")
            st.session_state.doc = None
            st.session_state.msp = None
            st.session_state.entity_summary = {}
            st.session_state.layers = set()
            st.session_state.visualization_description = ""
        except Exception as e:
            st.error(f"An unexpected error occurred while processing the DXF file: {e}. Please try a different DXF file or contact support.")
            st.session_state.doc = None
            st.session_state.msp = None
            st.session_state.entity_summary = {}
            st.session_state.layers = set()
            st.session_state.visualization_description = ""
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    else:
        st.info("Please upload a DXF file to get started with CAD analysis.")

def raster_to_vector_section():
    """Renders the Raster to Vector Converter section."""
    st.markdown("<h3 class='section-header'>🖼️ Raster to Vector Converter</h3>", unsafe_allow_html=True)
    st.markdown("Convert raster images (JPG, PNG) or single-page PDFs into scalable vector graphics (SVG) and then export them to DXF format.")

    uploaded_file = st.file_uploader("Upload Image (JPG/PNG) or PDF", type=["png", "jpg", "jpeg", "pdf"], key="vector_uploader")

    st.markdown("---")

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        st.session_state.uploaded_file_name = uploaded_file.name

        image_to_process = None
        if file_extension in ["png", "jpg", "jpeg"]:
            image_to_process = Image.open(uploaded_file)
        elif file_extension == "pdf":
            image_to_process = extract_image_from_pdf(uploaded_file)

        if image_to_process:
            st.session_state.current_image_pil = image_to_process
            st.success(f"File **{uploaded_file.name}** loaded for conversion.")
            st.subheader("Image Preview:")
            st.image(image_to_process, caption="Uploaded Image", use_container_width=True)

            if st.session_state.gradio_client_ready:
                if st.button("Convert to SVG", key="convert_to_svg_btn"):
                    svg_content = convert_image_to_svg(st.session_state.current_image_pil)
                    if svg_content:
                        st.session_state.last_svg_content = svg_content
                        st.download_button(
                            label="Download SVG",
                            data=svg_content.encode("utf-8"),
                            file_name=f"{os.path.splitext(st.session_state.uploaded_file_name)[0]}_vectorized.svg",
                            mime="image/svg+xml",
                            key="download_svg_btn"
                        )
                        st.info("SVG conversion complete. You can now export to DXF.")
                    else:
                        st.error("SVG conversion failed.")
            else:
                st.warning("Vectorization services not available. SVG conversion disabled.")

            if st.session_state.get('last_svg_content'):
                if st.button("Export to DXF", key="export_to_dxf_btn"):
                    dxf_bytes = convert_svg_to_dxf(st.session_state.last_svg_content)
                    if dxf_bytes:
                        st.download_button(
                            label="Download DXF",
                            data=dxf_bytes,
                            file_name=f"{os.path.splitext(st.session_state.uploaded_file_name)[0]}_vectorized.dxf",
                            mime="application/dxf",
                            key="download_dxf_btn"
                        )
                    else:
                        st.error("DXF export failed.")
            else:
                st.info("Convert to SVG first to enable DXF export.")
        else:
            st.error("Could not process the uploaded file. Please ensure it's a valid image or a single-page PDF.")
            st.session_state.current_image_pil = None
            st.session_state.last_svg_content = None
    else:
        st.info("Please upload an image or PDF file to get started with vectorization.")

# --- Main Application Logic ---

def main():
    # --- Full-width Fixed Navbar ---
    st.markdown(
        """
        <div class="navbar">
            <img src="https://github.com/Tailailabs/TAILAI_CAD_Analyzer/blob/main/Tailai_LOGO.jpeg?raw=true" 
                 alt="TAILAI Logo" 
                 style="height: 40px; margin-right: 10px; border-radius: 5px;">
        </div>
        """, 
        unsafe_allow_html=True
    )

    # --- Horizontal Radio for Navigation ---
    nav_option = st.radio(
        "Choose a functionality:",
        ["CAD Drawing Analyzer", "Raster to Vector Converter"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- Initialize State ---
    for key, default in {
        'doc': None,
        'msp': None,
        'entity_summary': {},
        'layers': set(),
        'visualization_description': "",
        'chat_history': [{"role": "system", "content": "You are a helpful CAD assistant. Respond concisely and accurately based on the provided DXF data."}],
        'current_image_pil': None,
        'last_svg_content': None,
        'uploaded_file_name': ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # --- Load Section ---
    if nav_option == "CAD Drawing Analyzer":
        cad_analyzer_section()
    elif nav_option == "Raster to Vector Converter":
        raster_to_vector_section()


    # --- Optional Footer (Uncomment if needed) ---
    st.markdown("<div class='footer'>© 2025 TAILAI LABS PVT LTD. All rights reserved.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
