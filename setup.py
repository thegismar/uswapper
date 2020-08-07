from setuptools import setup

setup(name='uswapper',
      version='1.5',
      description='Simple wrapper for uniswap graphql api',
      license='MIT',
      packages=['uswapper'],
      install_requires=[
              'pandas',
              'requests==2.22.0',
              'python_graphql_client',
              'urllib3'
              ],
      zip_safe=False)
