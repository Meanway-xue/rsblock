import pygame
import random
import socket
import threading
import json
import sys
import time
import copy

# Constants for the game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Define tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# Define colors for shapes
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class SimpleTetrisBot:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.running = False
        self.thread = None
        self.opponent_grid = None
        
        # Adjust timings based on difficulty
        if difficulty == 'easy':
            self.move_delay = 1.5
            self.attack_chance = 0.3
            self.clear_chance = 0.1
        elif difficulty == 'medium':
            self.move_delay = 1.0
            self.attack_chance = 0.5
            self.clear_chance = 0.2
        else:  # hard
            self.move_delay = 0.5
            self.attack_chance = 0.7
            self.clear_chance = 0.3
    
    def start(self, opponent_grid, attack_callback):
        """Start the bot with references to game state"""
        self.opponent_grid = opponent_grid
        self.attack_callback = attack_callback
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        self.thread = None
    
    def _run(self):
        """Main bot loop"""
        while self.running:
            # Make a move
            if self.opponent_grid:
                self._make_move()
            
            # Wait before next move
            time.sleep(self.move_delay)
    
    def _make_move(self):
        """Make a move in the game"""
        # Randomly decide whether to clear lines
        if random.random() < self.clear_chance:
            # Clear a random line
            lines_cleared = random.randint(1, 2)
            
            # Add some completed lines
            for _ in range(lines_cleared):
                line_index = random.randint(GRID_HEIGHT - 5, GRID_HEIGHT - 1)
                self.opponent_grid[line_index] = [random.randint(1, 7) for _ in range(GRID_WIDTH)]
            
            # Then clear them
            for y in range(GRID_HEIGHT):
                if all(cell != 0 for cell in self.opponent_grid[y]):
                    self.opponent_grid.pop(y)
                    self.opponent_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            # Maybe attack player
            if random.random() < self.attack_chance:
                self.attack_callback(lines_cleared)

class Tetromino:
    def __init__(self, x, y, shape_idx=None):
        if shape_idx is None:
            self.shape_idx = random.randint(0, len(SHAPES) - 1)
        else:
            self.shape_idx = shape_idx
        self.shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.x = x
        self.y = y
        self.rotation = 0

    def rotate(self):
        # Create a new rotated shape
        rows, cols = len(self.shape), len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        return rotated

    def get_shape(self):
        return self.shape

    def get_positions(self):
        positions = []
        shape = self.shape
        for r in range(len(shape)):
            for c in range(len(shape[r])):
                if shape[r][c]:
                    positions.append((self.x + c, self.y + r))
        return positions

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 64)
        self.selected = 0
        self.options = ["Single Player", "Multiplayer", "Play vs. Bot", "Exit"]
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("TETRIS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 50))
            self.screen.blit(text, rect)
        
        pygame.display.flip()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "single"
                    elif self.selected == 1:
                        return "multiplayer"
                    elif self.selected == 2:
                        return "bot"
                    elif self.selected == 3:
                        return "exit"
        
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        while True:
            result = self.handle_input()
            if result:
                return result
            
            self.draw()
            clock.tick(60)

class BotDifficultyMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.selected = 0
        self.options = ["Easy", "Medium", "Hard", "Back"]
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("Select Bot Difficulty", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            color = GREEN if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 50))
            self.screen.blit(text, rect)
        
        pygame.display.flip()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "easy"
                    elif self.selected == 1:
                        return "medium"
                    elif self.selected == 2:
                        return "hard"
                    elif self.selected == 3:
                        return "back"
                elif event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        while True:
            result = self.handle_input()
            if result:
                return result
            
            self.draw()
            clock.tick(60)

