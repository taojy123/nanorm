from setuptools import setup
import nanorm


try:
    long_description = open('README.md').read()
except Exception as e:
    long_description = ''


setup(
    name='nanorm',
    py_modules=['nanorm', 'nanorm_example'],
    version=nanorm.__VERSION__,
    keywords='orm namo mini sample database sqlite nanorm nanoorm',
    description='A simple ORM framework for Python ( Nano ORM )',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tao Jiayuan",
    author_email="taojy123@163.com",
    license="MIT",
    url="https://github.com/taojy123/nanorm",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)

