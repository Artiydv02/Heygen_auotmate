import sys
sys.path.append('.')
try:
    from src.product_feature_heygen_video.tools.heygen_tools import HeyGenVideoTool
    print("HeyGenVideoTool import successful!")
except ImportError as e:
    print(f"HeyGenVideoTool import failed: {e}")

try:
    from src.product_feature_heygen_video.tools.gcs_tool import GCStorageTool
    print("GCStorageTool import successful!")
except ImportError as e:
    print(f"GCStorageTool import failed: {e}") 