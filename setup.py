from setuptools import setup, find_packages

setup(
    name='authentication-service-pkg',
    version='0.1.0',
    # 1. IMPORTANT: Tell Python that the packages it should install are 
    #    physically located inside the 'src' subdirectory.
    package_dir={'': 'src'}, 
    
    # 2. Find ALL packages within the directory specified by package_dir,
    #    which is 'src' in this case. The top-level 'test' directory is ignored.
    packages=find_packages(where='src'), 
    
    # You can add other configurations like dependencies here later:
    # install_requires=['fastapi', 'uvicorn', 'pydantic'],
    include_package_data=True,
)