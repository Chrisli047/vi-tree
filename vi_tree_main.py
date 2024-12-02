import argparse
from sqlite_utils import read_from_sqlite, get_all_ids
from function_utils import generate_constraints, compute_vertices, check_function
from tqdm import tqdm  # Import the progress bar library
import time  # Import time for measuring execution
import sqlite3

from vi_tree import VITree

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process VI tree with given m and n.")
    parser.add_argument("m", type=int, help="Number of functions (m)")
    parser.add_argument("n", type=int, help="Dimension of functions (n)")
    parser.add_argument("--db", type=str, default="intersections.db", help="Database file (default: intersections.db)")
    parser.add_argument("--var_min", type=float, default=0, help="Minimum value for variables (default: 0)")
    parser.add_argument("--var_max", type=float, default=10, help="Maximum value for variables (default: 10)")
    args = parser.parse_args()

    m = args.m
    n = args.n
    db_name = args.db
    var_min = args.var_min
    var_max = args.var_max

    # Dynamically construct the table name
    table_name = f"intersections_m{m}_n{n}"

    # Open a single connection to the database
    conn = sqlite3.connect(db_name)

    # Get all IDs from the table
    ids = get_all_ids(m, n, db_name=db_name)
    print(f"Found {len(ids)} IDs in table {table_name}.")

    # Generate constraints using n (as dimensionality), var_min, and var_max
    constraints = generate_constraints(n, var_min, var_max)
    print("Generated constraints as tuples:")
    for constraint in constraints:
        print(constraint)

    # Compute vertices for the initial domain
    vertices = compute_vertices(constraints)
    print(f"Computed vertices of the initial domain: {vertices}")

    # Initialize the VI Tree
    vi_tree = VITree()

    # Fetch and process records by ID
    print("Processing records:")
    # Start the timer
    start_time = time.time()

    # Insert records into the VI Tree with progress tracking
    for record_id in tqdm(ids, desc="Processing Records", unit="record"):
        record = read_from_sqlite(m, n, conn=conn, record_id=record_id)
        if check_function(record, vertices):
            # print(f"Record with ID {record_id} satisfies the condition: {record}")
            # Insert the record into the VI Tree
            vi_tree.insert(record_id, constraints, vertices, m=m, n=n, db_name=db_name, conn=conn)

    # Stop the timer
    end_time = time.time()

    # Print the time taken to insert all records
    print(f"Time taken to insert all records into the VI Tree: {end_time - start_time:.2f} seconds")

    # print("\nVI Tree Structure (Layer by Layer with Records):")
    # vi_tree.print_tree_by_layer(m, n, db_name, conn)

    # Print the height of the tree
    print(f"Height of the VI Tree: {vi_tree.get_height()}")

    # Print the number of leaf nodes
    print(f"Number of leaf nodes in the VI Tree: {vi_tree.get_leaf_count()}")

    # Close the database connection
    conn.close()
    print("Database connection closed.")
