import React, { useEffect, useState, useRef } from 'react';
import { Chessboard } from 'react-chessboard';
import { Chess } from 'chess.js';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:4000';
const ROOM_ID = 'dev-room-1';

export default function ChessGame() {
  const [game, setGame] = useState(new Chess());
  const [playerColor, setPlayerColor] = useState('');
  const [gameStatus, setGameStatus] = useState('Connecting...');
  const [clocks, setClocks] = useState({ w: 300, b: 300 });
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io(SOCKET_URL);
    const socket = socketRef.current;

    socket.emit('joinGame', { roomId: ROOM_ID });

    socket.on('initGame', ({ fen, color, clocks }) => {
      setGame(new Chess(fen));
      setPlayerColor(color);
      setClocks(clocks);
      setGameStatus(color === 'spectator' ? 'Spectating' : `Playing as ${color === 'w' ? 'White' : 'Black'}`);
    });

    socket.on('moveMade', ({ fen, clocks }) => {
      setGame(new Chess(fen));
      setClocks(clocks);
    });

    socket.on('clockTick', ({ clocks }) => {
      setClocks(clocks);
    });

    socket.on('gameOver', ({ reason }) => {
      setGameStatus(`Game Over: ${reason}`);
    });

    return () => socket.disconnect();
  }, []);

  function onDrop(sourceSquare, targetSquare) {
    if (playerColor === 'spectator' || game.turn() !== playerColor) return false;

    const movePayload = { from: sourceSquare, to: targetSquare, promotion: 'q' };
    try {
      const testGame = new Chess(game.fen());
      if (testGame.move(movePayload)) {
        socketRef.current.emit('makeMove', { roomId: ROOM_ID, move: movePayload });
        return true;
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  // Helper function to turn seconds into MM:SS format
  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', fontFamily: 'monospace', padding: '20px' }}>
      <h2>Full-Stack Chess</h2>
      <p style={{ fontSize: '18px', background: '#eee', padding: '5px 10px', borderRadius: '4px' }}>{gameStatus}</p>

      {/* Opponent Clock (Top) */}
      <div style={clockStyle(game.turn() === (playerColor === 'w' ? 'b' : 'w'))}>
        Opponent Time: {formatTime(playerColor === 'b' ? clocks.w : clocks.b)}
      </div>

      <div style={{ width: 'min(80vw, 450px)', margin: '15px 0' }}>
        <Chessboard 
          position={game.fen()} 
          onPieceDrop={onDrop}
          boardOrientation={playerColor === 'b' ? 'black' : 'white'}
        />
      </div>

      {/* Player Clock (Bottom) */}
      <div style={clockStyle(game.turn() === playerColor)}>
        Your Time: {formatTime(playerColor === 'w' ? clocks.w : clocks.b)}
      </div>
    </div>
  );
}

// Simple dynamic styling to highlight whose clock is actively ticking
const clockStyle = (isActive) => ({
  fontSize: '24px',
  fontWeight: 'bold',
  padding: '10px 20px',
  borderRadius: '5px',
  background: isActive ? '#ff4d4d' : '#333',
  color: '#fff',
  transition: 'background 0.3s'
});
