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
@st.cache_resource
def get_gradio_client():
    try:
        client = Client("openfree/image-to-vector")
        # Removed st.session_state modification from here
        return client
    except Exception as e:
        # Error message will be handled outside this function
        return None # Return None if initialization fails

gradio_client = get_gradio_client()

# Update session state based on whether client initialization was successful
if gradio_client is not None:
    st.session_state.gradio_client_ready = True
else:
    st.session_state.gradio_client_ready = False
    st.error("Failed to initialize vectorization services. Please check your internet connection or try again later.")


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

        visualization_summary_parts.append(f"The drawing spans from X: {min_x:.2f} to {max_x:.2f}, Y: {min_y:.2f} to {max_y:.2f}")
        if has_3d:
            visualization_summary_parts.append(f", and Z: {min_z:.2f} to {max_z:.2f}.")
        else:
            visualization_summary_parts.append(".")

        # Set equal aspect ratio
        if has_3d:
            max_range = np.array([bbox_width, bbox_height, bbox_depth]).max()
            mid_x = (min_x + max_x) * 0.5
            mid_y = (min_y + max_y) * 0.5
            mid_z = (min_z + max_z) * 0.5 if has_3d else 0

            ax.set_xlim(mid_x - max_range, mid_x + max_range)
            ax.set_ylim(mid_y - max_range, mid_y + max_range)
            ax.set_zlim(mid_z - max_range, mid_z + max_range)
        else:
            ax.set_aspect('equal', adjustable='box')
            ax.autoscale_view()

    ax.set_title("DXF Drawing Visualization", fontsize=16, color='#1f2937')
    ax.set_xlabel("X-axis", color='#374151')
    ax.set_ylabel("Y-axis", color='#374151')
    if has_3d:
        ax.set_zlabel("Z-axis", color='#374151')
    
    # Grid and ticks
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Improve tick visibility
    ax.tick_params(axis='x', colors='#4b5563')
    ax.tick_params(axis='y', colors='#4b5563')
    if has_3d:
        ax.tick_params(axis='z', colors='#4b5563')

    # Create a BytesIO object to save the figure
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    buf.seek(0)
    plt.close(fig) # Close the figure to free up memory

    for etype, count in entity_counts.items():
        visualization_summary_parts.append(f"{count} {etype}s")

    visualization_description = "The visualization displays various entities found in the DXF file. " + \
                                ", ".join(visualization_summary_parts) + \
                                " This visual helps in understanding the layout and components of the CAD drawing."

    return buf, visualization_description

