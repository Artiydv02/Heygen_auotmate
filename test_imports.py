# Test imports
try:
    from product_feature_heygen_video.tools.gcs_tool import GCStorageTool
    from product_feature_heygen_video.tools.heygen_tools import HeyGenVideoTool
    print("Imports successful!")
    print(f"GCStorageTool: {GCStorageTool}")
    print(f"HeyGenVideoTool: {HeyGenVideoTool}")
except Exception as e:
    print(f"Import error: {e}") 