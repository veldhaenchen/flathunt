#!/bin/bash

set -eu

pip install -r requirements.txt

pylint_runner
pylint_runner_exit_code=$?

# https://pylint.pycqa.org/en/latest/user_guide/usage/run.html#exit-codes
if [ $(( $pylint_runner_exit_code & 32 )) != 0 ] || # usage error
   [ $(( $pylint_runner_exit_code & 16 )) != 0 ] || # convention message issued
   # [ $(( $pylint_runner_exit_code & 8 )) != 0 ] || # refactor message issued -> considered okay, therefore ignored
   # [ $(( $pylint_runner_exit_code & 4 )) != 0 ] || # warning message issued -> considered okay, therefore ignored
   [ $(( $pylint_runner_exit_code & 2 )) != 0 ] || # error message issued
   [ $(( $pylint_runner_exit_code & 1 )) != 0 ] # fatal message issued
then
  echo "Looks bad; exit code $pylint_runner_exit_code"
  exit $pylint_runner_exit_code
fi

echo "Looking good!"
exit 0