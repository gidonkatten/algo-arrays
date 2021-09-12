#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

gcmd="goal -d ../../net1/Primary"
MAIN=$(${gcmd} account list|awk '{ print $3 }'|tail -1)

APP_ID=1

INDEX=64591
TRUE=1
FALSE=0

# create transactions
${gcmd} app call -f "$MAIN" \
  --app-id "$APP_ID" \
  --app-arg "str:set_bool" \
  --app-arg "int:$INDEX" \
  --app-arg "int:$TRUE"
#  --app-arg "int:$TRUE" --dryrun-dump -o dr.json

#TEAL_APPROVAL_PROG="../../contracts/booleans.teal"
#tealdbg debug "$TEAL_APPROVAL_PROG" -d dr.json --group-index 0


# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$MAIN"
