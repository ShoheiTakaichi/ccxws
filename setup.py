from setuptools import setup

setup(
    name="ccxws",
    version="0.0.1",
    install_requires=[
        "websocket-client>=1.3.0",
        "ccxt>=1.85.39",
        "pydantic>=1.9.1"
    ],
    extras_require={},
    entry_points={},
)
