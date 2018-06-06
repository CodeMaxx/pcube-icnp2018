#!/bin/bash

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


###--- Setup Environment
rm distributed_stateful_load_balancer_$1.json
sudo rm -f *.pcap
sudo mn -c
THIS_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

source $THIS_DIR/../../../../env.sh

P4C_BM_SCRIPT=$P4C_BM_PATH/p4c_bm/__main__.py

SWITCH_PATH=$BMV2_PATH/targets/simple_switch/simple_switch

# CLI_PATH=$BMV2_PATH/tools/runtime_CLI.py
CLI_PATH=$BMV2_PATH/tools/modified_runtime_CLI.py
# CLI_PATH=$BMV2_PATH/targets/simple_switch/sswitch_CLI.py


###--- Read topo, create json dump of topology
python topo_to_json.py

###--- Generate p4 for all switches from ip4
python3 generate_p4.py distributed_stateful_load_balancer_merged.ip4

###--- Generate commands for sending packets to lowest load server
# 5 is Threshold here
python generate_commands.py merged 5

###--- Generate sync_commands.txt
python generate_sync_commands.py

###--- Create P4 for each switch; format : "<filename>_<switch_id>.p4"
# python3 p4src/generate_p4.py p4src/distributed_stateful_load_balancer_$1.ip4

###--- Compile p4 for all switches
for j in `seq 1 $2`
do
    $P4C_BM_SCRIPT p4src/distributed_stateful_load_balancer_$1_$j.p4 --json distributed_stateful_load_balancer_$1_$j.json
    sudo $SWITCH_PATH >/dev/null 2>&1
done

###--- Burn json for each switch individually using topo.py
sudo PYTHONPATH=$PYTHONPATH:$BMV2_PATH/mininet/ python topo.py \
    --behavioral-exe $SWITCH_PATH \
    --json distributed_stateful_load_balancer_$1 \
    --cli $CLI_PATH
