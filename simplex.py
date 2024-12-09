from scipy.optimize import linprog
import numpy as np
import time

def check_constraints_feasibility(constraints):
    """
    Checks if a set of constraints is feasible using a dummy objective function.

    Parameters:
        constraints: List of tuples representing constraints in the format:
                     (coef1, coef2, ..., constant), interpreted as:
                     coef1 * x1 + coef2 * x2 + ... + constant >= 0.

    Returns:
        Boolean indicating whether the constraints are feasible.
    """
    try:
        # Start timer
        start_time = time.time()

        # Reformat constraints for Simplex
        A_ub = []
        b_ub = []

        for constraint in constraints:
            *coefficients, constant = constraint
            A_ub.append([-coef for coef in coefficients])  # Negate coefficients
            b_ub.append(-constant)  # Negate constant

        # Convert to numpy arrays
        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)

        # Use a dummy objective function (all zeros) since we only care about feasibility
        num_vars = len(A_ub[0])  # Number of variables
        dummy_function = [0] * num_vars

        # Set variable bounds (default: [0, 10] for all variables)
        var_bounds = [(0, 10)] * num_vars

        # Use Simplex to check feasibility
        result = linprog(dummy_function, A_ub=A_ub, b_ub=b_ub, bounds=var_bounds, method='highs')

        # Check if the optimization was successful
        if result.success:
            print(f"Constraints are feasible. Checked in {time.time() - start_time:.6f} seconds.")
            return True
        else:
            print(f"Constraints are not feasible. Reason: {result.message}")
            return False

    except Exception as e:
        print(f"Error in check_constraints_feasibility: {e}")
        return False
