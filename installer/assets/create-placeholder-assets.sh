#!/bin/bash

# Create placeholder assets for ProductivityFlow Installer
echo "🎨 Creating placeholder assets..."

# Create a simple background image using sips (macOS built-in tool)
# This creates a 800x600 gradient background
cat > background.png.py << 'EOF'
from PIL import Image, ImageDraw
import os

# Create a gradient background
width, height = 800, 600
image = Image.new('RGB', (width, height), color='#f0f0f0')
draw = ImageDraw.Draw(image)

# Create a subtle gradient
for y in range(height):
    alpha = int(255 * (1 - y / height * 0.3))
    color = (240, 240, 240 - int(y / height * 40))
    draw.line([(0, y), (width, y)], fill=color)

# Add ProductivityFlow branding
from PIL import ImageFont
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
except:
    font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Draw title
title = "ProductivityFlow"
subtitle = "Choose your productivity tools"

# Get text size and center it
bbox = draw.textbbox((0, 0), title, font=font)
title_width = bbox[2] - bbox[0]
title_height = bbox[3] - bbox[1]

draw.text(((width - title_width) // 2, height // 2 - 100), title, 
          fill='#333333', font=font)

bbox = draw.textbbox((0, 0), subtitle, font=small_font)
subtitle_width = bbox[2] - bbox[0]
draw.text(((width - subtitle_width) // 2, height // 2 - 40), subtitle, 
          fill='#666666', font=small_font)

image.save('background.png')
print("Background image created: background.png")
EOF

# Run the Python script if PIL is available
if python3 -c "import PIL" 2>/dev/null; then
    python3 background.png.py
    rm background.png.py
else
    echo "⚠️  PIL not available, creating simple background..."
    # Create a simple colored rectangle as fallback
    cat > simple_bg.applescript << 'EOF'
tell application "Image Events"
    launch
    set bg to make new image with properties {dimensions:{800, 600}, color:{240, 240, 240}}
    save bg as PNG in POSIX file "$PWD/background.png"
end tell
EOF
    osascript simple_bg.applescript 2>/dev/null || echo "Background creation skipped - will use default"
    rm -f simple_bg.applescript
fi

# Create a simple icon using built-in tools
echo "📱 Creating installer icon..."

# Create icon using SF Symbols or fallback to simple colored square
cat > create_icon.py << 'EOF'
from PIL import Image, ImageDraw
import os

# Create app icon (512x512 for high resolution)
size = 512
image = Image.new('RGBA', (size, size), color=(70, 130, 180, 255))
draw = ImageDraw.Draw(image)

# Draw a simple productivity-themed icon
# Background circle
circle_margin = 50
draw.ellipse([circle_margin, circle_margin, size-circle_margin, size-circle_margin], 
             fill=(70, 130, 180, 255), outline=(50, 110, 160, 255), width=8)

# Draw gear/productivity symbol
center = size // 2
gear_size = 80
gear_color = (255, 255, 255, 255)

# Simple gear representation
for i in range(8):
    angle = i * 45
    import math
    x1 = center + (gear_size // 2) * math.cos(math.radians(angle))
    y1 = center + (gear_size // 2) * math.sin(math.radians(angle))
    x2 = center + gear_size * math.cos(math.radians(angle))
    y2 = center + gear_size * math.sin(math.radians(angle))
    draw.line([(x1, y1), (x2, y2)], fill=gear_color, width=12)

# Inner circle
draw.ellipse([center-30, center-30, center+30, center+30], 
             fill=gear_color, outline=(200, 200, 200, 255), width=4)

# Save different sizes
image.save('installer-icon.png')

# Create .icns file structure (simplified)
os.makedirs('installer-icon.iconset', exist_ok=True)

# Generate different sizes
sizes = [16, 32, 128, 256, 512]
for s in sizes:
    resized = image.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(f'installer-icon.iconset/icon_{s}x{s}.png')
    
    # Create @2x versions
    if s < 512:
        resized_2x = image.resize((s*2, s*2), Image.Resampling.LANCZOS)
        resized_2x.save(f'installer-icon.iconset/icon_{s}x{s}@2x.png')

print("Icon files created")
EOF

if python3 -c "import PIL" 2>/dev/null; then
    python3 create_icon.py
    
    # Convert to .icns if iconutil is available
    if command -v iconutil &> /dev/null; then
        iconutil -c icns installer-icon.iconset
        echo "✅ installer-icon.icns created"
    else
        echo "⚠️  iconutil not available, using PNG icon"
        cp installer-icon.png installer-icon.icns
    fi
    
    # Also create volume icon
    cp installer-icon.icns volume-icon.icns
    
    rm -rf installer-icon.iconset
    rm create_icon.py
else
    echo "⚠️  PIL not available, skipping icon creation"
    # Create empty placeholder files
    touch installer-icon.icns
    touch volume-icon.icns
fi

echo "✅ Placeholder assets created successfully!"
echo "📁 Files created:"
echo "   - background.png (DMG background)"
echo "   - installer-icon.icns (App icon)"
echo "   - volume-icon.icns (DMG volume icon)"
echo ""
echo "💡 You can replace these with custom-designed assets for better branding."