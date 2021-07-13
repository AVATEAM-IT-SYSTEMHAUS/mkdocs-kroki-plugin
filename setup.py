from setuptools import setup, find_packages
from pathlib import Path

# read the contents of your README file
PROJ_DIR = Path(__file__).resolve().parent
with open(PROJ_DIR / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mkdocs-kroki-plugin',
    version='0.2.0',
    description='MkDocs plugin for Kroki-Diagrams',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='mkdocs python markdown kroi diagram',
    url='https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin',
    author='Benjamin Bittner',
    author_email='benjamin.bittner@avateam.com',
    license='MIT',
    python_requires='>=3.6',
    install_requires=[
        'mkdocs>=1.1.2'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'kroki = kroki.plugin:KrokiPlugin'
        ]
    }
)
