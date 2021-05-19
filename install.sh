git clone https://github.com/oduwsdl/sumgram.git /tmp/sumgram
(cd /tmp/sumgram; sed 's/numpy==1.17.0/numpy/g' setup.py > setup.py.new; mv setup.py.new setup.py; pip install . --use-feature=in-tree-build)

pip install .  --use-feature=in-tree-build
