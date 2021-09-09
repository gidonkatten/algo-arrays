#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

gcmd="goal -d ../../net1/Primary"
MAIN=$(${gcmd} account list|awk '{ print $3 }'|tail -1)

APP_ID=1

INDEX=3
VALUE="This is a string that will be placed in an array"

# create transactions
${gcmd} app call -f "$MAIN" \
  --app-id "$APP_ID" \
  --app-arg "str:set_string" \
  --app-arg "int:$INDEX" \
  --app-arg "str:$VALUE"

# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$MAIN"
