const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { Chess } = require('chess.js');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

const games = {}; 
const STARTING_TIME = 300; // 5 minutes in seconds

io.on('connection', (socket) => {
  
  socket.on('joinGame', ({ roomId }) => {
    socket.join(roomId);

    if (!games[roomId]) {
      games[roomId] = {
        chess: new Chess(),
        players: { white: null, black: null },
        clocks: { w: STARTING_TIME, b: STARTING_TIME },
        timerInterval: null,
        gameStarted: false
      };
    }

    const game = games[roomId];

    let assignedColor = null;
    if (!game.players.white) {
      game.players.white = socket.id;
      assignedColor = 'w';
    } else if (!game.players.black && game.players.white !== socket.id) {
      game.players.black = socket.id;
      assignedColor = 'b';
      game.gameStarted = true; // Start the game when both players arrive
      startClockInterval(roomId);
    } else {
      assignedColor = 'spectator';
    }

    socket.emit('initGame', {
      fen: game.chess.fen(),
      color: assignedColor,
      clocks: game.clocks
    });
  });

  socket.on('makeMove', ({ roomId, move }) => {
    const game = games[roomId];
    if (!game || !game.gameStarted) return;

    const currentTurn = game.chess.turn();
    if (
      (currentTurn === 'w' && socket.id !== game.players.white) ||
      (currentTurn === 'b' && socket.id !== game.players.black)
    ) {
      return;
    }

    try {
      const result = game.chess.move(move);
      if (result) {
        io.to(roomId).emit('moveMade', {
          fen: game.chess.fen(),
          clocks: game.clocks // Send exact clock states after the move
        });

        if (game.chess.isGameOver()) {
          clearInterval(game.timerInterval);
          io.to(roomId).emit('gameOver', { reason: 'Checkmate or Draw' });
        }
      }
    } catch (e) {
      socket.emit('error', 'Invalid move.');
    }
  });
});

// Centralized Clock Tick Logic
function startClockInterval(roomId) {
  const game = games[roomId];
  if (!game || game.timerInterval) return;

  game.timerInterval = setInterval(() => {
    const currentTurn = game.chess.turn(); // 'w' or 'b'
    
    if (game.clocks[currentTurn] > 0) {
      game.clocks[currentTurn]--;
      
      // Broadcast live clock tick to both clients
      io.to(roomId).emit('clockTick', { clocks: game.clocks });
    } else {
      // Time Out Flag
      clearInterval(game.timerInterval);
      const winner = currentTurn === 'w' ? 'Black' : 'White';
      io.to(roomId).emit('gameOver', { reason: `${winner} wins on time!` });
    }
  }, 1000);
}

server.listen(4000, () => console.log('Server running on port 4000'));
