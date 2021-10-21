from setuptools import find_packages, setup


setup(
    name='FQ',
    version='0.1.0',
    author='wocks1123',
    author_email='wocks1123@gmail.com',
    url='https://github.com/wocks1123/FQ',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    install_requires=[
        'click',
        'numpy',
        'opencv-python',
        'python-dotenv',
        'pyzmq',
        'zmq'
    ],
    entry_points={
        'console_scripts': [
            'fq = FQ.cli:main'
        ]
    }
)
