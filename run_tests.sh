#!/bin/bash
set -e

DIR=$(dirname $(realpath "$0")) 	# locate folder where this sh-script is located in
SCRIPT_DECOMPOSITION="./tests/run_tests_decomposition.inp"
PACKAGE_NAME="decomposition"

cd $DIR
echo "Switched to ${DIR}"

gretlcli -b -e -q ${SCRIPT_DECOMPOSITION}

if [ $? -eq 0 ]
then
  echo "Success: All tests passed for '${PACKAGE_NAME}'."
  exit 0
else
  echo "Failure: Tests not passed for '${PACKAGE_NAME}'." >&2
  exit 1
fi

