import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import './index.css';


const BACKEND_ENDPOINT = 'http://localhost:8080';
const GAME_TYPES = {
  BOT: "bot",
  MULTIPLAYER: "multiplayer",
};


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
      player_1: 'player 1',
      player_2: 'player 2',
      allowMove: true,
      winner: null,
      xIsBot: null,
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
      const squares = Array(this.state.x_size * this.state.y_size).fill(null);

      for (let i = 0; i < tiles.length; i++) {
        squares[
          (tiles[i].y_coordinate * this.state.x_size) + tiles[i].x_coordinate
        ] = tiles[i].player === this.state.player_1 ? 'X' : 'O';
      }

      this.setState({
        squares: squares,
        winner: winner,
        xIsNext: !this.state.xIsNext,
        winner: winner,
      });
    })
    .catch(error => {
      console.log(error);
      alert(error.response.status + " " + error.response.statusText);
    });
  }

  handleClickAddTile(i) {
    if (!this.state.allowMove || this.state.winner) {
      return;
    }

    if (this.state.gameType === GAME_TYPES.MULTIPLAYER) {
      this.addTile(i)
    } else if (this.state.gameType === GAME_TYPES.BOT) {

      if (this.state.xIsBot !== this.state.xIsNext) {
        this.addTile(i).then(() => {
          this.getAdviceAndMove();
        });
      }

    }
  }

  getAdviceAndMove() {
    this.getAdvice()
      .then(data => {
        const x = data[0];
        const y = data[1];
        return (y * this.state.x_size) + x;
      }).then(i => {
        this.addTile(i);
      })
  }

  handleClickGetAdvice() {
    const squares = this.state.squares.slice();

    if (this.state.winner) {
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
      allowMove: false
    });

    return axios.get(BACKEND_ENDPOINT + '/api/v1/game/'+this.state.gameId+'/next_move/'+player)
      .then(response => {
        const x = response.data.coordinates[0];
        const y = response.data.coordinates[1];
        this.setState({
          allowMove: true,
        });
        return [x, y]
      })
      .catch(error => {
        alert(error.response.status + " " + error.response.statusText);
        console.log(error);
      });
  }

  startNewGame(gameType, bot_player = null) {
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
        winner: null,
        xIsBot: bot_player ? (bot_player === 'X') : null,
      });
    })
    .then(() => {
      if (this.state.xIsBot) {
        this.getAdviceAndMove();
      }
    })
    .catch(error => {
      console.log(error.response);
      alert(error.response.status + " " + error.response.statusText);
    });
  }

  render() {
    const squares = this.state.squares;

    let status = "Next player: " + (this.state.xIsNext ? "X" : "O");

    let board;
    let advice_button;
    if (this.state.gameId) {
      board = <Board
        squares={squares}
        onClick={i => this.handleClickAddTile(i)}
        x_size={this.state.x_size}
        y_size={this.state.y_size}
      />;
      if (this.state.gameType === GAME_TYPES.MULTIPLAYER) {
        advice_button = <button onClick={() => this.handleClickGetAdvice()}>
          Get advice
        </button>
      } else {
        advice_button = null;
      }
      if (this.state.winner) {
        status = "Winner: " + this.state.winner;
        alert("Winner: " + this.state.winner);
      }
    } else {
      board = null;
      status = null;
    }

    return (
      <div className="game">
        <div className="game-board">
          {board}
        </div>
        <div className="game-info">
          <div>{status}</div>

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
      </div>
    );
  }
}

// ========================================

ReactDOM.render(<Game />, document.getElementById("root"));