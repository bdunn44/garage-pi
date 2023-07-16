#!/bin/bash
SCRIPT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
(cd $SCRIPT_PATH/.. && python3 -m src)