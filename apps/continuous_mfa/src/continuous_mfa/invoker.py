import importlib
import importlib.util

def invoker(module_name, function_name, parameters=None):
    """
    Dynamically invoke a function from a specified module.

    Args:
        module_name (str): The name of the module to import.
        function_name (str): The name of the function to call.
        parameters (list, optional): A list of parameters to pass to the function.

    Returns:
        The result of the function call.
    """
    # Dynamically import the module
    module = importlib.import_module(module_name)
    
    # Retrieve the function from the module
    func = getattr(module, function_name)
    
    # Call the function with or without parameters
    if parameters is None:
        return func()
    else:
        return func(*parameters)

def module_function_exists(module_name, function_name):
    """
    Check whether a module and a function within that module exist.

    Args:
        module_name (str): The name of the module.
        function_name (str): The name of the function.

    Returns:
        bool: True if the module exists and contains the function, False otherwise.
    """
    # Check if the module exists using its spec.
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False
    
    # Import the module and check for the function attribute
    module = importlib.import_module(module_name)
    return hasattr(module, function_name)

def safe_invoke(module_name, function_name, parameters=None):
    """
    Safely invoke a function by checking if the module and function exist.

    Args:
        module_name (str): The name of the module.
        function_name (str): The name of the function.
        parameters (list, optional): A list of parameters to pass to the function.

    Returns:
        The result of the function call if successful, or None if the module or function does not exist.
    """
    if not module_function_exists(module_name, function_name):
        print(f"Module '{module_name}' or function '{function_name}' not found.")
        return None

    # If the module and function exist, invoke the function
    return invoker(module_name, function_name, parameters)

# Example Usage:
if __name__ == "__main__":
    # Example 1: Calling math.sqrt with a parameter of 16.
    result = safe_invoke("math", "sqrt", [16])
    if result is not None:
        print("Result of math.sqrt(16):", result)  # Expected output: 4.0

    # Example 2: Attempt to call a non-existent function in the math module.
    result = safe_invoke("math", "non_existent_function")
    if result is None:
        print("Call failed due to missing module/function.")

    # Example 3: Calling a function without parameters from the random module.
    random_value = safe_invoke("random", "random")
    if random_value is not None:
        print("Result of random.random():", random_value)
