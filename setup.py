from setuptools import setup, find_packages

# This setup file is designed for the 'src' layout.
# It ensures that all files inside 'src' are packaged correctly,
# allowing you to use absolute imports like 'from authentication.service import...'
# after the package is installed (even in editable mode).
setup(
    # The name of the installed package. This is what you would see in 'pip list'.
    name='localfreelanceportal', 
    version='0.1.0',
    description='Authentication microservice for Local Freelance Portal.',
    author='Your Name',
    
    # CRITICAL: This line tells Python to look inside the 'src' directory
    # when attempting to resolve package imports.
    package_dir={'': 'src'}, 
    
    # This automatically finds all Python packages (folders containing __init__.py)
    # inside the 'src' directory (e.g., it will find 'authentication').
    packages=find_packages(where='src'), 
    
    # Basic dependencies inferred from your project (FastAPI setup)
    install_requires=[
        'fastapi',
        'uvicorn[standard]',
        'pydantic',
        'passlib[bcrypt]',
        'python-jose[cryptography]',
        'motor', # Assuming MongoDB driver based on context
    ],
    
    # Set up development and testing dependencies
    extras_require={
        'dev': ['pytest', 'httpx', 'mypy', 'flake8'],
    },
    
    include_package_data=True,
    python_requires='>=3.11',
)
