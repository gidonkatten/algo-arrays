#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

gcmd="goal -d ../../net1/Primary"
MAIN=$(${gcmd} account list|awk '{ print $3 }'|tail -1)

APP_ID=1

INDEX=7

# create transactions
${gcmd} app call -f "$MAIN" \
  --app-id "$APP_ID" \
  --app-arg "str:is_int_odd" \
  --app-arg "int:$INDEX"
