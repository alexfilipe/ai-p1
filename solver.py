"""solver.py -- Implements informed search strategy for 8-puzzle solution

Author: Álex Filipe Santos
Date: 19 July 2020
"""
from queue import PriorityQueue
from copy import deepcopy
from puzzle import Puzzle, NotSolvableException

# Standard cost of reaching a new node.
STANDARD_COST = 1

class PuzzleNode:
    """Represents a node in the search graph.
    """
    def __init__(self,
                 puzzle,
                 parent=None,
                 cost=0,
                 cumulative_cost=0,
                 heuristic=1):
        self.puzzle = puzzle

        # Pointer to the parent puzzle.
        self.parent = parent

        # Cost of reaching this node
        self.cost = cost

        # Cumulative cost of reaching this node
        self.cumulative_cost = cumulative_cost

        # Type of heuristic used for this node
        self.heuristic = heuristic

        # Evaluation function result for the node
        self.evaluation = self._evaluation(heuristic)


    # These comparison operators compare different evaluations (considering path
    # cost and heuristic) between different nodes of the search graph.
    def __lt__(self, other):
        return self.evaluation < other.evaluation
    def __le__(self, other):
        return self.evaluation <= other.evaluation
    def __eq__(self, other):
        return self.evaluation == other.evaluation
    def __ne__(self, other):
        return self.evaluation != other.evaluation
    def __ge__(self, other):
        return self.evaluation >= other.evaluation
    def __gt__(self, other):
        return self.evaluation > other.evaluation


    def next_moves(self):
        """Expands the current node, returning a list of next possible moves.

        Returns:
            list of obj:`Puzzle`: a list of all next state puzzles that have
                allowed moves.
        """
        possible_moves = self.puzzle.allowed_moves
        nodes = []

        for move in possible_moves:
            child_puzzle = deepcopy(self.puzzle)
            child_puzzle.move(move)

            cumulative_cost = self.cumulative_cost + STANDARD_COST

            child_node = PuzzleNode(child_puzzle,
                                    parent=self,
                                    cost=STANDARD_COST,
                                    cumulative_cost=cumulative_cost,
                                    heuristic=self.heuristic)

            nodes.append(child_node)

        return nodes

    def _evaluation(self, heuristic=1):
        """Evaluation function for the node.

        Args:
            heuristic (int): The search heuristic to use.
                1 = represents the misplaced tiles heuristic
                2 = represents the Manhattan distance heuristic

        Returns:
            int: the search heuristic result.
        """
        h = 0

        # Misplaced heuristic
        if heuristic == 1:
            h = self.puzzle.misplaced_heuristic()

        # Manhattan heuristic
        elif heuristic == 2:
            h = self.puzzle.manhattan_heuristic()

        return self.cumulative_cost + h


class PuzzleSolver:
    """Represents a puzzle tree with informed search method to find the goal.
    """
    def __init__(self, puzzle, heuristic=1):
        if not puzzle.is_solvable():
            raise NotSolvableException("The puzzle provided is not solvable.")

        # Initial state of the puzzle
        self.tree_root = PuzzleNode(puzzle, heuristic=heuristic)


    def find_solution(self):
        """Returns a list of steps to reach the solution, including some
        statistics (depth of solution and cost of solution - number of node
        expansions needed).

        Returns:
            dict: statistics
        """
        steps = []
        solution, cost = self.search_solution()

        if solution is None:
            raise NotSolvableException("Failed to find a solution.")

        # Finds all previous node states.
        node = solution
        while node is not None:
            steps.append(node.puzzle)
            node = node.parent

        steps.reverse()

        return {
            "steps": steps,
            "depth": len(steps) - 1,
            "cost": cost
        }


    def search_solution(self):
        """Runs the A* search algorithm to find a solution.

        Returns:
            obj:`PuzzleNode`: the node representing the solution in the tree.
            int: the total cost to reach the solution.
        """

        # Priority queue of best cost nodes
        frontier = PriorityQueue()

        # Set of strings to remember if state was explored or not
        explored = set()

        # Put the root in the priority queue
        # The PuzzleNode class implements heuristic comparison with Python
        # rich comparison operators.
        frontier.put(self.tree_root)

        # Number of nodes generated
        search_cost = 1

        while not frontier.empty():
            next_node = frontier.get()

            if next_node.puzzle.is_solved():
                return next_node, search_cost

            explored.add(next_node.puzzle.string)

            moves = next_node.next_moves()

            for moved_node in moves:
                # Add node to the frontier
                if moved_node.puzzle.string not in explored:
                    frontier.put(moved_node)
                    search_cost += 1

        # Failed to find a solution
        if frontier.empty():
            return None, search_cost
