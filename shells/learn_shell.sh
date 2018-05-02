#! /bin/bash

for k in Hello World;do
    echo "I am ${k}"
done

a="imojbk"
readonly a
echo ${a:1:4}

a_list=(
$h=1
$h1=2
$h2=3)
echo $h
echo ${a_list[@]}
length=${#a_list[@]}
echo ${length}

echo $1 $2 $3

echo "--\$*--"
for i in "$*";do
    echo ${i}
done

echo "--\$@--"
for i in "$@";do
    echo ${i}
done

val=`expr 2 + 23`
echo "sum is $val"

a_int=2
b_int=3
sum=`expr ${a_int} \* ${b_int}`
echo $sum

if [ $a_int == $b_int ]
then
    echo "a = b"
fi

if [ $a_int != $b_int ]
then
    echo "a != b"
fi

if [ $a_int -eq $b_int ]
then
    echo "a != b"
else
    echo "a = b"
fi