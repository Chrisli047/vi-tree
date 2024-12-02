from copy import deepcopy

import cdd
import numpy as np

from sqlite_utils import read_from_sqlite


def generate_constraints(n, var_min, var_max):
    """
    Generate constraints for an n-dimensional space with var_min and var_max.
    Returns a list of tuples in the format (coe1, coe2, ..., coen, constant).
    # Define inequalities in the form A x + b > 0
    """
    constraints = []

    for i in range(n):
        # Lower bound: x_i >= var_min -> x_i - var_min >= 0
        lower_bound = [0] * n
        lower_bound[i] = 1
        constraints.append((*lower_bound, -var_min))

        # Upper bound: x_i <= var_max -> -x_i + var_max >= 0
        upper_bound = [0] * n
        upper_bound[i] = -1
        constraints.append((*upper_bound, var_max))

    return constraints

def compute_vertices(constraints):
    # Define inequalities in the form A x + b > 0

    """
    Compute vertices for the initial domain from a list of constraints.
    Constraints are in the format (coe1, coe2, ..., constant).
    """
    try:
        rows = []
        for constraint in constraints:
            # Split the tuple into coefficients (A[i]) and the constant (b[i])
            *coefficients, constant = constraint
            row = [constant] + coefficients  # Include constant as the first element
            rows.append(row)

        # Convert to cdd matrix
        mat = cdd.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)

        # Create polyhedron from the matrix
        poly = cdd.polyhedron_from_matrix(mat)
        ext = cdd.copy_generators(poly)

        vertices = []
        for row in ext.array:
            if row[0] == 1.0:  # This indicates a vertex
                vertex = [round(coord, 4) for coord in row[1:]]
                vertices.append(vertex)

        return vertices
    except Exception as e:
        print(f"Error in compute_vertices: {e}")
        return []


def check_function(func, vertices, threshold=1e-6) -> bool:
    """
    Checks if the function AX = b has vertices that satisfy both AX < b and AX > b.

    Parameters:
        func (tuple): A tuple in the format (coe1, coe2, ..., coed, constant).
        vertices (list): List of vertices to evaluate.
        threshold (float): Tolerance for considering a vertex close to the plane AX = b.

    Returns:
        bool: True if there exist vertices with AX < b and AX > b; False otherwise.
    """
    *coefficients, constant = func  # Unpack coefficients and constant

    # Convert coefficients to a NumPy array for vectorized operations
    coefficients_array = np.array(coefficients)

    positive_found = False
    negative_found = False

    for vertex in vertices:
        # Convert vertex to a NumPy array
        vertex_array = np.array(vertex)

        # Evaluate AX - b for the current vertex
        value = np.dot(coefficients_array, vertex_array) - constant

        # Ignore values close to zero (threshold region around AX = b)
        if abs(value) < threshold:
            continue

        # Check for positive and negative signs
        if value > 0:
            positive_found = True
        elif value < 0:
            negative_found = True

        # If both positive and negative values are found, return True
        if positive_found and negative_found:
            return True

    # If no crossing is found, return False
    return False


def merge_constraints(node_constraints, init_constraints, m, n, db_name, conn):
    """
    Merge node.constraints with init_constraints by fetching records from the database.
    Parameters:
        node_constraints (list): Constraints for the current node.
        init_constraints (list): Global initial constraints.
        m (int): Number of functions.
        n (int): Dimension of functions.
        db_name (str): Database file name.
        conn: SQLite database connection.
    Returns:
        list of tuples: Merged constraints.
    """
    # Deep-copy init_constraints to avoid modifying the original
    merged_constraints = deepcopy(init_constraints)


    for record_id in node_constraints:
        # Fetch record from the database
        if record_id < 0:
            record = read_from_sqlite(m=m, n=n, db_name=db_name, record_id=-record_id, conn=conn)
            # Negate coefficients, keep constant unchanged
            record = tuple(-coeff for coeff in record[:-1]) + (record[-1],)  # Convert to a tuple
        else:
            record = read_from_sqlite(m=m, n=n, db_name=db_name, record_id=record_id, conn=conn)
            # Keep coefficients, negate constant
            record = tuple(record[:-1]) + (-record[-1],)  # Convert to a tuple

        # Append the modified record as a tuple to merged_constraints
        merged_constraints.append(record)

    return merged_constraints