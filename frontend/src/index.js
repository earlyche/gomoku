import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import './index.css';


const BACKEND_ENDPOINT = 'http://localhost:8080';
const GAME_TYPES = {
  BOT: "bot",
  MULTIPLAYER: "multiplayer",
};
const DRAW = "Draw";


function Square(props) {
  return (
    <button className="square" onClick={props.onClick}>
      {props.value}
    </button>
  );
}

class Board extends React.Component {
  renderSquare(i) {
    return (
      <Square
        key={i}
        value={this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
      />
    );
  }

  get_table() {
    let rows = []

    for (let i = 0; i < this.props.y_size; i++) {
      let row = []

      for (let j = 0; j < this.props.x_size; j++) {
        row.push(this.renderSquare((i * this.props.x_size) + j))
      }
      rows.push(<div key={i} className="board-row">{row}</div>)
    }
    return rows
  }

  render() {
    return (
      <div>
        {this.get_table()}
      </div>
    );
  }
}

class Game extends React.Component {
  constructor(props) {
    super(props);
    const x_size = 19;
    const y_size = 19;

    this.state = {
      squares: Array(x_size * y_size).fill(null),
      x_size: x_size,
      y_size: y_size,
      xIsNext: true,
      gameId: null,
      player_1: 'X',
      player_2: 'O',
      allowMove: true,
      allowAdvice: true,
      winner: null,
      xIsBot: null,
      moveTime: null,
      botPlayer: null,
      oCaptures: 0,
      xCaptures: 0,
      // moves: 0,
    };
  }

  addTile(i) {
    return axios.post(
      BACKEND_ENDPOINT + '/api/v1/game/add_tile/',
      {
        x_coordinate: i === 0 ? 0 : i % this.state.x_size,
        y_coordinate: i === 0 ? 0 : i / this.state.y_size >> 0,
        game_id: this.state.gameId,
        player: this.state.xIsNext ? this.state.player_1 : this.state.player_2,
      }
    )
    .then(response => {
      const tiles = response.data.tiles.slice();
      const winner = response.data.winner;
      const xCaptures = response.data.captures.x;
      const oCaptures = response.data.captures.o;
      const squares = Array(this.state.x_size * this.state.y_size).fill(null);
      // const moves = this.state.moves+1;

      for (let i = 0; i < tiles.length; i++) {
        squares[
          (tiles[i].y_coordinate * this.state.x_size) + tiles[i].x_coordinate
        ] = tiles[i].player === this.state.player_1 ? 'X' : 'O';
      }

      this.setState({
        squares: squares,
        winner: winner,
        xIsNext: !this.state.xIsNext,
        xCaptures: xCaptures,
        oCaptures: oCaptures,
        allowAdvice: true,
        // moves: moves,
      });

      this.forceUpdate();

    });
  }

  handleClickAddTile(i) {
    if (!this.state.allowMove || this.state.winner) {
      return;
    }

    if (this.state.squares[i] === 'X' ||
      this.state.squares[i] === 'O') {
      return;
    }

    if (this.state.gameType === GAME_TYPES.MULTIPLAYER) {
      this.addTile(i)
      .catch(error => {
        console.log(error);
        if (error.hasOwnProperty('response')) {
          if (error.response.status === 403) {
            alert("MOVE FORBIDDEN");
          } else {
            alert("Error");
          }
        }
      });
    } else if (this.state.gameType === GAME_TYPES.BOT) {

      if (this.state.xIsBot !== this.state.xIsNext) {
        this.addTile(i)
        .then(() => {
          this.getAdviceAndMove();
        })
        .catch(error => {
          console.log(error);
          if (error.hasOwnProperty('response')) {
            if (error.response.status === 403) {
              alert("MOVE FORBIDDEN");
            } else {
              alert("Error");
            }
          }
        });
      }

    }
  }

  getAdviceAndMove() {
    if (this.state.winner) {
      return
    }
    this.getAdvice()
      .then(data => {
        const x = data[0];
        const y = data[1];
        return (y * this.state.x_size) + x;
      }).then(i => {
        this.addTile(i)
        .catch(error => {
          console.log(error);
          if (error.hasOwnProperty('response')) {
            if (error.response.status === 403) {
              alert("MOVE FORBIDDEN");
            } else {
              alert("Error");
            }
          }
        });
      })
  }

