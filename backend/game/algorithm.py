from typing import TYPE_CHECKING, Tuple, Union

from game.analyzer import Analyzer
from game.rules import GameRules

if TYPE_CHECKING:
    from game.node import Node
    from game.heuristics import Heuristic


class Minimax:
    def __init__(self, heuristic: 'Heuristic'):
        self.heuristic = heuristic

    def calculate_minimax(
            self,
            node: 'Node',
            depth: int,
            alpha: float = None,
            beta: float = None,
    ) -> Tuple[float, Union['Node', None]]:
        alpha = alpha if alpha is not None else self.heuristic.alpha_min
        beta = beta if beta is not None else self.heuristic.beta_max
        alpha_node = None
        beta_node = None

        if depth == 0 or GameRules.is_terminated(node):
            value = self.heuristic.calculate(node)
            return value, node
        if node.maximizing_player:
            for child in node.children():
                Analyzer.update(Analyzer.NODE_COUNT, 1)
                new_alpha = self.calculate_minimax(child, depth - 1, alpha, beta)[0]
                if new_alpha > alpha:
                    alpha = new_alpha
                    alpha_node = child
                if beta <= alpha:
                    break
            node.chosen = (alpha_node.new_move if alpha_node else None, alpha)
            return alpha, alpha_node
        else:
            for child in node.children():
                Analyzer.update(Analyzer.NODE_COUNT, 1)
                new_beta = self.calculate_minimax(child, depth - 1, alpha, beta)[0]
                if new_beta < beta:
                    beta = new_beta
                    beta_node = child
                if beta <= alpha:
                    break

            node.chosen = (beta_node.new_move if beta_node else None, beta)
            return beta, beta_node
