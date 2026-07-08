const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { Chess } = require('chess.js');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" } // Allowing cross-origin for development
});

// In-memory store for active games (In production, use Redis)
const games = {}; 

io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // 1. JOIN/CREATE ROOM
  socket.on('joinGame', ({ roomId }) => {
    socket.join(roomId);

    // If game doesn't exist, initialize it
    if (!games[roomId]) {
      games[roomId] = {
        chess: new Chess(),
        players: { white: null, black: null }
      };
    }

    const game = games[roomId];

    // Assign color roles
    let assignedColor = null;
    if (!game.players.white) {
      game.players.white = socket.id;
      assignedColor = 'w';
    } else if (!game.players.black && game.players.white !== socket.id) {
      game.players.black = socket.id;
      assignedColor = 'b';
    } else {
      assignedColor = 'spectator';
    }

    // Send initial state to the joined player
    socket.emit('initGame', {
      fen: game.chess.fen(),
      color: assignedColor
    });

    console.log(`User ${socket.id} joined room ${roomId} as ${assignedColor}`);
  });

  // 2. HANDLE MOVES
  socket.on('makeMove', ({ roomId, move }) => {
    const game = games[roomId];
    if (!game) return;

    // Security Check: Verify it is the correct player's turn
    const currentTurn = game.chess.turn(); // 'w' or 'b'
    if (
      (currentTurn === 'w' && socket.id !== game.players.white) ||
      (currentTurn === 'b' && socket.id !== game.players.black)
    ) {
      socket.emit('error', 'It is not your turn.');
      return;
    }

    try {
      // Validate move via chess.js
      const result = game.chess.move(move);
      
      if (result) {
        // Broadcast the updated FEN to everyone in the room
        io.to(roomId).emit('moveMade', {
          fen: game.chess.fen(),
          lastMove: move
        });

        // Check for game over states
        if (game.chess.isGameOver()) {
          io.to(roomId).emit('gameOver', {
            checkmate: game.chess.isCheckmate(),
            draw: game.chess.isDraw()
          });
        }
      }
    } catch (error) {
      socket.emit('error', 'Invalid move.');
    }
  });

  // 3. CLEANUP ON DISCONNECT
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
    // Optional: Clean up empty rooms or alert opponents here
  });
});

server.listen(4000, () => {
  console.log('Server running on port 4000');
});
