#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

gcmd="goal -d ../../net1/Primary"
MAIN=$(${gcmd} account list|awk '{ print $3 }'|tail -1)

TEAL_APPROVAL_PROG="../../contracts/booleans.teal"
TEAL_ESCROW="../../contracts/booleans.teal"
APP_ID=14

INDEX=127
TRUE=1
FALSE=0

# create transactions
${gcmd} app call -f "$MAIN" \
  --app-id "$APP_ID" \
  --app-arg "str:set_bool" \
  --app-arg "int:$INDEX" \
  --app-arg "int:$TRUE"

# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$MAIN"