class TetrisGame:
    def __init__(self, server_host='127.0.0.1', server_port=5555, game_mode="single"):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        # Game state
        self.player_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.opponent_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.game_over = False
        self.score = 0
        self.opponent_score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds per grid cell
        self.last_fall_time = time.time()
        self.player_name = "Player"
        self.opponent_name = "Opponent"
        self.game_mode = game_mode  # "single", "multiplayer", or "bot"
        
        # Bot player
        self.bot = None
        self.bot_difficulty = "medium"  # Can be "easy", "medium", or "hard"
        
        # High scores (for single player mode)
        self.high_scores = []
        
        # Network
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = server_host
        self.server_port = server_port
        self.connected = False
        self.player_id = None
        
        # Message queue
        self.message_queue = []
        self.lock = threading.Lock()
        
        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)

    def initialize_bot(self):
        """Initialize the bot player."""
        self.bot = SimpleTetrisBot(self.bot_difficulty)
        self.opponent_name = f"Bot ({self.bot_difficulty})"
        
        # Start bot in a separate thread
        self.bot.start(self.opponent_grid, self.add_junk_lines)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            self.connected = True
            print("Connected to server")
            
            # Start a thread to receive messages from the server
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Request player ID from server and specify game mode
            self.send_message({
                "type": "join", 
                "name": self.player_name,
                "mode": self.game_mode
            })
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_message(self, message):
        try:
            self.client_socket.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False

    def receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    print("Server disconnected")
                    self.connected = False
                    break
                
                message = json.loads(data.decode())
                
                with self.lock:
                    self.message_queue.append(message)
                    
            except Exception as e:
                print(f"Receive error: {e}")
                self.connected = False
                break

    def process_messages(self):
        with self.lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        
        for message in messages:
            message_type = message.get("type")
            
            if message_type == "player_id":
                self.player_id = message["id"]
                print(f"Assigned player ID: {self.player_id}")
            
            elif message_type == "game_start":
                self.opponent_name = message["opponent_name"]
                print(f"Game started against {self.opponent_name}")
            
            elif message_type == "opponent_update":
                self.opponent_grid = message["grid"]
                self.opponent_score = message["score"]
            
            elif message_type == "add_lines":
                if self.game_mode == "multiplayer":
                    num_lines = message["lines"]
                    self.add_junk_lines(num_lines)
                
            elif message_type == "game_over":
                winner = message.get("winner")
                if winner:
                    if winner == self.player_id:
                        print("You won!")
                    else:
                        print("You lost!")
            
            elif message_type == "high_scores":
                self.high_scores = message.get("scores", [])
                print("Received high scores from server")
                
    def add_junk_lines(self, num_lines):
        # Shift the grid up by num_lines
        for i in range(num_lines):
            # Remove the top line
            self.player_grid.pop(0)
            
            # Add a junk line at the bottom
            new_line = [0] * GRID_WIDTH
            # Fill the junk line with gray blocks, leaving one random gap
            gap = random.randint(0, GRID_WIDTH - 1)
            for j in range(GRID_WIDTH):
                if j != gap:
                    new_line[j] = 8  # 8 will represent gray blocks
            self.player_grid.append(new_line)
            
        # Check if the current piece overlaps with any blocks
        # If it does, move it up
        while self.check_collision():
            self.current_piece.y -= 1

    def check_collision(self):
        positions = self.current_piece.get_positions()
        for x, y in positions:
            if (x < 0 or x >= GRID_WIDTH or 
                y >= GRID_HEIGHT or 
                (y >= 0 and self.player_grid[y][x] != 0)):
                return True
        return False

    def rotate_piece(self):
        original_shape = self.current_piece.shape
        self.current_piece.shape = self.current_piece.rotate()
        
        # If rotation causes collision, revert
        if self.check_collision():
            self.current_piece.shape = original_shape

    def move_piece(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        # If move causes collision, revert
        if self.check_collision():
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        return True

    def drop_piece(self):
        while self.move_piece(0, 1):
            pass

    def lock_piece(self):
        positions = self.current_piece.get_positions()
        for x, y in positions:
            if y >= 0:  # Only lock if within the grid
                self.player_grid[y][x] = self.current_piece.shape_idx + 1
        
        # Check for lines to clear
        lines_cleared = self.clear_lines()
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * lines_cleared * 100 * self.level
            
            # In multiplayer mode, send cleared lines to opponent
            if self.game_mode == "multiplayer" and self.connected:
                self.send_message({
                    "type": "clear_lines",
                    "lines": lines_cleared
                })
            # In bot mode, send cleared lines to bot opponent
            elif self.game_mode == "bot" and lines_cleared > 0:
                # Add junk lines to bot's grid
                for i in range(lines_cleared):
                    # Remove bot's top line
                    self.opponent_grid.pop(0)
                    
                    # Add a junk line at the bottom
                    new_line = [0] * GRID_WIDTH
                    gap = random.randint(0, GRID_WIDTH - 1)
                    for j in range(GRID_WIDTH):
                        if j != gap:
                            new_line[j] = 8  # Gray blocks
                    self.opponent_grid.append(new_line)
                
                # Increase opponent score a bit anyway
                self.opponent_score += lines_cleared * 50
        
        # Update level
        self.level = max(1, self.lines_cleared // 10 + 1)
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
        
        # New piece
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        # Check game over
        if self.check_collision():
            self.game_over = True
            
            # Notify server of game over
            if self.connected:
                self.send_message({
                    "type": "game_over",
                    "score": self.score
                })
                
            # If in bot mode, stop the bot
            if self.game_mode == "bot" and self.bot:
                self.bot.stop()

    def clear_lines(self):
        lines_to_clear = []
        
        for i, row in enumerate(self.player_grid):
            if all(cell != 0 for cell in row):
                lines_to_clear.append(i)
        
        # Remove lines from bottom to top
        for line in reversed(lines_to_clear):
            self.player_grid.pop(line)
            self.player_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        return len(lines_to_clear)

    def draw_grid(self, grid, x_offset, y_offset, title):
        # Draw title
        title_text = self.title_font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(x_offset + GRID_WIDTH * GRID_SIZE // 2, y_offset - 30))
        self.screen.blit(title_text, title_rect)
        
        # Draw grid background
        pygame.draw.rect(self.screen, WHITE, 
                        (x_offset - 1, y_offset - 1, 
                         GRID_WIDTH * GRID_SIZE + 2, GRID_HEIGHT * GRID_SIZE + 2), 
                        1)
        
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_value = grid[y][x]
                if cell_value != 0:
                    if cell_value == 8:  # Gray junk blocks
                        color = GRAY
                    else:
                        color = SHAPE_COLORS[cell_value - 1]
                    pygame.draw.rect(self.screen, color, 
                                   (x_offset + x * GRID_SIZE, y_offset + y * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x_offset + x * GRID_SIZE, y_offset + y * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE), 
                                   1)

    def draw_piece(self, piece, x_offset, y_offset):
        shape = piece.get_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color, 
                                   (x_offset + (piece.x + x) * GRID_SIZE, 
                                    y_offset + (piece.y + y) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x_offset + (piece.x + x) * GRID_SIZE, 
                                    y_offset + (piece.y + y) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE), 
                                   1)

    def draw_next_piece(self, x_offset, y_offset):
        # Draw next piece box
        pygame.draw.rect(self.screen, WHITE, 
                        (x_offset, y_offset, 6 * GRID_SIZE, 6 * GRID_SIZE), 
                        1)
        
        # Draw next piece title
        next_text = self.font.render("Next Piece", True, WHITE)
        next_rect = next_text.get_rect(center=(x_offset + 3 * GRID_SIZE, y_offset - 15))
        self.screen.blit(next_text, next_rect)
        
        # Draw next piece
        shape = self.next_piece.get_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece.color, 
                                   (x_offset + (x + 1) * GRID_SIZE, 
                                    y_offset + (y + 1) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x_offset + (x + 1) * GRID_SIZE, 
                                    y_offset + (y + 1) * GRID_SIZE, 
                                    GRID_SIZE, GRID_SIZE), 
                                   1)

    def draw_stats(self, x_offset, y_offset):
        # Draw stats box
        pygame.draw.rect(self.screen, WHITE, 
                        (x_offset, y_offset, SIDEBAR_WIDTH, 200), 
                        1)
        
        # Draw stats
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (x_offset + 10, y_offset + 10))
        
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (x_offset + 10, y_offset + 40))
        
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (x_offset + 10, y_offset + 70))
        
        if self.game_mode == "multiplayer" or self.game_mode == "bot":
            opponent_text = self.font.render(f"Opponent: {self.opponent_name}", True, WHITE)
            self.screen.blit(opponent_text, (x_offset + 10, y_offset + 100))
            
            opponent_score_text = self.font.render(f"Opponent Score: {self.opponent_score}", True, WHITE)
            self.screen.blit(opponent_score_text, (x_offset + 10, y_offset + 130))

    def draw_high_scores(self, x_offset, y_offset):
        # Draw high scores box
        pygame.draw.rect(self.screen, WHITE, 
                        (x_offset, y_offset, SIDEBAR_WIDTH, 200), 
                        1)
        
        # Draw high scores title
        title_text = self.font.render("Leaderboard", True, WHITE)
        self.screen.blit(title_text, (x_offset + 10, y_offset + 10))
        
        # Draw high scores
        y_pos = y_offset + 40
        for i, (name, score) in enumerate(self.high_scores[:5]):
            score_text = self.font.render(f"{i+1}. {name}: {score}", True, WHITE)
            self.screen.blit(score_text, (x_offset + 10, y_pos))
            y_pos += 30

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_mode == "single":
            # Single player mode - centered grid
            grid_offset_x = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
            grid_offset_y = 50
            
            # Draw player grid
            self.draw_grid(self.player_grid, grid_offset_x, grid_offset_y, f"{self.player_name}")
            
            # Draw current piece
            self.draw_piece(self.current_piece, grid_offset_x, grid_offset_y)
            
            # Draw next piece
            self.draw_next_piece(grid_offset_x + GRID_WIDTH * GRID_SIZE + 20, grid_offset_y)
            
            # Draw stats
            self.draw_stats(grid_offset_x + GRID_WIDTH * GRID_SIZE + 20, grid_offset_y + 7 * GRID_SIZE)
            
            # Draw high scores
            if self.high_scores:
                self.draw_high_scores(grid_offset_x - SIDEBAR_WIDTH - 20, grid_offset_y)
        else:
            # Multiplayer or Bot mode - two grids side by side
            player_offset_x = 50
            opponent_offset_x = 450
            grid_offset_y = 50
            
            # Draw player grid
            self.draw_grid(self.player_grid, player_offset_x, grid_offset_y, f"{self.player_name}")
            
            # Draw current piece
            self.draw_piece(self.current_piece, player_offset_x, grid_offset_y)
            
            # Draw opponent grid
            self.draw_grid(self.opponent_grid, opponent_offset_x, grid_offset_y, f"{self.opponent_name}")
            
            # Draw next piece
            self.draw_next_piece(player_offset_x + GRID_WIDTH * GRID_SIZE + 20, grid_offset_y)
            
            # Draw stats
            self.draw_stats(player_offset_x + GRID_WIDTH * GRID_SIZE + 20, grid_offset_y + 7 * GRID_SIZE)
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.title_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)
            
            restart_text = self.font.render("Press R to restart or ESC to exit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.drop_piece()
                        self.lock_piece()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
        
        return True

    def reset_game(self):
        self.player_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.opponent_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.game_over = False
        self.score = 0
        self.opponent_score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.last_fall_time = time.time()
        
        # If in bot mode, reinitialize the bot
        if self.game_mode == "bot":
            if self.bot:
                self.bot.stop()
            self.initialize_bot()
        
        # If in multiplayer mode, need to reconnect and find a new opponent
        if self.game_mode == "multiplayer" and self.connected:
            self.send_message({
                "type": "ready_for_new_game"
            })