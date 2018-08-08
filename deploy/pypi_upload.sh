export TWINE_USERNAME=${PYPI_USER}
export TWINE_PASSWORD=${PYPI_PASSWD}

pip install -U twine && python setup.py sdist
twine upload --skip-existing dist/*
