cythonize -i ./saf/framework.py ./saf/io.py ./saf/theories.py ./saf/utils.py ./saf/tasks.py ./saf/argument.py
cython ./saf/__main__.py --embed -X language_level=3
gcc -Os -I /usr/include/python3.8 -o solved-af-static ./saf/__main__.c -lpython3.8 -lpthread -lm -lutil -ldl

./clean.sh