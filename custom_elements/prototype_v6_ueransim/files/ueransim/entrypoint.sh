#!/usr/bin/env bash

set -euo pipefail

CONFIG_DIR="/opt/prototype_master/ueransim"
UERANSIM_DIR="/UERANSIM/build"

USE_FQDN=${USE_FQDN:-no}
SST_R=${SST_R:-$SST}
SD_R=${SD_R:-$SD}

for c in ${CONFIG_DIR}/*.yaml; do
    VARS=$(grep -oP '@[a-zA-Z0-9_]+@' ${c} | sort | uniq | xargs)
    echo "Now setting these variables '${VARS}'"

    EXPRESSIONS=""
    for v in ${VARS}; do
        NEW_VAR=$(echo $v | sed -e "s#@##g")
        if [[ -z ${!NEW_VAR+x} ]]; then
            echo "Error: Environment variable '${NEW_VAR}' is not set." \
                "Config file '$(basename $c)' requires all of $VARS."
            exit 1
        fi
        EXPRESSIONS="${EXPRESSIONS};s|${v}|${!NEW_VAR}|g"
    done
    EXPRESSIONS="${EXPRESSIONS#';'}"

    sed -i "${EXPRESSIONS}" ${c}
done
echo "Done setting the configuration"
echo "### Running ueransim ###"

echo "Running gnb"
$UERANSIM_DIR/nr-gnb -c $CONFIG_DIR/gnb_config.yaml &

sleep 1

run_ue() {
    local ue_config=$1
    echo "Running ue with config ${ue_config}"
    $UERANSIM_DIR/nr-ue -c $CONFIG_DIR/${ue_config}
}

run_ue "ue_1_config.yaml"
run_ue "ue_2_config.yaml"
run_ue "ue_3_config.yaml"