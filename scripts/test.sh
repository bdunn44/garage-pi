#!/bin/bash
SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
if [[ $1 == "ble" || $1 == "climate" || $1 == "video" ]]
then
    (cd "$SCRIPT_PATH/.." && python3 -m src.$1)
else
    echo "Usage: test.sh [ble|climate|video]"
    exit 1
fi
exit 0