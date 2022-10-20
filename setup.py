from setuptools import setup


setup(
    name='Caiasoft-Python-SDK',
    description='Python tools for building K-State Libraries related applications',
    url='https://github.com/kstatelibraries/ksul-sdk-python',
    author='Kansas State University Libraries',
    author_email='admin@pennlabs.org',
    version='0.1.0',
    packages=['caiasoft'],
    license='MIT',
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        # 'penn': ['data/laundry.csv'],
    },
    long_description=open('./README.md').read(),
    install_requires=[
        'requests',
    ]
)
