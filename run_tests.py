import unittest
import os

# Create tests directory if it doesn't exist
if not os.path.exists('tests'):
    os.makedirs('tests')
    # Create an __init__.py file to make the directory a package
    with open('tests/__init__.py', 'w') as f:
        pass

# Discover and run all tests
loader = unittest.TestLoader()
start_dir = './tests'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print(f"Tests run: {result.testsRun}")
print(f"Errors: {len(result.errors)}")
print(f"Failures: {len(result.failures)}")