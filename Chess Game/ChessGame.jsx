import React, { useEffect, useState, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:4000';
const ROOM_ID = 'dev-room-1'; // Static room for development simplicity

export default function ChessGame() {
  const [game, setGame] = useState(new Chess());
  const [playerColor, setPlayerColor] = useState(''); // 'w', 'b', or 'spectator'
  const [gameStatus, setGameStatus] = useState('Connecting to game...');
  const socketRef = useRef(null);

  useEffect(() => {
    // Connect to backend websocket
    socketRef.current = io(SOCKET_URL);
    const socket = socketRef.current;

    socket.emit('joinGame', { roomId: ROOM_ID });

    socket.on('initGame', ({ fen, color }) => {
      const initialGame = new Chess(fen);
      setGame(initialGame);
      setPlayerColor(color);
      
      if (color === 'spectator') {
        setGameStatus('Spectating match');
      } else {
        setGameStatus(`Playing as ${color === 'w' ? 'White' : 'Black'}`);
      }
    });

    socket.on('moveMade', ({ fen }) => {
      const updatedGame = new Chess(fen);
      setGame(updatedGame);
    });

    socket.on('gameOver', ({ checkmate, draw }) => {
      if (checkmate) setGameStatus('Game Over: Checkmate!');
      if (draw) setGameStatus('Game Over: Draw!');
    });

    socket.on('error', (message) => {
      alert(message);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Handle Drag and Drop action on the board
  function onDrop(sourceSquare, targetSquare) {
    // Prevent moving if you are a spectator
    if (playerColor === 'spectator') return false;

    // Prevent moving opponent's pieces
    const currentTurn = game.turn();
    if (currentTurn !== playerColor) return false;

    const movePayload = {
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q', // Automatically promote to Queen for simplicity
    };

    // Optimistically check move validity on client side first
    try {
      const testGame = new Chess(game.fen());
      const validMove = testGame.move(movePayload);
      
      if (validMove) {
        // Send the verified move attempt to server
        socketRef.current.emit('makeMove', {
          roomId: ROOM_ID,
          move: movePayload,
        });
        return true;
      }
    } catch (e) {
      return false; // Piece snaps back to place if invalid
    }
    return false;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', fontFamily: 'sans-serif' }}>
      <h2>Full-Stack Chess Engine</h2>
      <p style={{ fontWeight: 'bold', color: '#555' }}>{gameStatus}</p>
      
      <div style={{ width: 'min(80vw, 500px)', boxShadow: '0 4px 10px rgba(0,0,0,0.15)' }}>
        <Chessboard 
          position={game.fen()} 
          onPieceDrop={onDrop}
          boardOrientation={playerColor === 'b' ? 'black' : 'white'}
        />
      </div>
      
      <p style={{ marginTop: '15px' }}>
        Current Turn: {game.turn() === 'w' ? 'White' : 'Black'}
      </p>
    </div>
  );
}
