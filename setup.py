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
        'click==8.0.3',
        'numpy==1.21.2',
        'opencv-python==4.5.3.56',
        'python-dotenv==0.19.1',
        'pyzmq==22.3.0',
        'zmq==0.0.0'
    ],
    entry_points={
        'console_scripts': [
            'fq = FQ.cli:main'
        ]
    }
)
