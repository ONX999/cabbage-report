"""
安裝配置檔案
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cabbage-report",
    version="0.1.0",
    author="ONX999",
    author_email="",
    description="自動化甘藍品種批發/零售價格報表產生器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ONX999/cabbage-report",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pylint>=3.0",
            "black>=23.0",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cabbage-report=cabbage_report.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)