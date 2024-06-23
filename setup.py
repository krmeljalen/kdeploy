from setuptools import setup, find_packages

setup(
    name="kdeploy",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    scripts=["bin/kdeploy"],
    entry_points={
        "console_scripts": [
            "kdeploy = kdeploy.core:run",
        ],
    },
    install_requires=["docker==7.1.0", "PyYAML==5.4.1"],
    author="Alen Krmelj",
    author_email="krmelj.alen@gmail.com",
    description="A brief description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/krmeljalen/kdeploy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
