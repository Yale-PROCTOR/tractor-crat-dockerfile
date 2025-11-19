```bash
./download.sh
docker build -t tractor-crat:latest .
docker run -it tractor-crat:latest
```

Inside the container:

```bash
cd Test-Corpus
./translate_all.py
```

To translate an individual test case:

```bash
./translate.sh Public-Tests/B01_organic/bin2hex_lib
```

To run tests:

```bash
./deployment/scripts/github-actions/run-tests.pyz --keep-going --rust
```
