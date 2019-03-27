from typing import TYPE_CHECKING, Tuple, Union


if TYPE_CHECKING:
    from game.node import Node
    from game.rules import GameRules
    from game.heuristics import Heuristic


class Minimax:
    def __init__(self, heuristic: 'Heuristic', rules: 'GameRules'):
        self.rules = rules
        self.heuristic = heuristic
        self._depth = None

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

        # TODO: remove
        if not self._depth:
            self._depth = depth

        if depth == 0 or self.rules.is_terminated(node):
            value = self.heuristic.calculate(node)
            return value, node
        if node.maximizing_player:
            for child in node.children():
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
                new_beta = self.calculate_minimax(child, depth - 1, alpha, beta)[0]
                if new_beta < beta:
                    beta = new_beta
                    beta_node = child
                if beta <= alpha:
                    break

            node.chosen = (beta_node.new_move if beta_node else None, beta)
            return beta, beta_node
