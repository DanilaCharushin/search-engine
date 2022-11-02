![code quality](https://github.com/DanilaCharushin/search-engine/actions/workflows/code-quality.yml/badge.svg)

## Info

* Python version: `3.8`
* Django version: `3.2`
* PostgreSQL version: `13`
* Tasks processing: `dramatiq[redis]`

___

## Get started

1. Install **[Python 3.8.15](https://www.python.org/ftp/python/3.8.15/)**
3. Install **[Docker](https://www.docker.com/products/docker-desktop/)**
4. Install **[Taskfile](https://taskfile.dev)**
5. Initialize project: `task init`
6. Know more about all available tasks run `task --list`
7. Optional install **[Allure](https://github.com/allure-framework/allure2)**: `brew install allure`

To run application type `task up`

To test application type `task test`

To stop application type `task down`

To build application docker image type `task build`

Important info:

* `task lint` and `task format` uses **local** venv
* `task freeze` creates temp venv locally, install requirements.txt, freeze it and do cleanup
* If you add new python requirement, you have to run `task freeze` and then `task build` commands

## Testing

To run specific test just run `task test:concrete -- <any_part_of_test_name>`

To run only failed test type `task test:failed`

To show html coverage report run `task coverage`

To inspect tests results with allure type `task allure` (needs installed *allure*)
