from graphviz import Digraph

class BDDNode:
    def __init__(self, var=None, low=None, high=None):
        self.var = var
        self.low = low
        self.high = high

def build_bdd(expression, variables):

    def recursive_build(path, depth):
        if depth == len(variables):
            output = expression(path)
            return BDDNode(var="1") if output else BDDNode(var="0")

        var = variables[depth]
        node = BDDNode(var=var)

        # first case
        path[var] = 0
        node.low = recursive_build(path.copy(), depth + 1)

        # second case
        path[var] = 1
        node.high = recursive_build(path.copy(), depth + 1)

        return node

    return recursive_build({}, 0)

def is_terminal(node):
    return node.var in ["0", "1"]

def reduce_bdd(node, visited=None):
    if visited is None:
        visited = {}

    if node.var in ["0", "1"]:
        return node

    node.low = reduce_bdd(node.low, visited)
    node.high = reduce_bdd(node.high, visited)

    if node.low == node.high:
        return node.low

    # simplify nodes where children always resolve to the same value (direct terminal)
    if is_terminal(node.low) and is_terminal(node.high):
        if node.low.var == node.high.var:
            return node.low  # both branches lead to the same terminal value

    low_id = node.low.var if node.low.var in ["0", "1"] else id(node.low)
    high_id = node.high.var if node.high.var in ["0", "1"] else id(node.high)

    node_id = (node.var, low_id, high_id)
    if node_id in visited:
        print("found one")
        return visited[node_id]

    visited[node_id] = node
    return node

def equivalent_subtrees(node1, node2):
    """
    Check if two subtrees are structurally equivalent.
    """
    if node1 is node2:  # same object
        return True
    if node1.var != node2.var:  # different variables
        return False
    if node1.var in ["0", "1"] and node2.var in ["0", "1"]:  # both are terminal nodes
        return node1.var == node2.var
    return (equivalent_subtrees(node1.low, node2.low) and
            equivalent_subtrees(node1.high, node2.high))

def visualize_bdd(node):
    dot = Digraph()

    def add_nodes_edges(node):
        if node.var in ["0", "1"]:
            unique_id = f"{node.var}_{id(node)}"
            dot.node(unique_id, node.var, shape="box")
            return unique_id

        dot.node(str(id(node)), node.var)
        low_id = add_nodes_edges(node.low)
        high_id = add_nodes_edges(node.high)
        dot.edge(str(id(node)), low_id, label="0", style="dotted")
        dot.edge(str(id(node)), high_id, label="1")

        return str(id(node))

    add_nodes_edges(node)
    return dot

def visualize_robdd(node):
    dot = Digraph()

    def add_nodes_edges(node, visited):
        if node.var in ["0", "1"]:
            # Use a single box for terminal nodes
            if node.var not in visited:
                dot.node(node.var, node.var, shape="box")
                visited[node.var] = node.var
            return node.var

        # Check if this node has already been visited
        node_id = (node.var, id(node.low), id(node.high))

        if node_id in visited:
            return visited[node_id]

        # Add the current node to the graph
        current_id = str(id(node))
        dot.node(current_id, node.var)
        visited[node_id] = current_id

        # Add edges to the graph
        low_id = add_nodes_edges(node.low, visited)
        high_id = add_nodes_edges(node.high, visited)
        dot.edge(current_id, low_id, label="0", style="dotted")
        dot.edge(current_id, high_id, label="1")

        return current_id

    add_nodes_edges(node, {})
    return dot


