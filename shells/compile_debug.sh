#! /bin/bash

# --- useage ---
function usage()
{
cat <<- EOT
    Useage:$0 [options] [--]
    Options:
        -c|common       common branch
        -v|vehicle      algo_vehicle_slam branch
        -s|server       algo_sam branch
        -h|help         Display this message

    Example:
        ./compile_debug.sh -c master -v master -s master
EOT
}

get_status()
{
    if [ $? -eq 0 ];then
            echo "$1 $2 success!"
    else
            echo "$1 $2 fail!"
            exit 1
    fi
}

#get arguments
while getopts "c:v:s:h" opt
do
    case $opt in
        c|common)
            echo "common branch is $OPTARG"
            COMMON_BARNCH=$OPTARG
        ;;
        v|vehicle)
            echo "algo_vehicle_slam branch is $OPTARG"
            ALGO_VEHICLE_SLAM_BRANCH=$OPTARG
        ;;
        s|server)
            echo "algo_sam branch is $OPTARG"
            ALGO_SAM_BARNCH=$OPTARG
        ;;
        h|help)
            usage
            exit 0
        ;;
        ?)
            echo "error"
            exit 1
        ;;
    esac
done

#get current path and module path
CURRENT_PATH=$(cd "$(dirname "$0")";pwd)
COMMON_PATH=$CURRENT_PATH/common
GMOCK_PATH=$CURRENT_PATH/framework/device/gmock
ROADDB_LOGGER_PATH=$CURRENT_PATH/framework/device/roaddb_logger
ROADDB_VIDEO_PATH=$CURRENT_PATH/framework/device/roaddb_video
CORE_COMMON_PATH=$CURRENT_PATH/core/common
CORE_ALGO_COMMON_PATH=$CURRENT_PATH/core/algorithm_common
ALGO_VEHICLE_SLAM_PATH=$CURRENT_PATH/core/algorithm_vehicle_slam
ALGO_SAM_PATH=$CURRENT_PATH/core/algorithm_sam
VEHICLE_PATH=$CURRENT_PATH/core/vehicle

PATH_LIST=(
$COMMON_PATH
$GMOCK_PATH
$ROADDB_LOGGER_PATH
$ROADDB_VIDEO_PATH
$CORE_COMMON_PATH
$CORE_ALGO_COMMON_PATH
$ALGO_VEHICLE_SLAM_PATH
$ALGO_SAM_PATH
$VEHICLE_PATH
)
#start git pull
echo "the current path is $CURRENT_PATH"
echo "==== Start git pull ===="
for module in ${PATH_LIST[@]};
do
    echo "=== git pull ${module##*/} ==="
    if [ $module = $ALGO_VEHICLE_SLAM_PATH ]
    then
        cd $module && git checkout $ALGO_VEHICLE_SLAM_BRANCH && git pull
    elif [ $module = $ALGO_SAM_PATH ]
    then
        cd $module && git checkout $ALGO_SAM_BARNCH && git pull
    else
        cd $module && git checkout $COMMON && git pull
    fi
    get_status "git pull" ${module##*/}
done

#start build
for module in ${PATH_LIST[@]};
do
    echo "=== Build ${module##*/} ==="
    if [ $module = $ALGO_VEHICLE_SLAM_PATH ]
    then
        cd $module"/example" && ./main.sh -d
    elif [[ $module = $ALGO_SAM_PATH || $module = $CORE_ALGO_COMMON_PATH ]]
    then
        cd $module && ./build.sh -g
    elif [ $module = $VEHICLE_PATH ]
    then
        echo "=== skip build ${module##*/} ==="
        continue
    else
        cd $module && ./build.sh
    fi
    get_status "build" ${module##*/}
done

echo "==== Build End ===="

