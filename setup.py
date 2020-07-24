from setuptools import setup

setup(name='uswapper',
      version='0.31',
      description='Simple wrapper for uniswap graphql api',
      license='MIT',
      packages=['uswapper'],
      install_requires=[
              'pandas',
              'requests',
              'python_graphql_client',
              'six'
              ],
      zip_safe=False)