def get_llm_response(prompt):
    """Fetches a response from the LLM based on the given prompt."""
    if not st.session_state.llm_client_ready:
        return "AI services are not available. Please ensure GROQ_API_KEY is set."
    
    try:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Filter chat history to only include system, user, and assistant roles
        # Ensure only the last few relevant turns are sent if history becomes too long
        relevant_history = []
        # Keep initial system message
        if st.session_state.chat_history and st.session_state.chat_history[0]["role"] == "system":
            relevant_history.append(st.session_state.chat_history[0])
        
        # Add a few recent user/assistant messages to maintain context
        # Adjust this number based on typical conversation length and token limits
        recent_messages = [msg for msg in st.session_state.chat_history if msg["role"] in ["user", "assistant"]][-5:] 
        relevant_history.extend(recent_messages)


        chat_completion = llm_client.chat.completions.create(
            messages=relevant_history,
            model="llama3-8b-8192", # Or another suitable model
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        response = chat_completion.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        return f"Error communicating with AI: {e}. Please try again."

def cad_analyzer_section():
    """Handles the CAD Drawing Analyzer functionality."""
    st.markdown("<h2 class='section-header'>📐 CAD Drawing Analyzer</h2>", unsafe_allow_html=True)
    st.write("Upload a DXF file to analyze its structure, visualize entities, and chat with an AI assistant about its content.")

    uploaded_file = st.file_uploader("Upload DXF File", type=["dxf"], key="dxf_uploader")

    if uploaded_file is not None:
        try:
            # Check if a new file is uploaded or if 'doc' is not in session_state
            # or if the current uploaded file name is different from the last processed one.
            if uploaded_file.name != st.session_state.uploaded_file_name or st.session_state.doc is None:
                # Save uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                st.session_state.doc = ezdxf.readfile(tmp_path)
                st.session_state.msp = st.session_state.doc.modelspace()
                
                # Clear chat history for new file
                st.session_state.chat_history = [{"role": "system", "content": "You are a helpful CAD assistant. Respond concisely and accurately based on the provided DXF data."}]
                st.session_state.uploaded_file_name = uploaded_file.name # Store the name of the newly processed file

                # Perform initial analysis
                entity_summary, layers = get_entity_summary(st.session_state.msp)
                st.session_state.entity_summary = entity_summary
                st.session_state.layers = layers

                # Generate visualization
                img_buffer, vis_desc = plot_dxf_drawing(st.session_state.msp)
                if img_buffer:
                    st.session_state.current_image_pil = Image.open(img_buffer)
                    st.session_state.visualization_description = vis_desc
                else:
                    st.session_state.current_image_pil = None
                    st.session_state.visualization_description = vis_desc # Store the error message

                os.remove(tmp_path) # Clean up the temporary file

            st.success(f"DXF file '{uploaded_file.name}' loaded successfully!")

            # Display sections
            st.markdown("---")
            st.markdown("<h3 class='sub-header'>Summary & Visualization</h3>", unsafe_allow_html=True)
            col_summary, col_vis = st.columns([1, 2])

            with col_summary:
                st.markdown("#### Entity Summary:")
                if st.session_state.entity_summary:
                    for entity_type, count in st.session_state.entity_summary.items():
                        st.write(f"- **{entity_type}**: {count}")
                else:
                    st.info("No entities found or unable to parse summary.")

                st.markdown("#### Layers Found:")
                if st.session_state.layers:
                    for layer in sorted(list(st.session_state.layers)):
                        st.write(f"- {layer}")
                else:
                    st.info("No layers found.")

            with col_vis:
                if st.session_state.current_image_pil:
                    st.image(st.session_state.current_image_pil, caption="DXF Drawing Visualization", use_column_width=True)
                    st.markdown(f"<p class='text-muted'>{st.session_state.visualization_description}</p>", unsafe_allow_html=True)
                else:
                    st.warning(st.session_state.visualization_description) # Display error if no image

            st.markdown("---")
            st.markdown("<h3 class='sub-header'>AI Assistant for CAD</h3>", unsafe_allow_html=True)

            if not st.session_state.llm_client_ready:
                st.warning("AI assistant is not available. Please ensure GROQ_API_KEY is set in your environment variables.")
            else:
                st.markdown(f"""
                <div style="
                    background-color: var(--bg-secondary); 
                    border-radius: 12px; 
                    padding: 1rem; 
                    margin-bottom: 1rem; 
                    border: 1px solid var(--border-color);
                    box-shadow: var(--shadow-sm);
                ">
                    <small>Type your questions about the DXF file. Examples: "What are the dimensions of the lines?", "Count all circles", "Explain the purpose of Layer 'ABC'".</small>
                </div>
                """, unsafe_allow_html=True)

                # Display chat messages from history on app rerun
                for message in st.session_state.chat_history:
                    if message["role"] != "system": # Don't display the system message
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                # React to user input
                if prompt := st.chat_input("Ask about the DXF file..."):
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            entity_details = get_entity_details(st.session_state.msp)
                            context_prompt = f"The user has uploaded a DXF file. Here is a summary of its entities: {st.session_state.entity_summary}. Here are some details about individual entities:\n{entity_details}\n\nUser's question: {prompt}"
                            full_response = get_llm_response(context_prompt)
                            st.markdown(full_response)

        except ezdxf.DXFStructureError as e:
            st.error(f"Error reading DXF file: {e}. Please ensure it's a valid DXF format.")
            st.session_state.doc = None # Clear invalid doc from state
            st.session_state.msp = None
            st.session_state.current_image_pil = None
            st.session_state.visualization_description = ""
            st.session_state.entity_summary = {}
            st.session_state.layers = set()
            st.session_state.chat_history = [{"role": "system", "content": "You are a helpful CAD assistant. Respond concisely and accurately based on the provided DXF data."}]
            st.session_state.uploaded_file_name = ""

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.doc = None # Clear invalid doc from state
            st.session_state.msp = None
            st.session_state.current_image_pil = None
            st.session_state.visualization_description = ""
            st.session_state.entity_summary = {}
            st.session_state.layers = set()
            st.session_state.chat_history = [{"role": "system", "content": "You are a helpful CAD assistant. Respond concisely and accurately based on the provided DXF data."}]
            st.session_state.uploaded_file_name = ""

    else:
        st.info("Please upload a DXF file to get started with CAD analysis.")

def raster_to_vector_section():
    """Handles the Raster to Vector Converter functionality."""
    st.markdown("<h2 class='section-header'>🖼️ Raster to Vector Converter</h2>", unsafe_allow_html=True)
    st.write("Convert raster images (PNG, JPG) and PDF documents into editable vector formats like SVG and DXF.")

    uploaded_image = st.file_uploader("Upload Image or PDF", type=["png", "jpg", "jpeg", "pdf"], key="image_pdf_uploader")

    if uploaded_image is not None:
        if uploaded_image.name != st.session_state.uploaded_file_name or st.session_state.current_image_pil is None:
            try:
                if uploaded_image.type == "application/pdf":
                    # Read PDF using PyMuPDF
                    pdf_document = fitz.open(stream=uploaded_image.getvalue(), filetype="pdf")
                    # Render the first page as a PNG image
                    page = pdf_document.load_page(0)  # Load the first page
                    pix = page.get_pixmap()
                    img_buffer = io.BytesIO(pix.pil_tobytes(format="PNG"))
                    st.session_state.current_image_pil = Image.open(img_buffer)
                    pdf_document.close()
                else:
                    st.session_state.current_image_pil = Image.open(uploaded_image)
                
                st.session_state.uploaded_file_name = uploaded_image.name
                st.session_state.last_svg_content = None # Clear previous SVG content
                st.success(f"File '{uploaded_image.name}' loaded successfully for vectorization.")
            except Exception as e:
                st.error(f"Error loading file: {e}. Please ensure it's a valid image or PDF.")
                st.session_state.current_image_pil = None
                st.session_state.uploaded_file_name = ""
        
        if st.session_state.current_image_pil:
            st.image(st.session_state.current_image_pil, caption="Uploaded Image/PDF Preview", use_column_width=True)

            st.markdown("---")
            st.markdown("<h3 class='sub-header'>Vectorization Options</h3>", unsafe_allow_html=True)

            if st.session_state.gradio_client_ready:
                col_convert, col_options = st.columns([1, 1])
                
                with col_convert:
                    if st.button("Convert to Vector (SVG/DXF)"):
                        with st.spinner("Converting... This may take a moment."):
                            try:
                                # Save the PIL image to a temporary file for Gradio Client
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img_file:
                                    st.session_state.current_image_pil.save(tmp_img_file, format="PNG")
                                    tmp_img_path = tmp_img_file.name

                                # Use handle_file to prepare the image for Gradio
                                gradio_file = handle_file(tmp_img_path)

                                # Call the Gradio API
                                # Assuming the 'image-to-vector' model has a specific input/output signature.
                                # You might need to adjust '0' based on the actual API signature.
                                result = gradio_client.predict(
                                    gradio_file,
                                    api_name="/predict" # Or the correct API endpoint if different
                                )
                                
                                os.remove(tmp_img_path) # Clean up temp image file

                                if isinstance(result, str) and result.strip().endswith(".svg"):
                                    # Result is likely a path to the SVG file
                                    # Fetch the content if it's a path, or directly use if content
                                    # For Hugging Face Gradio, result is usually a file path
                                    with open(result, 'r') as f:
                                        svg_content = f.read()
                                    st.session_state.last_svg_content = svg_content
                                    st.success("Conversion successful!")
                                    st.download_button(
                                        label="Download SVG",
                                        data=svg_content,
                                        file_name=f"{os.path.splitext(uploaded_image.name)[0]}.svg",
                                        mime="image/svg+xml",
                                        key="download_svg_button"
                                    )
                                    # Offer DXF conversion if SVG is available (requires a separate service or library)
                                    st.info("DXF download coming soon! (Requires SVG to DXF conversion logic)")
                                    
                                elif isinstance(result, dict) and 'name' in result and result['name'].endswith(".svg"):
                                    # Handle Gradio's File class output
                                    file_path = result['name']
                                    with open(file_path, 'r') as f:
                                        svg_content = f.read()
                                    st.session_state.last_svg_content = svg_content
                                    st.success("Conversion successful!")
                                    st.download_button(
                                        label="Download SVG",
                                        data=svg_content,
                                        file_name=f"{os.path.splitext(uploaded_image.name)[0]}.svg",
                                        mime="image/svg+xml",
                                        key="download_svg_button"
                                    )
                                    st.info("DXF download coming soon! (Requires SVG to DXF conversion logic)")
                                else:
                                    st.error("Vectorization service returned an unexpected result format.")
                                    st.json(result) # For debugging: show the raw result

                            except Exception as e:
                                st.error(f"Error during vectorization: {e}. Please try again.")
                                st.session_state.last_svg_content = None
            else:
                st.warning("Vectorization service is not available. Please check your internet connection or the service status.")
                
            # Display SVG if available
            if st.session_state.last_svg_content:
                st.markdown("---")
                st.markdown("<h3 class='sub-header'>Vectorized Output Preview (SVG)</h3>", unsafe_allow_html=True)
                st.components.v1.html(st.session_state.last_svg_content, height=600, scrolling=True)
        else:
            st.info("Please upload an image or PDF file to get started with vectorization.")

# --- Main Application Logic ---

def main():
    # --- Full-width Fixed Navbar ---
    st.markdown("""
    <div class="navbar">
        <img src="https://github.com/Tailailabs/TAILAI_CAD_Analyzer/blob/main/Tailai_LOGO.jpeg?raw=true" 
             alt="TAILAI Logo" 
             style="height: 40px; margin-right: 10px; border-radius: 5px;">
        </div>
    """, 
    unsafe_allow_html=True)

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
        'uploaded_file_name': "",
        'gradio_client_ready': False # <-- ADDED THIS LINE
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # --- Load Section ---
    if nav_option == "CAD Drawing Analyzer":
        cad_analyzer_section()
    elif nav_option == "Raster to Vector Converter":
        raster_to_vector_section()


    # --- Optional Footer (Uncomment if needed) ---
    st.markdown("""<div class='footer'>© 2025 TAILAI LABS PVT LTD. All rights reserved.</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