# LogicCircuit Class
class LogicCircuit:
    def check_if_valid(self, expression):
        valid_chars = set('ABCabc!&|()^ ')
        for ch in expression:
            if ch not in valid_chars:
                print("Invalid Expression")
                return False
        return True

    def evaluate_expression(self, expression, A, B, C):
        values = []
        operators = []

        i = 0
        while i < len(expression):
            ch = expression[i]
            if ch.islower():
                ch = ch.upper()

            if ch == ' ':
                i += 1
                continue

            if ch in 'ABC':
                currentVar = A if ch == 'A' else (B if ch == 'B' else C)
                values.append(currentVar)
            elif ch == '!' and i + 1 < len(expression) and expression[i + 1] in 'ABC':
                i += 1
                currentVar = A if expression[i] == 'A' else (B if expression[i] == 'B' else C)
                values.append(not currentVar)
            elif ch == '(':
                operators.append(ch)
            elif ch == ')':
                while operators and operators[-1] != '(':
                    val2 = values.pop()
                    val1 = values.pop()
                    op = operators.pop()
                    values.append(self.assign_operator(op, val1, val2))
                operators.pop()
            elif ch in '&|^':
                while operators and operators[-1] != '(':
                    op = operators.pop()
                    val2 = values.pop()
                    val1 = values.pop()
                    values.append(self.assign_operator(op, val1, val2))
                operators.append(ch)

            i += 1

        while operators:
            op = operators.pop()
            val2 = values.pop()
            val1 = values.pop()
            values.append(self.assign_operator(op, val1, val2))

        return values[-1]

    def assign_operator(self, op, a, b):
        if op == '&':
            return a and b
        elif op == '|':
            return a or b
        elif op == '^':
            return a != b
        return False

    def truth_table(self, expression):
        truth_table = []
        print("Truth Table")
        print("A\tB\tC\tResult")
        for A in range(2):
            for B in range(2):
                for C in range(2):
                    result = self.evaluate_expression(expression, A, B, C)
                    result = int(result)
                    truth_table.append({'A': A, 'B': B, 'C': C, 'Result': result})
                    print(f"{A}\t{B}\t{C}\t{result}")
        return truth_table



def main():
    circuit = LogicCircuit()

    print("Enter the first Boolean expression (e.g., A & B | !C):")
    expression1 = input().strip()
    print("Enter the second Boolean expression (e.g., A & (B | !C)):")
    expression2 = input().strip()

    if not circuit.check_if_valid(expression1) or not circuit.check_if_valid(expression2):
        print("Invalid expression(s). Exiting.")
        return

    variables = ['A', 'B', 'C']

    print("\nBuilding BDDs...")
    bdd1 = build_bdd(lambda path: circuit.evaluate_expression(expression1, path['A'], path['B'], path['C']), variables)
    bdd_graph1 = visualize_bdd(bdd1)
    bdd2 = build_bdd(lambda path: circuit.evaluate_expression(expression2, path['A'], path['B'], path['C']), variables)
    bdd_graph2 = visualize_bdd(bdd2)

    robdd1 = reduce_bdd(bdd1)
    robdd_graph1 = visualize_robdd(robdd1)
    robdd2 = reduce_bdd(bdd2)
    robdd_graph2 = visualize_robdd(robdd2)

    while True:
        print("\n--- Boolean Function Analysis ---")
        print("1. Display Truth Table for Expression 1")
        print("2. Display Truth Table for Expression 2")
        print("3. Visualize BDD for Expression 1")
        print("4. Visualize BDD for Expression 2")
        print("5. Visualize ROBDD for Expression 1")
        print("6. Visualize ROBDD for Expression 2")
        print("7. Check Equivalence of Expressions")
        print("8. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            circuit.truth_table(expression1)
        elif choice == '2':
            circuit.truth_table(expression2)
        elif choice == '3':

            bdd_graph1.render("bdd1_diagram", format="png", cleanup=True)
            print("BDD for Expression 1 saved as bdd1_diagram.png.")
        elif choice == '4':
            bdd_graph2.render("bdd2_diagram", format="png", cleanup=True)
            print("BDD for Expression 2 saved as bdd2_diagram.png.")
        elif choice == '5':

            robdd_graph1.render("robdd1_diagram", format="png", cleanup=True)
            print("ROBDD for Expression 1 saved as robdd1_diagram.png.")
        elif choice == '6':

            robdd_graph2.render("robdd2_diagram", format="png", cleanup=True)
            print("ROBDD for Expression 2 saved as robdd2_diagram.png.")
        elif choice == '7':
            if equivalent_subtrees(robdd1, robdd2):
                print("The two Boolean functions are equivalent.")
            else:
                print("The two Boolean functions are NOT equivalent.")
        elif choice == '8':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
