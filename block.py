import pygame
import random
import time

# 初始化Pygame
pygame.init()

# 游戏窗口设置
cols = 10
rows = 20
block_size = 30
width = cols * block_size
height = rows * block_size
# 增加侧边预览区宽度
sidebar_width = 150
screen = pygame.display.set_mode((width + sidebar_width, height))
pygame.display.set_caption("Tetris")

# 方块颜色定义 (主色，亮色，暗色)
colors = [
    [(0, 0, 0), (30, 30, 30), (0, 0, 0)],          # 黑色背景
    [(0, 240, 240), (120, 255, 255), (0, 160, 160)], # I型 - 青色
    [(240, 240, 0), (255, 255, 120), (160, 160, 0)], # O型 - 黄色
    [(160, 0, 240), (210, 120, 255), (100, 0, 160)], # T型 - 紫色
    [(0, 240, 0), (120, 255, 120), (0, 160, 0)],     # S型 - 绿色
    [(240, 0, 0), (255, 120, 120), (160, 0, 0)],     # Z型 - 红色
    [(0, 0, 240), (120, 120, 255), (0, 0, 160)],     # J型 - 蓝色
    [(240, 160, 0), (255, 200, 120), (160, 100, 0)]  # L型 - 橙色
]

# 修正方块形状定义（所有形状都具有相同的数据结构）
# 每种方块有4种不同的旋转状态
shapes = [
    # I型
    [[[0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0],
      [0, 0, 0, 0]],
     [[0, 0, 1, 0],
      [0, 0, 1, 0],
      [0, 0, 1, 0],
      [0, 0, 1, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0]],
     [[0, 1, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0]]],
    
    # O型
    [[[0, 0, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]]],
    
    # T型
    [[[0, 0, 0, 0],
      [0, 1, 0, 0],
      [1, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 0, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 1, 1, 0],
      [0, 1, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 0, 0]]],
    
    # S型
    [[[0, 0, 0, 0],
      [0, 1, 1, 0],
      [1, 1, 0, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 1, 0],
      [0, 0, 1, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [0, 1, 1, 0],
      [1, 1, 0, 0]],
     [[0, 0, 0, 0],
      [1, 0, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 0, 0]]],
    
    # Z型
    [[[0, 0, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 0, 1, 0],
      [0, 1, 1, 0],
      [0, 1, 0, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 1, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [1, 1, 0, 0],
      [1, 0, 0, 0]]],
    
    # J型
    [[[0, 0, 0, 0],
      [1, 0, 0, 0],
      [1, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 1, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 1, 1, 0],
      [0, 0, 1, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0],
      [1, 1, 0, 0]]],
    
    # L型
    [[[0, 0, 0, 0],
      [0, 0, 1, 0],
      [1, 1, 1, 0],
      [0, 0, 0, 0]],
     [[0, 0, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 1, 0]],
     [[0, 0, 0, 0],
      [0, 0, 0, 0],
      [1, 1, 1, 0],
      [1, 0, 0, 0]],
     [[0, 0, 0, 0],
      [1, 1, 0, 0],
      [0, 1, 0, 0],
      [0, 1, 0, 0]]]
]

# 游戏板类
class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        
    def draw(self):
        # 绘制游戏主区域
        for y in range(rows):
            for x in range(cols):
                if self.grid[y][x] != 0:
                    # 获取颜色元组
                    color_main = colors[self.grid[y][x]][0]
                    color_light = colors[self.grid[y][x]][1]
                    color_dark = colors[self.grid[y][x]][2]
                    
                    # 绘制主体
                    pygame.draw.rect(screen, 
                                    color_main, 
                                    (x*block_size, y*block_size,
                                     block_size, block_size))
                    
                    # 绘制高光（上方和左方）
                    pygame.draw.polygon(screen, 
                                        color_light,
                                        [(x*block_size, y*block_size),
                                         ((x+1)*block_size-2, y*block_size),
                                         ((x+1)*block_size-2, (y+1)*block_size-2),
                                         (x*block_size, (y+1)*block_size-2)])
                    
                    # 绘制阴影（右方和下方）
                    pygame.draw.polygon(screen, 
                                        color_dark,
                                        [((x+1)*block_size, y*block_size),
                                         ((x+1)*block_size, (y+1)*block_size),
                                         (x*block_size+2, (y+1)*block_size),
                                         (x*block_size+2, y*block_size+2)])
                    
                    # 绘制内部亮点
                    pygame.draw.rect(screen, 
                                    color_light, 
                                    (x*block_size + 4, y*block_size + 4,
                                     block_size // 3, block_size // 3))
                else:
                    # 绘制空格子 (深色背景上有细微网格)
                    pygame.draw.rect(screen, 
                                    (20, 20, 20), 
                                    (x*block_size, y*block_size,
                                     block_size, block_size))
                    # 绘制网格线
                    pygame.draw.rect(screen, 
                                    (40, 40, 40), 
                                    (x*block_size, y*block_size,
                                     block_size, block_size),
                                    1)

        # 绘制游戏区域右侧边界线
        pygame.draw.line(screen, (128, 128, 128), 
                         (width, 0), (width, height), 2)
        
    def is_collision(self, piece):
        for y in range(4):
            for x in range(4):
                if piece.shape[piece.rotation][y][x]:
                    pos_x = piece.x + x
                    pos_y = piece.y + y
                    
                    # 检查是否超出边界或与已有方块碰撞
                    if (pos_x < 0 or pos_x >= cols or 
                        pos_y >= rows or 
                        (pos_y >= 0 and self.grid[pos_y][pos_x])):
                        return True
        return False

    def lock_piece(self, piece):
        for y in range(4):
            for x in range(4):
                if piece.shape[piece.rotation][y][x]:
                    pos_x = piece.x + x
                    pos_y = piece.y + y
                    if pos_y >= 0:  # 确保不会在屏幕外尝试锁定
                        self.grid[pos_y][pos_x] = piece.color_id

    def clear_lines(self):
        lines_cleared = 0
        y = rows - 1
        while y >= 0:
            # 检查是否填满一行
            if all(self.grid[y][x] != 0 for x in range(cols)):
                lines_cleared += 1
                
                # 将上面的所有行下移
                for y2 in range(y, 0, -1):
                    for x in range(cols):
                        self.grid[y2][x] = self.grid[y2-1][x]
                
                # 清空顶行
                for x in range(cols):
                    self.grid[0][x] = 0
            else:
                y -= 1
                
        return lines_cleared

# 方块类
class Piece:
    def __init__(self):
        self.color_id = random.randint(1, 7)
        self.shape = shapes[self.color_id-1]
        self.rotation = 0  # 初始旋转状态
        self.x = cols//2 - 2  # 居中出现
        self.y = -1  # 从顶部稍微露出来开始
        
    # 方向控制
    def move_left(self, board):
        self.x -= 1
        if board.is_collision(self):
            self.x += 1
            return False
        return True

    def move_right(self, board):
        self.x += 1
        if board.is_collision(self):
            self.x -= 1
            return False
        return True
        
    def move_down(self, board):
        self.y += 1
        if board.is_collision(self):
            self.y -= 1
            return False
        return True

    def rotate(self, board):
        original_rotation = self.rotation
        self.rotation = (self.rotation + 1) % 4
        
        # 如果旋转后发生碰撞，尝试偏移位置
        if board.is_collision(self):
            # 尝试左移
            self.x -= 1
            if not board.is_collision(self):
                return True
                
            # 恢复并尝试右移
            self.x += 1
            self.x += 1
            if not board.is_collision(self):
                return True
                
            # 恢复并尝试上移（对于I型和其他长条状方块）
            self.x -= 1
            self.y -= 1
            if not board.is_collision(self):
                return True
                
            # 都不行就恢复原状
            self.y += 1
            self.rotation = original_rotation
            return False
            
        return True

    def draw(self, x_offset=0, y_offset=0):
        for y in range(4):
            for x in range(4):
                if self.shape[self.rotation][y][x]:
                    # 计算位置
                    rect_x = (self.x + x) * block_size + x_offset
                    rect_y = (self.y + y) * block_size + y_offset
                    
                    # 获取颜色元组
                    color_main = colors[self.color_id][0]
                    color_light = colors[self.color_id][1]
                    color_dark = colors[self.color_id][2]
                    
                    # 绘制主体
                    pygame.draw.rect(screen, 
                                     color_main, 
                                     (rect_x, rect_y,
                                      block_size, block_size))
                    
                    # 绘制高光（上方和左方）
                    pygame.draw.polygon(screen, 
                                        color_light,
                                        [(rect_x, rect_y),
                                         (rect_x+block_size-2, rect_y),
                                         (rect_x+block_size-2, rect_y+block_size-2),
                                         (rect_x, rect_y+block_size-2)])
                    
                    # 绘制阴影（右方和下方）
                    pygame.draw.polygon(screen, 
                                        color_dark,
                                        [(rect_x+block_size, rect_y),
                                         (rect_x+block_size, rect_y+block_size),
                                         (rect_x+2, rect_y+block_size),
                                         (rect_x+2, rect_y+2)])
                    
                    # 绘制内部亮点
                    pygame.draw.rect(screen, 
                                     color_light, 
                                     (rect_x + 4, rect_y + 4,
                                      block_size // 3, block_size // 3))
    
    def draw_ghost(self, board):
        """绘制方块落地位置的虚线框"""
        # 创建一个副本来计算落地位置
        ghost_y = self.y
        
        # 将副本一直向下移动直到碰撞
        while True:
            ghost_y += 1
            # 检查是否碰撞
            if self._check_collision_at_position(board, self.x, ghost_y):
                ghost_y -= 1  # 回退一步，得到最终位置
                break
        
        # 绘制虚线框
        for y in range(4):
            for x in range(4):
                if self.shape[self.rotation][y][x]:
                    rect_x = (self.x + x) * block_size
                    rect_y = (ghost_y + y) * block_size
                    
                    # 计算幽灵方块的颜色
                    color_main = colors[self.color_id][0]
                    # 创建一个更明显的颜色
                    ghost_color = (min(color_main[0]+50, 255), 
                                   min(color_main[1]+50, 255), 
                                   min(color_main[2]+50, 255))
                    
                    # 内缩值，使幽灵方块小一些但仍然明显
                    s = 3
                    
                    # 先绘制一个实心的半透明块作为背景
                    ghost_surface = pygame.Surface((block_size-2*s, block_size-2*s))
                    ghost_surface.set_alpha(50)  # 设置透明度
                    ghost_surface.fill(ghost_color)
                    screen.blit(ghost_surface, (rect_x+s, rect_y+s))
                    
                    # 绘制灰色外框，不再使用刺眼的白色
                    pygame.draw.rect(screen, 
                                    (180, 180, 180), 
                                    (rect_x+s, rect_y+s, block_size-2*s, block_size-2*s), 
                                    2)  # 线宽为2
                    
                    # 绘制内部彩色线条
                    pygame.draw.rect(screen, 
                                    ghost_color, 
                                    (rect_x+s+2, rect_y+s+2, block_size-2*s-4, block_size-2*s-4), 
                                    1)  # 线宽为1
                    
                    # 绘制角落标记，使用灰色而不是白色
                    corner_size = 4
                    corner_color = (160, 160, 160)  # 适中的灰色，不太刺眼
                    # 左上角
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+s, rect_y+s), 
                                    (rect_x+s+corner_size, rect_y+s), 2)
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+s, rect_y+s), 
                                    (rect_x+s, rect_y+s+corner_size), 2)
                    # 右上角
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+block_size-s, rect_y+s), 
                                    (rect_x+block_size-s-corner_size, rect_y+s), 2)
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+block_size-s, rect_y+s), 
                                    (rect_x+block_size-s, rect_y+s+corner_size), 2)
                    # 左下角
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+s, rect_y+block_size-s), 
                                    (rect_x+s+corner_size, rect_y+block_size-s), 2)
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+s, rect_y+block_size-s), 
                                    (rect_x+s, rect_y+block_size-s-corner_size), 2)
                    # 右下角
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+block_size-s, rect_y+block_size-s), 
                                    (rect_x+block_size-s-corner_size, rect_y+block_size-s), 2)
                    pygame.draw.line(screen, corner_color, 
                                    (rect_x+block_size-s, rect_y+block_size-s), 
                                    (rect_x+block_size-s, rect_y+block_size-s-corner_size), 2)
    
    def _check_collision_at_position(self, board, test_x, test_y):
        """检查在特定位置是否会发生碰撞"""
        for y in range(4):
            for x in range(4):
                if self.shape[self.rotation][y][x]:
                    pos_x = test_x + x
                    pos_y = test_y + y
                    
                    # 检查是否超出边界或与已有方块碰撞
                    if (pos_x < 0 or pos_x >= cols or 
                        pos_y >= rows or 
                        (pos_y >= 0 and board.grid[pos_y][pos_x])):
                        return True
        return False
                     
    def draw_preview(self, x, y):
        # 绘制预览区块
        preview_block_size = block_size - 5  # 稍小一些的方块尺寸
        for row in range(4):
            for col in range(4):
                if self.shape[self.rotation][row][col]:
                    rect_x = x + col * preview_block_size
                    rect_y = y + row * preview_block_size
                    
                    # 获取颜色元组
                    color_main = colors[self.color_id][0]
                    color_light = colors[self.color_id][1]
                    color_dark = colors[self.color_id][2]
                    
                    # 绘制主体
                    pygame.draw.rect(screen, 
                                     color_main, 
                                     (rect_x, rect_y,
                                      preview_block_size, preview_block_size))
                    
                    # 绘制高光（上方和左方）- 简化版
                    pygame.draw.line(screen, color_light, 
                                     (rect_x, rect_y), 
                                     (rect_x+preview_block_size-2, rect_y), 2)
                    pygame.draw.line(screen, color_light, 
                                     (rect_x, rect_y), 
                                     (rect_x, rect_y+preview_block_size-2), 2)
                    
                    # 绘制阴影（右方和下方）- 简化版
                    pygame.draw.line(screen, color_dark, 
                                     (rect_x+preview_block_size, rect_y), 
                                     (rect_x+preview_block_size, rect_y+preview_block_size), 2)
                    pygame.draw.line(screen, color_dark, 
                                     (rect_x, rect_y+preview_block_size), 
                                     (rect_x+preview_block_size, rect_y+preview_block_size), 2)

