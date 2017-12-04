from setuptools import setup
import nanorm

setup(name='nanorm',
      py_modules=['nanorm', 'nanorm_test'],
      version=nanorm.__VERSION__,
      keywords='orm namo mini sample database sqlite nanorm nanoorm',
      description='A simple ORM framework for Python ( Nano ORM )',
      long_description=open('description.txt').read(),
      author="Tao Jiayuan",
      author_email="taojy123@163.com",
      license="MIT",
      url="https://github.com/taojy123/nanorm",
      )

