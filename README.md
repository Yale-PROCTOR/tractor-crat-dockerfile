To build and run the container:

```bash
./download.sh
docker build -t tractor-crat:latest .
docker run -it tractor-crat:latest
```

Inside the container:

```bash
./translate_all.py
```

To translate an individual test case:

```bash
./translate.sh Public-Tests/B01_organic/bin2hex_lib
```

To run tests:

```bash
./deployment/scripts/github-actions/run_rust.sh --keep-going -m B01 -m P00 -m P01
```
