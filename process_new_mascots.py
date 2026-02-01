from PIL import Image
import numpy as np

# Process fox_happy.png
try:
    img1 = Image.open(r'C:\Users\shaik\.gemini\antigravity\brain\7888f1f2-340c-488f-9289-16a6e3771c7a\fox_happy_1769882511778.png').convert('RGBA')
    data1 = np.array(img1)
    
    red, green, blue, alpha = data1[:,:,0], data1[:,:,1], data1[:,:,2], data1[:,:,3]
    white_areas = (red > 240) & (green > 240) & (blue > 240)
    data1[white_areas, 3] = 0
    
    result1 = Image.fromarray(data1)
    result1.save(r'static\images\fox_happy.png')
    print("✓ fox_happy.png processed")
except Exception as e:
    print(f"❌ Error processing fox_happy: {e}")

# Process fox_thinking.png
try:
    img2 = Image.open(r'C:\Users\shaik\.gemini\antigravity\brain\7888f1f2-340c-488f-9289-16a6e3771c7a\fox_thinking_1769882531001.png').convert('RGBA')
    data2 = np.array(img2)
    
    red, green, blue, alpha = data2[:,:,0], data2[:,:,1], data2[:,:,2], data2[:,:,3]
    white_areas = (red > 240) & (green > 240) & (blue > 240)
    data2[white_areas, 3] = 0
    
    result2 = Image.fromarray(data2)
    result2.save(r'static\images\fox_thinking.png')
    print("✓ fox_thinking.png processed")
except Exception as e:
    print(f"❌ Error processing fox_thinking: {e}")

print("\n✨ New mascot expressions ready!")
