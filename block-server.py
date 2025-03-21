import socket
import threading
import json
import random
import time
import uuid
import logging
import heapq
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TetrisServer:
    def __init__(self, host='0.0.0.0', port=5555, scores_file="high_scores.json"):
        self.host = host
        self.port = port
        self.scores_file = scores_file
        self.server_socket = None
        self.clients = {}  # {client_id: {"socket": socket, "name": name, "opponent": opponent_id, "game_state": {...}, "mode": mode}}
        self.waiting_player = None  # ID of player waiting for opponent
        self.high_scores = []  # List of (score, name) tuples for ranking
        self.lock = threading.Lock()
        self.running = False
        
        # Load high scores if file exists
        self.load_high_scores()

    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    self.high_scores = json.load(f)
                logger.info(f"Loaded {len(self.high_scores)} high scores")
            else:
                self.high_scores = []
        except Exception as e:
            logger.error(f"Error loading high scores: {e}")
            self.high_scores = []

    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.high_scores, f)
            logger.info(f"Saved {len(self.high_scores)} high scores")
        except Exception as e:
            logger.error(f"Error saving high scores: {e}")

    def add_high_score(self, name, score):
        """Add a high score to the list and save"""
        with self.lock:
            # Add the score
            self.high_scores.append([name, score])
            
            # Sort by score (descending)
            self.high_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only top 20 scores
            if len(self.high_scores) > 20:
                self.high_scores = self.high_scores[:20]
            
            # Save to file
            self.save_high_scores()
            
            logger.info(f"Added high score: {name} - {score}")

    def start(self):
        """Start the server and listen for connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Start accepting connections
            while self.running:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"New connection from {addr}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        with self.lock:
            for client_id, client_info in self.clients.items():
                try:
                    client_info["socket"].close()
                except:
                    pass
            
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        
        # Save high scores
        self.save_high_scores()
        
        logger.info("Server stopped")
    
    def handle_client(self, client_socket, addr):
        """Handle communication with a client"""
        client_id = str(uuid.uuid4())
        
        try:
            # Add client to clients dictionary
            with self.lock:
                self.clients[client_id] = {
                    "socket": client_socket,
                    "name": f"Player_{client_id[:8]}",
                    "opponent": None,
                    "game_state": {
                        "grid": [],
                        "score": 0
                    },
                    "mode": "unknown"  # Will be set when client sends join message
                }
            
            # Handle client messages
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                self.process_message(client_id, data)
                
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.handle_client_disconnect(client_id)
    
    def handle_client_disconnect(self, client_id):
        """Handle client disconnection"""
        with self.lock:
            if client_id in self.clients:
                # Get opponent ID before removing client
                opponent_id = self.clients[client_id].get("opponent")
                
                # Close socket and remove client
                try:
                    self.clients[client_id]["socket"].close()
                except:
                    pass
                
                # If this client was waiting for an opponent, clear waiting player
                if self.waiting_player == client_id:
                    self.waiting_player = None
                
                # Notify opponent of disconnection if in multiplayer mode
                if opponent_id and opponent_id in self.clients:
                    self.send_message(opponent_id, {
                        "type": "opponent_disconnected"
                    })
                    
                    # Reset opponent's opponent
                    self.clients[opponent_id]["opponent"] = None
                
                # Remove client
                del self.clients[client_id]
                
                logger.info(f"Client {client_id} disconnected")
    
    def process_message(self, client_id, data):
        """Process a message from a client"""
        try:
            message = json.loads(data.decode())
            message_type = message.get("type")
            
            if message_type == "join":
                self.handle_join(client_id, message)
            
            elif message_type == "grid_update":
                self.handle_grid_update(client_id, message)
            
            elif message_type == "clear_lines":
                self.handle_clear_lines(client_id, message)
            
            elif message_type == "game_over":
                self.handle_game_over(client_id, message)
            
            elif message_type == "ready_for_new_game":
                self.handle_ready_for_new_game(client_id)
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")
        except Exception as e:
            logger.error(f"Error processing message from client {client_id}: {e}")
    
    def handle_join(self, client_id, message):
        """Handle a join request from a client"""
        with self.lock:
            # Update client name if provided
            if "name" in message:
                self.clients[client_id]["name"] = message["name"]
            
            # Update game mode
            game_mode = message.get("mode", "single")
            self.clients[client_id]["mode"] = game_mode
            
            # Send player ID back to client
            self.send_message(client_id, {
                "type": "player_id",
                "id": client_id
            })
            
            # Send high scores to client
            self.send_message(client_id, {
                "type": "high_scores",
                "scores": self.high_scores
            })
            
            # If multiplayer mode, handle matchmaking
            if game_mode == "multiplayer":
                # Check if there's a waiting player
                if self.waiting_player and self.waiting_player in self.clients:
                    # Match with waiting player
                    opponent_id = self.waiting_player
                    
                    # Update opponent references
                    self.clients[client_id]["opponent"] = opponent_id
                    self.clients[opponent_id]["opponent"] = client_id
                    
                    # Clear waiting player
                    self.waiting_player = None
                    
                    # Notify both players of game start
                    self.send_message(client_id, {
                        "type": "game_start",
                        "opponent_name": self.clients[opponent_id]["name"]
                    })
                    
                    self.send_message(opponent_id, {
                        "type": "game_start",
                        "opponent_name": self.clients[client_id]["name"]
                    })
                    
                    logger.info(f"Started multiplayer game between {self.clients[client_id]['name']} and {self.clients[opponent_id]['name']}")
                else:
                    # Become the waiting player
                    self.waiting_player = client_id
                    logger.info(f"{self.clients[client_id]['name']} is waiting for an opponent")
            else:
                # Single player mode
                logger.info(f"{self.clients[client_id]['name']} started a single player game")
    
    def handle_grid_update(self, client_id, message):
        """Handle a grid update from a client"""
        with self.lock:
            if client_id in self.clients:
                # Update client's game state
                self.clients[client_id]["game_state"]["grid"] = message["grid"]
                self.clients[client_id]["game_state"]["score"] = message["score"]
                
                # If in multiplayer mode, forward update to opponent
                game_mode = message.get("mode", self.clients[client_id].get("mode", "single"))
                if game_mode == "multiplayer":
                    opponent_id = self.clients[client_id].get("opponent")
                    if opponent_id and opponent_id in self.clients:
                        self.send_message(opponent_id, {
                            "type": "opponent_update",
                            "grid": message["grid"],
                            "score": message["score"]
                        })
    
    def handle_clear_lines(self, client_id, message):
        """Handle a line clear notification from a client"""
        with self.lock:
            if client_id in self.clients:
                lines_cleared = message.get("lines", 0)
                
                # In multiplayer mode, notify opponent to add junk lines
                game_mode = self.clients[client_id].get("mode", "single")
                if game_mode == "multiplayer":
                    opponent_id = self.clients[client_id].get("opponent")
                    if opponent_id and opponent_id in self.clients:
                        self.send_message(opponent_id, {
                            "type": "add_lines",
                            "lines": lines_cleared
                        })
                        
                        logger.info(f"{self.clients[client_id]['name']} cleared {lines_cleared} lines, sending to {self.clients[opponent_id]['name']}")
    
    def handle_game_over(self, client_id, message):
        """Handle a game over notification from a client"""
        with self.lock:
            if client_id in self.clients:
                score = message.get("score", 0)
                game_mode = self.clients[client_id].get("mode", "single")
                
                # Add to high scores
                self.add_high_score(self.clients[client_id]["name"], score)
                
                # Send updated high scores
                self.send_message(client_id, {
                    "type": "high_scores",
                    "scores": self.high_scores
                })
                
                # Handle multiplayer game over
                if game_mode == "multiplayer":
                    opponent_id = self.clients[client_id].get("opponent")
                    
                    if opponent_id and opponent_id in self.clients:
                        # Notify both players of game over
                        self.send_message(client_id, {
                            "type": "game_over",
                            "winner": opponent_id
                        })
                        
                        self.send_message(opponent_id, {
                            "type": "game_over",
                            "winner": opponent_id
                        })
                        
                        logger.info(f"Multiplayer game over - {self.clients[opponent_id]['name']} wins over {self.clients[client_id]['name']}")
                        
                        # Send updated high scores to opponent too
                        self.send_message(opponent_id, {
                            "type": "high_scores",
                            "scores": self.high_scores
                        })
                        
                        # Reset opponents
                        self.clients[client_id]["opponent"] = None
                        self.clients[opponent_id]["opponent"] = None
                else:
                    # Single player game over
                    logger.info(f"Single player game over - {self.clients[client_id]['name']} scored {score}")
    
    def handle_ready_for_new_game(self, client_id):
        """Handle a client ready for a new game after game over"""
        with self.lock:
            if client_id in self.clients:
                game_mode = self.clients[client_id].get("mode", "single")
                
                if game_mode == "multiplayer":
                    # Check if there's a waiting player
                    if self.waiting_player and self.waiting_player in self.clients and self.waiting_player != client_id:
                        # Match with waiting player
                        opponent_id = self.waiting_player
                        
                        # Update opponent references
                        self.clients[client_id]["opponent"] = opponent_id
                        self.clients[opponent_id]["opponent"] = client_id
                        
                        # Clear waiting player
                        self.waiting_player = None
                        
                        # Notify both players of game start
                        self.send_message(client_id, {
                            "type": "game_start",
                            "opponent_name": self.clients[opponent_id]["name"]
                        })
                        
                        self.send_message(opponent_id, {
                            "type": "game_start",
                            "opponent_name": self.clients[client_id]["name"]
                        })
                        
                        logger.info(f"Started new multiplayer game between {self.clients[client_id]['name']} and {self.clients[opponent_id]['name']}")
                    else:
                        # Become the waiting player
                        self.waiting_player = client_id
                        logger.info(f"{self.clients[client_id]['name']} is waiting for an opponent")
    
    def send_message(self, client_id, message):
        """Send a message to a client"""
        try:
            if client_id in self.clients:
                self.clients[client_id]["socket"].send(json.dumps(message).encode())
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            self.handle_client_disconnect(client_id)

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Tetris Multiplayer Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=5555, help="Port to bind to")
    parser.add_argument("--scores", default="high_scores.json", help="High scores file")
    args = parser.parse_args()
    
    # Start server
    server = TetrisServer(args.host, args.port, args.scores)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        server.stop()