import setuptools

setuptools.setup(
    name='hubploy',
    version='0.1.0',
    url="https://github.com/yuvipanda/hubploy",
    author="Yuvi Panda",
    packages=setuptools.find_packages(),
    install_requires=[
        'docker',
        'jupyter-repo2docker>=0.8',
    ],
    entry_points={
        'console_scripts': [
            'hubploy = hubploy.__main__:main',
        ],
    },

)
