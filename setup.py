"""Setup script for helios-intercropping package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "PyHelios-based intercropping scene generation pipeline"

setup(
    name="helios-intercropping",
    version="1.0.0",
    author="Nelson",
    description="Photorealistic RGB/multispectral image generation for intercropping research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/helios-intercropping",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.3.0",
        "matplotlib>=3.4.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.6b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "helios-intercrop=scripts.generate_scene:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="pyhelios agriculture intercropping synthetic-data computer-vision",
)