  handleClickGetAdvice() {
    const squares = this.state.squares.slice();

    if (this.state.winner || !this.state.allowAdvice) {
      return;
    }

    this.getAdvice()
      .then(data => {
        const x = data[0];
        const y = data[1];

        squares[(y * this.state.x_size) + x] = '.';
        this.setState({
          squares: squares,
        });
      });
  }

  getAdvice() {
    const player = this.state.xIsNext ? this.state.player_1 : this.state.player_2;

    this.setState({
      allowMove: false,
      allowAdvice: false
    });

    return axios.get(BACKEND_ENDPOINT + '/api/v1/game/'+this.state.gameId+'/next_move/'+player)
      .then(response => {
        const x = response.data.coordinates[0];
        const y = response.data.coordinates[1];
        const moveTime = response.data.time;

        this.setState({
          allowMove: true,
          moveTime: moveTime,
        });
        return [x, y]
      })
      .catch(error => {
        alert("Error");
        console.log(error);
      });
  }

  startNewGame(gameType, botPlayer = null) {
    axios.post(
      BACKEND_ENDPOINT + '/api/v1/game/',
      {
        player_1: this.state.player_1,
        player_2: this.state.player_2,
        type: gameType,
      }
    )
    .then(response => {
      this.setState({
        gameId: response.data.id,
        player_1: response.data.player_1,
        player_2: response.data.player_2,
        gameType: gameType,
        squares: Array(this.state.x_size * this.state.y_size).fill(null),
        xIsNext: true,
        allowMove: true,
        allowAdvice: true,
        winner: null,
        xIsBot: botPlayer ? (botPlayer === 'X') : null,
        botPlayer: botPlayer,
        moveTime: null,
        oCaptures: 0,
        xCaptures: 0,
        // moves: 0,
      });
    })
    .then(() => {
      if (this.state.xIsBot) {
        this.getAdviceAndMove();
      }
    })
    .catch(error => {
      alert("Error");
      console.log(error);
    });
  }

  render() {
    const squares = this.state.squares;
    let status = <h2>Next player: {(this.state.xIsNext ? "X" : "O")}</h2>;
    let board;
    let advice_button;
    let moveTime = null;

    if (this.state.gameId) {
      board = <Board
        squares={squares}
        onClick={i => this.handleClickAddTile(i)}
        x_size={this.state.x_size}
        y_size={this.state.y_size}
      />;
      advice_button = <button onClick={() => this.handleClickGetAdvice()}>
      Get advice
      </button>
      if (this.state.winner) {
        if (this.state.winner === DRAW) {
          const color = "green";
          status = <h2 style={{'color': color}}>{DRAW}</h2>;
        } else {
          const color = (this.state.botPlayer && this.state.botPlayer === this.state.winner) ? "red" : "green";
          status = <h2 style={{'color': color}}>Winner: {this.state.winner}</h2>;
        }
      }

    } else {
      board = null;
      status = null;
    }

    if (this.state.moveTime) {
      moveTime =
        <div className="move-time">
          <p>Move time: {this.state.moveTime.toFixed(3)} sec.</p>
        </div>
    }

    return (
      <div className="game">
        <div className="game-board">
          {board}
        </div>
        <div className="game-info">
          {status}
          <div>
            <button onClick={() => this.startNewGame(GAME_TYPES.BOT, 'O')}>
              Start new game with bot for X
            </button>
          </div>
          <div>
            <button onClick={() => this.startNewGame(GAME_TYPES.BOT, 'X')}>
              Start new game with bot for O
            </button>
          </div>
          <div>
            <button onClick={() => this.startNewGame(GAME_TYPES.MULTIPLAYER)}>
              Start new multiplayer game
            </button>
          </div>
          <div>
            {advice_button}
          </div>
        </div>
        <div className="captures">
          <p>X captures: {this.state.xCaptures}</p>
          <p>O captures: {this.state.oCaptures}</p>
          {/* <p>Moves: {this.state.moves}</p> */}
        </div>
        {moveTime}
      </div>
    );
  }
}

// ========================================

ReactDOM.render(<Game />, document.getElementById("root"));