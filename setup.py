from setuptools import setup, find_packages
from typing import List 

HYPEN_E_DOT='-e .'
def read_requirements(file_path: str) -> List[str]:
    requirements = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                if line == HYPEN_E_DOT:
                    continue
                requirements.append(line)
    return requirements

setup(
    name='myFinal project Sepsis Survival & Risk Prediction Platform', 
    version='0.1.0',
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'), 
    author='Lakshman',
    author_email='lakshman9103@gmai.com'
)