# 游戏核心逻辑
def game_loop():
    board = Board()
    current_piece = Piece()
    next_piece = Piece()
    
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 500   # 初始下落速度（毫秒）
    score = 0
    level = 1
    lines_cleared = 0   # 记录总共消除的行数
    paused = False
    
    running = True
    game_over = False
    
    # 创建背景网格纹理
    background = pygame.Surface((width, height))
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            color = (15, 15, 15) if (x//block_size + y//block_size) % 2 == 0 else (25, 25, 25)
            pygame.draw.rect(background, color, (x, y, block_size, block_size))
    
    # 尝试使用系统默认字体，更好地支持中文
    try:
        font_small = pygame.font.Font(None, 24)  # 使用默认字体
        font_big = pygame.font.Font(None, 48)    # 使用默认字体
    except:
        # 如果默认字体不可用，回退到SysFont
        font_small = pygame.font.SysFont(None, 24)
        font_big = pygame.font.SysFont(None, 48)
    
    while running:
        dt = clock.tick(60)
        fall_time += dt
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # 键盘控制
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN:
                        # 重新开始游戏
                        board = Board()
                        current_piece = Piece()
                        next_piece = Piece()
                        fall_time = 0
                        score = 0
                        level = 1
                        fall_speed = 500
                        game_over = False
                else:
                    if event.key == pygame.K_LEFT:
                        current_piece.move_left(board)
                    elif event.key == pygame.K_RIGHT:
                        current_piece.move_right(board)
                    elif event.key == pygame.K_DOWN:
                        # 下箭头改为立即落到底部（与空格键相同功能）
                        while current_piece.move_down(board):
                            pass
                        board.lock_piece(current_piece)
                        lines = board.clear_lines()
                        # 使用新的得分规则
                        if lines == 1:
                            score += 10
                        elif lines == 2:
                            score += 30
                        elif lines == 3:
                            score += 60
                        elif lines == 4:
                            score += 100
                            
                        # 满300分升级，最高10级
                        old_level = level
                        level = min(score // 300 + 1, 10)
                        
                        # 如果升级了，调整下落速度
                        if level > old_level:
                            # 每升一级提高5%的自然下落速度
                            fall_speed = int(500 * (0.95 ** (level - 1)))
                        
                        current_piece = next_piece
                        next_piece = Piece()
                        
                        if board.is_collision(current_piece):
                            game_over = True
                    elif event.key == pygame.K_UP:
                        current_piece.rotate(board)
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_SPACE:
                        # 硬降落（直接落到底部）
                        while current_piece.move_down(board):
                            pass
                        board.lock_piece(current_piece)
                        lines = board.clear_lines()
                        # 使用新的得分规则
                        if lines == 1:
                            score += 10
                        elif lines == 2:
                            score += 30
                        elif lines == 3:
                            score += 60
                        elif lines == 4:
                            score += 100
                            
                        # 满300分升级
                        old_level = level
                        level = score // 300 + 1
                        
                        # 如果升级了，调整下落速度
                        if level > old_level:
                            # 每升一级提高5%的自然下落速度
                            fall_speed = int(500 * (0.95 ** (level - 1)))
                        
                        current_piece = next_piece
                        next_piece = Piece()
                        
                        if board.is_collision(current_piece):
                            game_over = True
        
        # 如果暂停或游戏结束，跳过游戏逻辑更新
        if paused or game_over:
            # 填充黑色背景
            screen.fill((0, 0, 0))
            
            # 绘制游戏板
            board.draw()
            
            # 绘制侧边栏
            draw_sidebar(score, level, next_piece)
            
            if paused:
                # 半透明暂停覆盖层
                pause_overlay = pygame.Surface((width, height))
                pause_overlay.set_alpha(150)
                pause_overlay.fill((0, 0, 0))
                screen.blit(pause_overlay, (0, 0))
                
                # 绘制暂停菜单背景
                pause_rect = (width//2-100, height//2-70, 200, 140)
                pygame.draw.rect(screen, (60, 60, 80), pause_rect)
                pygame.draw.rect(screen, (100, 100, 150), pause_rect, 3)
                
                pause_text = font_big.render("PAUSED", True, (255, 255, 255))
                screen.blit(pause_text, (width//2 - pause_text.get_width()//2, height//2 - 40))
                instruction = font_small.render("Press P to continue", True, (220, 220, 220))
                screen.blit(instruction, (width//2 - instruction.get_width()//2, height//2 + 20))
            
            if game_over:
                # 半透明游戏结束覆盖层
                game_over_overlay = pygame.Surface((width, height))
                game_over_overlay.set_alpha(180)
                game_over_overlay.fill((20, 0, 0))
                screen.blit(game_over_overlay, (0, 0))
                
                # 绘制游戏结束菜单背景
                gameover_rect = (width//2-120, height//2-100, 240, 200)
                pygame.draw.rect(screen, (60, 30, 30), gameover_rect)
                pygame.draw.rect(screen, (150, 50, 50), gameover_rect, 3)
                
                game_over_text = font_big.render("GAME OVER", True, (255, 200, 200))
                screen.blit(game_over_text, (width//2 - game_over_text.get_width()//2, height//2 - 70))
                
                score_text = font_big.render(f"SCORE: {score}", True, (255, 255, 200))
                screen.blit(score_text, (width//2 - score_text.get_width()//2, height//2 - 10))
                
                restart_text = font_small.render("Press ENTER to restart", True, (220, 220, 220))
                screen.blit(restart_text, (width//2 - restart_text.get_width()//2, height//2 + 50))
                
            pygame.display.update()
            continue
            
        # 自动下落逻辑
        if fall_time > fall_speed:
            if not current_piece.move_down(board):
                board.lock_piece(current_piece)
                
                lines = board.clear_lines()
                # 使用新的得分规则
                if lines == 1:
                    score += 10
                elif lines == 2:
                    score += 30
                elif lines == 3:
                    score += 60
                elif lines == 4:
                    score += 100
                    
                # 满300分升级，最高10级
                old_level = level
                level = min(score // 300 + 1, 10)
                
                # 如果升级了，调整下落速度
                if level > old_level:
                    # 每升一级提高5%的自然下落速度
                    fall_speed = int(500 * (0.95 ** (level - 1)))
                
                current_piece = next_piece
                next_piece = Piece()
                
                # 检查游戏是否结束
                if board.is_collision(current_piece):
                    game_over = True
                    
            fall_time = 0
        
        # 填充黑色背景
        screen.fill((0, 0, 0))
        # 绘制背景纹理
        screen.blit(background, (0, 0))
        
        # 绘制游戏板
        board.draw()
        
        # 绘制当前方块的落地位置预测（虚线框）
        current_piece.draw_ghost(board)
        
        # 绘制当前方块
        current_piece.draw()
        
        # 绘制侧边栏
        draw_sidebar(score, level, next_piece)
        
        pygame.display.update()
    
    pygame.quit()

def draw_sidebar(score, level, next_piece):
    # 绘制侧边栏背景
    pygame.draw.rect(screen, (30, 30, 30), 
                    (width, 0, sidebar_width, height))
    
    # 使用默认字体，更好地支持中文
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont(None, 24)
    
    # 绘制下一个方块文本 - 使用英文避免中文显示问题
    next_text = font.render("NEXT:", True, (255, 255, 255))
    screen.blit(next_text, (width + 10, 20))
    
    # 绘制下一个方块预览
    next_piece.draw_preview(width + 20, 50)
    
    # 绘制分数 - 使用英文避免中文显示问题
    score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
    screen.blit(score_text, (width + 10, height//2))
    
    # 绘制等级 - 使用英文避免中文显示问题
    level_text = font.render(f"LEVEL: {level}", True, (255, 255, 255))
    screen.blit(level_text, (width + 10, height//2 + 30))
    
    # 显示下一级所需分数
    next_level_score = level * 300
    next_level_text = font.render(f"NEXT LVL: {next_level_score}", True, (255, 255, 255))
    screen.blit(next_level_text, (width + 10, height//2 + 60))
    
    # 绘制操作说明 - 使用英文避免中文显示问题
    controls_y = height//2 + 80
    controls = [
        "LEFT/RIGHT: Move",
        "UP: Rotate",
        "DOWN: Drop",
        "SPACE: Drop",
        "P: Pause/Resume"
    ]
    
    for i, control in enumerate(controls):
        ctrl_text = font.render(control, True, (200, 200, 200))
        screen.blit(ctrl_text, (width + 10, controls_y + i*25))

if __name__ == "__main__":
    game_loop()