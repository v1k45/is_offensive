from setuptools import setup

setup(
    name="is_offensive",
    version="0.0.1",
    packages=["."],
    install_requires=["httpx"],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["is_offensive=is_offensive:main"]},
)
