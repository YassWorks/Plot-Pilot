import sys
import os
import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def run_code(code_str, data_path, output_image_path):
    """Executes the provided code string safely."""
    try:
        # Prepare the execution context
        # Make pandas available to the executed code under the name 'pd'
        # Make numpy available as 'np', matplotlib.pyplot as 'plt', seaborn as 'sns'
        # Provide the data_path variable
        local_vars = {
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns,
            "data_path": data_path,
            "output_image_path": output_image_path,
            # Add any other variables/modules the generated code might need
        }
        global_vars = {}  # Keep globals separate

        # Execute the code
        exec(code_str, global_vars, local_vars)

        # --- Crucial: Ensure the plot is saved ---
        # The generated code MUST include a line like:
        # plt.savefig(output_image_path)
        # Or if using seaborn/pandas plotting wrappers, ensure they use plt internally
        # and the savefig call happens after the plot is generated.

        # Check if the file was actually saved
        if not os.path.exists(output_image_path):
            # Fallback: Try to save the current figure if the code didn't explicitly save
            if plt.get_fignums():  # Check if any figures exist
                plt.savefig(output_image_path)
            else:
                raise RuntimeError(
                    "Code executed but no plot was saved to the specified path."
                )

        print(f"Plot successfully saved to {output_image_path}")

    except Exception as e:
        print(f"Error executing generated code: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)  # Exit with error code


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python execute_code.py <path_to_code.py> <path_to_data.csv> <output_image_path.png>",
            file=sys.stderr,
        )
        sys.exit(1)

    code_file_path = sys.argv[1]
    data_file_path = sys.argv[2]
    output_path = sys.argv[3]

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(code_file_path, "r") as f:
            user_code = f.read()

        if "savefig" not in user_code:
            user_code += f"\nplt.savefig('{output_path}')"
            print("Appended plt.savefig call.", file=sys.stderr)

        run_code(user_code, data_file_path, output_path)
    except Exception as e:
        print(f"Failed to read or execute code: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
