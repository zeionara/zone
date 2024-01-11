from setuptools import setup, find_packages

setup(
    name='ozonzone',
    version='0.0.1',
    license='Apache 2.0',
    author='Zeio Nara',
    author_email='zeionara@gmail.com',
    packages=find_packages(),
    description='Online store price monitor',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/zeionara/zone',
    project_urls={
        'Documentation': 'https://github.com/zeionara/zone#readme',
        'Bug Reports': 'https://github.com/zeionara/zone/issues',
        'Source Code': 'https://github.com/zeionara/zone'
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11"
    ],
    install_requires = ['click', 'requests', 'pandas', 'selenium', 'webdriver-manager', 'undetected-chromedriver', 'python-telegram-bot']
)
