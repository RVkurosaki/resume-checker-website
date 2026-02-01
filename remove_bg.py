try:
    from PIL import Image
    import numpy as np
    
    # Process fox_standing.png
    img1 = Image.open(r'C:\Users\shaik\.gemini\antigravity\brain\7888f1f2-340c-488f-9289-16a6e3771c7a\fox_standing_transparent_1769882152388.png').convert('RGBA')
    data1 = np.array(img1)
    
    # Make white (also shades close to white) pixels transparent
    red, green, blue, alpha = data1[:,:,0], data1[:,:,1], data1[:,:,2], data1[:,:,3]
    white_areas = (red > 240) & (green > 240) & (blue > 240)
    data1[white_areas, 3] = 0  # Set alpha to 0 for white areas
    
    result1 = Image.fromarray(data1)
    result1.save(r'static\images\fox_standing.png')
    print("✓ fox_standing.png processed")
    
    # Process fox_running.png
    img2 = Image.open(r'C:\Users\shaik\.gemini\antigravity\brain\7888f1f2-340c-488f-9289-16a6e3771c7a\fox_running_transparent_1769882169388.png').convert('RGBA')
    data2 = np.array(img2)
    
    red, green, blue, alpha = data2[:,:,0], data2[:,:,1], data2[:,:,2], data2[:,:,3]
    white_areas = (red > 240) & (green > 240) & (blue > 240)
    data2[white_areas, 3] = 0
    
    result2 = Image.fromarray(data2)
    result2.save(r'static\images\fox_running.png')
    print("✓ fox_running.png processed")
    
    print("\n✨ Both mascot images now have transparent backgrounds!")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("PIL (Pillow) is not installed. Installing it now...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'Pillow', 'numpy'])
    print("Please run this script again.")
