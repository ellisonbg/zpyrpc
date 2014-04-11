from setuptools import setup, find_packages

setup(
    name = "zpyrpc",
    version = "0.1",
    packages = find_packages(),

    install_requires = ['tornado','pyzmq'],

    author = "Brian Granger",
    author_email = "ellisonbg@gmail.com",
    description = "Zippy fast and simple RPC based on ZeroMQ and Python",
    license = "Modified BSD",
    keywords = "ZeroMQ Tornado PyZMQ",
    url = "http://github.com/ellisonbg/zpyrpc",
    use_2to3 = True,
)
