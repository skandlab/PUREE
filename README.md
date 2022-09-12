# PUREE
Steps to install Puree:
1. python setup.py bdist_wheel
2. pip install dist/puree-0.1.0-py3-none.any.whl --force-reinstall

Now you can use the following:
```
from puree import *
p = Puree()
p.get_output(TEST_DATA_PATH, 'ENSEMBL', 'PUREE_genes')
```