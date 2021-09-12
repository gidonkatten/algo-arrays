#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

PYTHON=python3
gcmd="goal -d ../../net1/Primary"
MAIN=$(${gcmd} account list|awk '{ print $3 }'|tail -1)

PYTEAL_APPROVAL_PROG="../../contracts/strings.py"
PYTEAL_CLEAR_PROG="../../contracts/clear.py"
TEAL_APPROVAL_PROG="../../contracts/strings.teal"
TEAL_CLEAR_PROG="../../contracts/clear.teal"

# compile PyTeal into TEAL
"$PYTHON" "$PYTEAL_APPROVAL_PROG" > "$TEAL_APPROVAL_PROG"
"$PYTHON" "$PYTEAL_CLEAR_PROG" > "$TEAL_CLEAR_PROG"

# create app
ARRAY_LENGTH=4
APP_ID=$(
  ${gcmd} app create --creator "$MAIN" \
    --approval-prog "$TEAL_APPROVAL_PROG" \
    --clear-prog "$TEAL_CLEAR_PROG" \
    --global-byteslices "$ARRAY_LENGTH" \
    --global-ints 1 \
    --local-byteslices 0 \
    --local-ints 0 |
    grep Created |
    awk '{ print $6 }'
)
echo "App ID = $APP_ID"

# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$MAIN"
