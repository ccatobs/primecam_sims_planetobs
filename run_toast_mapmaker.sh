#!/bin/bash
export OMP_NUM_THREADS=2

echo "$(which python)"
echo "$(python --version)"

###################
####  CONFIG   ####
###################

### for arc10 tests
INDIR='planet_WNdata_d100'
OUTDIR='jupiter_maps'

PARENT_DIR="ccat_datacenter_mock"
DATA_DIR="mockdata"
MAP_DIR="fb_maps"
FULL_DATA_PATH="${PARENT_DIR}/${DATA_DIR}"
FULL_MAP_PATH="${PARENT_DIR}/${MAP_DIR}"

FULL_INDIR="${FULL_DATA_PATH}/${INDIR}"
FULL_OUTDIR="${FULL_MAP_PATH}/${OUTDIR}"
GRP_SIZE=24
MAP_PREFIX='jupiter'
NOTES=''
###################

echo "***** EXEC SCRIPT *****"
echo `date '+%F %H:%M:%S'`
echo "***********************"
echo ""

### Build Map
echo ""
echo "Processing Filter and Bin Pipeline..."
echo ""
mpirun -np 48 python write_toast_maps.py -in $FULL_INDIR -out $FULL_OUTDIR -g $GRP_SIZE -p $MAP_PREFIX -n "$NOTES"

echo ""
echo "******** DONE *********"
echo `date '+%F %H:%M:%S'`
echo "***********************"
