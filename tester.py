import ast
import operator
from typing import Any, Union

# Supported binary comparison operators
operators: dict[type, Any] = {
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
}


def safe_eval(expr: str, value: Union[int, float]) -> bool:
    """
    Safely evaluate a comparison expression with 'N' as a variable.

    Supports chained comparisons like "3 < N > 5".

    Args:
        expr: A string containing a comparison expression.
        value: A numeric value to substitute for 'N'.

    Returns:
        True if the expression evaluates to True, else False.

    Raises:
        ValueError: If the expression is invalid or unsupported.
    """
    try:
        node = ast.parse(expr, mode='eval').body

        if not isinstance(node, ast.Compare):
            raise ValueError("Only comparison expressions are supported.")

        # Resolve the left operand of the first comparison
        def resolve_operand(operand_node: ast.expr) -> Union[int, float]:
            if isinstance(operand_node, ast.Name) and operand_node.id == 'N':
                return value
            elif isinstance(operand_node, ast.Constant):  # Python 3.8+
                if isinstance(operand_node.value, (int, float)):
                    return operand_node.value
                else:
                    raise ValueError("Only numeric constants are supported.")
            else:
                raise ValueError("Unsupported operand type.")

        left_value = resolve_operand(node.left)

        for op, right in zip(node.ops, node.comparators):
            right_value = resolve_operand(right)

            op_type = type(op)
            if op_type not in operators:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")

            if not operators[op_type](left_value, right_value):
                return False  # Short-circuit if any comparison fails

            # Prepare for next chained comparison
            left_value = right_value

        return True

    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")



print(safe_eval("12 <= N >= 60", 61))  # True
