import numpy as np


def create_lookup_table(variable_range_start, variable_range_end, interval, dimensions):
    # Generate discretized values
    discretized_values = np.round(np.arange(variable_range_start, variable_range_end + interval, interval) / interval) * interval
    # Create a lookup table for all dimensions
    lookup_table = {i: set(discretized_values) for i in range(dimensions)}
    return lookup_table


def round_vertex(vertex, interval):
    """
    Round each value in the vertex to the nearest multiple of the interval.
    """
    return [round(value / interval) * interval for value in vertex]


def check_new_vertices(lookup_table, new_vertices, interval):
    """
    Check if any value in the new vertices is unvisited.

    Parameters:
    lookup_table (dict): Current lookup table of unvisited values.
    new_vertices (list of lists): New set of vertices.
    interval (float): Discretization interval.

    Returns:
    bool: True if new values are found, False otherwise.
    """
    for vertex in new_vertices:
        for i, value in enumerate(vertex):
            rounded_value = round(value / interval) * interval
            if rounded_value in lookup_table[i]:
                return True  # New value found
    return False


def update_visited(lookup_table, vertices, interval):
    """
    Update the lookup table by marking rounded values from the vertex set as visited.
    """
    for vertex in vertices:
        for i, value in enumerate(vertex):
            rounded_value = round(value / interval) * interval
            if rounded_value in lookup_table[i]:  # Mark as visited by removing from the table
                lookup_table[i].remove(rounded_value)


def process_new_vertices(lookup_table, new_vertices, interval):
    """
    Check if new vertices introduce any unvisited values, and update the lookup table if so.

    Parameters:
    lookup_table (dict): Current lookup table of unvisited values.
    new_vertices (list of lists): New set of vertices to check and potentially update.
    interval (float): Discretization interval.

    Returns:
    bool: True if new values were introduced (and the table updated), False otherwise.
    """
    if check_new_vertices(lookup_table, new_vertices, interval):
        update_visited(lookup_table, new_vertices, interval)
        return True
    return False
