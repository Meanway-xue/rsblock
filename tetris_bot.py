import random
import time
import copy
import threading

class TetrisBot:
    def __init__(self, difficulty='medium'):
        """
        Initialize a Tetris bot with a specific difficulty level.
        
        Args:
            difficulty (str): 'easy', 'medium', or 'hard' to determine bot skill
        """
        self.difficulty = difficulty
        self.grid = [[0 for _ in range(10)] for _ in range(20)]  # Standard 10x20 grid
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.running = False
        self.bot_thread = None
        
        # Difficulty settings
        self.settings = {
            'easy': {
                'move_delay': 0.5,  # Slower moves
                'think_delay': 0.3,  # Longer thinking time
                'error_rate': 0.3,   # 30% chance of suboptimal move
                'look_ahead': False  # Doesn't consider next piece
            },
            'medium': {
                'move_delay': 0.3,
                'think_delay': 0.2,
                'error_rate': 0.15,
                'look_ahead': True   # Considers next piece
            },
            'hard': {
                'move_delay': 0.1,   # Fast moves
                'think_delay': 0.1,  # Quick thinking
                'error_rate': 0.05,  # Rarely makes mistakes
                'look_ahead': True   # Considers next piece
            }
        }
        
        # Heuristic weights for evaluating moves
        self.weights = {
            'height': -4.5,         # Maximum height penalty
            'holes': -7.5,          # Holes penalty
            'bumpiness': -2.0,      # Surface roughness penalty
            'complete_lines': 5.0,  # Complete lines reward
            'edge_touch': 0.5,      # Reward for pieces touching edges
            'well_depth': -4.0,     # Penalty for deep wells
            'overhang': -3.0        # Penalty for overhangs
        }
        
        # Adjust weights based on difficulty
        if difficulty == 'easy':
            self.weights['height'] = -3.0
            self.weights['holes'] = -4.0
            self.weights['complete_lines'] = 10.0  # Prioritizes line clearing
        elif difficulty == 'hard':
            self.weights['height'] = -6.0
            self.weights['holes'] = -10.0
            self.weights['bumpiness'] = -3.0
            self.weights['well_depth'] = -5.0
    
    def set_grid(self, grid):
        """Set the current grid state from external source."""
        self.grid = copy.deepcopy(grid)
    
    def set_pieces(self, current_piece, next_piece):
        """Set the current and next pieces from external source."""
        self.current_piece = current_piece
        self.next_piece = next_piece
    
    def start(self):
        """Start the bot in a separate thread."""
        if not self.running:
            self.running = True
            self.bot_thread = threading.Thread(target=self.run)
            self.bot_thread.daemon = True
            self.bot_thread.start()
    
    def stop(self):
        """Stop the bot thread."""
        self.running = False
        if self.bot_thread:
            self.bot_thread = None
    
    def run(self):
        """Main bot loop - continuously decides and makes moves."""
        while self.running:
            if self.current_piece:
                # Decide on the best move
                best_move = self.find_best_move()
                
                # Execute the move
                if best_move:
                    rotations, position = best_move
                    # Apply bot's moves with a delay to make it feel more natural
                    self.execute_move(rotations, position)
            
            # Small delay between moves
            time.sleep(self.settings[self.difficulty]['move_delay'])
    
    def execute_move(self, rotations, position):
        """
        Simulate execution of moves, but in reality return the moves for the game to execute.
        
        Returns:
            dict: A message containing the bot's moves
        """
        # This is a placeholder - actual movement execution will be handled by the game
        moves = {
            'type': 'bot_move',
            'rotations': rotations,
            'position': position,
            'drop': True  # Always drop after positioning
        }
        return moves
    
    def find_best_move(self):
        """
        Find the best move (rotation and position) for the current piece.
        
        Returns:
            tuple: (rotations, x_position) for the best move
        """
        if not self.current_piece:
            return None
        
        # Add a thinking delay based on difficulty
        time.sleep(self.settings[self.difficulty]['think_delay'])
        
        # Get all possible moves
        possible_moves = self.get_possible_moves()
        
        if not possible_moves:
            return None
        
        # For easy difficulty, sometimes make suboptimal moves
        if random.random() < self.settings[self.difficulty]['error_rate']:
            return random.choice(possible_moves)
        
        best_score = float('-inf')
        best_moves = []
        
        for move in possible_moves:
            rotations, position = move
            
            # Create a copy of the grid to simulate the move
            test_grid = copy.deepcopy(self.grid)
            
            # Simulate placing the piece with these rotations and position
            test_piece = copy.deepcopy(self.current_piece)
            
            # Apply rotations
            for _ in range(rotations):
                test_piece.shape = self.rotate_shape(test_piece.shape)
            
            # Set position
            test_piece.x = position
            
            # Drop the piece to find its final position
            test_piece.y = 0
            while not self.check_collision(test_grid, test_piece, 0, 1):
                test_piece.y += 1
            
            # Place the piece on the test grid
            self.place_piece(test_grid, test_piece)
            
            # Clear any completed lines
            lines_cleared = self.clear_lines(test_grid)
            
            # Calculate score for this move
            move_score = self.evaluate_position(test_grid, lines_cleared)
            
            # If we're considering the next piece too (look-ahead)
            if self.settings[self.difficulty]['look_ahead'] and self.next_piece:
                # For each possible placement of the next piece
                next_piece_moves = self.get_possible_moves_for_piece(test_grid, self.next_piece)
                best_next_score = float('-inf')
                
                for next_move in next_piece_moves:
                    next_rotations, next_position = next_move
                    
                    # Create another test grid
                    next_test_grid = copy.deepcopy(test_grid)
                    next_test_piece = copy.deepcopy(self.next_piece)
                    
                    # Apply rotations
                    for _ in range(next_rotations):
                        next_test_piece.shape = self.rotate_shape(next_test_piece.shape)
                    
                    # Set position
                    next_test_piece.x = next_position
                    
                    # Drop the piece
                    next_test_piece.y = 0
                    while not self.check_collision(next_test_grid, next_test_piece, 0, 1):
                        next_test_piece.y += 1
                    
                    # Place the piece
                    self.place_piece(next_test_grid, next_test_piece)
                    
                    # Clear lines
                    next_lines_cleared = self.clear_lines(next_test_grid)
                    
                    # Evaluate
                    next_score = self.evaluate_position(next_test_grid, next_lines_cleared)
                    best_next_score = max(best_next_score, next_score)
                
                # Add the best next piece score with a discount factor
                move_score += 0.5 * best_next_score
            
            # Track the best move(s)
            if move_score > best_score:
                best_score = move_score
                best_moves = [move]
            elif move_score == best_score:
                best_moves.append(move)
        
        # If multiple moves have the same score, choose one randomly
        return random.choice(best_moves) if best_moves else None
    
    def get_possible_moves(self):
        """Get all possible moves (rotations and positions) for the current piece."""
        if not self.current_piece:
            return []
        
        return self.get_possible_moves_for_piece(self.grid, self.current_piece)
    
    def get_possible_moves_for_piece(self, grid, piece):
        """
        Get all possible moves for a given piece on a given grid.
        
        Args:
            grid: The game grid to check moves against
            piece: The tetromino piece to find moves for
            
        Returns:
            list: List of (rotations, x_position) tuples
        """
        possible_moves = []
        original_shape = copy.deepcopy(piece.shape)
        
        # Try each rotation
        for rotation in range(4):  # Max 4 rotations for any piece
            if rotation > 0:
                test_shape = self.rotate_shape(piece.shape)
                if test_shape == piece.shape:  # Skip duplicate rotations
                    continue
                piece.shape = test_shape
            
            shape_width = len(piece.shape[0])
            
            # Try each horizontal position
            for x in range(-2, 10):  # Allow some overhang for rotation clearance
                test_piece = copy.deepcopy(piece)
                test_piece.x = x
                test_piece.y = 0
                
                # Check if this position is valid
                if not self.check_collision(grid, test_piece, 0, 0):
                    possible_moves.append((rotation, x))
        
        # Restore original shape
        piece.shape = original_shape
        return possible_moves
    
    def rotate_shape(self, shape):
        """Rotate a shape 90 degrees clockwise."""
        # Get dimensions
        rows = len(shape)
        cols = len(shape[0])
        
        # Create a new rotated shape
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        # Fill in the rotated shape
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = shape[r][c]
        
        return rotated
    
    def check_collision(self, grid, piece, dx=0, dy=0):
        """
        Check if a piece at a given position would collide with the grid or boundaries.
        
        Args:
            grid: The game grid
            piece: The tetromino piece
            dx: Horizontal offset to check
            dy: Vertical offset to check
            
        Returns:
            bool: True if collision detected, False otherwise
        """
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    # Calculate position on grid
                    grid_x = piece.x + x + dx
                    grid_y = piece.y + y + dy
                    
                    # Check boundaries
                    if (grid_x < 0 or grid_x >= 10 or 
                        grid_y >= 20 or 
                        (grid_y >= 0 and grid[grid_y][grid_x] != 0)):
                        return True
        return False
    
    def place_piece(self, grid, piece):
        """
        Place a piece on the grid at its current position.
        
        Args:
            grid: The game grid to modify
            piece: The tetromino piece to place
        """
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = piece.x + x
                    grid_y = piece.y + y
                    
                    # Only place within grid bounds
                    if 0 <= grid_x < 10 and 0 <= grid_y < 20:
                        grid[grid_y][grid_x] = piece.shape_idx + 1
    
    def clear_lines(self, grid):
        """
        Clear completed lines from the grid and return the number cleared.
        
        Args:
            grid: The game grid to modify
            
        Returns:
            int: Number of lines cleared
        """
        lines_cleared = 0
        for y in range(20):
            if all(cell != 0 for cell in grid[y]):
                # Remove this line
                grid.pop(y)
                # Add a new empty line at the top
                grid.insert(0, [0 for _ in range(10)])
                lines_cleared += 1
        
        return lines_cleared
    
    def evaluate_position(self, grid, lines_cleared):
        """
        Evaluate a grid position using heuristics.
        
        Args:
            grid: The game grid to evaluate
            lines_cleared: Number of lines cleared in this move
            
        Returns:
            float: Score for this position (higher is better)
        """
        # Calculate heights of each column
        heights = [0] * 10
        for x in range(10):
            for y in range(20):
                if grid[y][x] != 0:
                    heights[x] = 20 - y
                    break
        
        # Maximum height
        max_height = max(heights) if heights else 0
        
        # Count holes (empty cells with non-empty cells above them)
        holes = 0
        for x in range(10):
            block_found = False
            for y in range(20):
                if grid[y][x] != 0:
                    block_found = True
                elif block_found and grid[y][x] == 0:
                    holes += 1
        
        # Calculate bumpiness (sum of differences in heights between adjacent columns)
        bumpiness = 0
        for x in range(9):
            bumpiness += abs(heights[x] - heights[x + 1])
        
        # Count edge touches (blocks touching left/right edges)
        edge_touch = 0
        for y in range(20):
            if grid[y][0] != 0:
                edge_touch += 1
            if grid[y][9] != 0:
                edge_touch += 1
        
        # Detect wells (columns with significantly lower height than neighbors)
        well_depth = 0
        for x in range(10):
            if x == 0:
                left_height = 20  # Edge of grid
            else:
                left_height = heights[x-1]
                
            if x == 9:
                right_height = 20  # Edge of grid
            else:
                right_height = heights[x+1]
                
            if heights[x] < left_height - 1 and heights[x] < right_height - 1:
                well_depth += min(left_height, right_height) - heights[x]
        
        # Detect overhangs (empty cells with non-empty cells to the left and right)
        overhang = 0
        for y in range(19):  # Skip bottom row
            for x in range(1, 9):  # Skip edges
                if grid[y][x] == 0 and grid[y+1][x] == 0:  # Empty cell with empty cell below
                    if grid[y][x-1] != 0 and grid[y][x+1] != 0:  # But blocks on left and right
                        overhang += 1
        
        # Calculate total score using weights
        score = (
            self.weights['height'] * max_height +
            self.weights['holes'] * holes +
            self.weights['bumpiness'] * bumpiness +
            self.weights['complete_lines'] * lines_cleared +
            self.weights['edge_touch'] * edge_touch +
            self.weights['well_depth'] * well_depth +
            self.weights['overhang'] * overhang
        )
        
        return score
