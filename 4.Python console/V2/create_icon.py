# -*- coding: utf-8 -*-
"""
创建简单的 ECG 图标
用于打包时的应用程序图标
"""

try:
    from PIL import Image, ImageDraw
    
    # 创建 256x256 的图像
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制心电图波形
    points = []
    margin = 40
    
    # 基线
    base_y = size // 2
    
    # 绘制典型的心电图波形 (P-QRS-T 波群)
    x_step = (size - 2 * margin) // 20
    
    for i in range(20):
        x = margin + i * x_step
        
        # 模拟 P-QRS-T 波形
        if i == 5:  # P 波
            y = base_y - 20
        elif i == 8:  # Q 波
            y = base_y + 15
        elif i == 9:  # R 波
            y = base_y - 60
        elif i == 10:  # S 波
            y = base_y + 15
        elif i == 14:  # T 波
            y = base_y - 30
        else:
            y = base_y
        
        points.append((x, y))
    
    # 绘制波形 (红色)
    draw.line(points, fill=(255, 107, 107, 255), width=4)
    
    # 绘制背景网格
    grid_color = (61, 61, 92, 128)
    grid_spacing = 32
    
    for x in range(margin, size - margin + 1, grid_spacing):
        draw.line([(x, margin), (x, size - margin)], fill=grid_color, width=1)
    
    for y in range(margin, size - margin + 1, grid_spacing):
        draw.line([(margin, y), (size - margin, y)], fill=grid_color, width=1)
    
    # 保存为 ICO 格式 (多尺寸)
    sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    
    # 调整大小并保存
    img.save('resources/icons/ecg.ico', format='ICO', sizes=sizes)
    
    print("图标创建成功：resources/icons/ecg.ico")
    
except ImportError:
    print("错误：需要安装 Pillow 库")
    print("运行：pip install pillow")
    
    # 创建一个空的占位文件
    with open('resources/icons/ecg.ico', 'wb') as f:
        # 写入一个简单的 ICO 文件头 (最小有效 ICO)
        f.write(b'\x00\x00\x01\x00\x01\x00\x20\x20\x00\x00\x01\x00\x20\x00')
        f.write(b'\x68\x04\x00\x00\x16\x00\x00\x00')
    print("已创建占位图标文件")
