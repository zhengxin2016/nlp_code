#!/usr/bin/env bash

dirpath='/home/zhengxin/shared/'

copy_fun(){
        path='data'
        if [[ ! -d $path ]]; then
                mkdir $path
        fi
        spath='0-'$1
        dpath='data/'$1
        if [[ -d $dirpath$spath ]]; then
                if [[ -d $dpath ]]; then
                        rm $dpath -fr
                fi
                cp $dirpath$spath $dpath -r
                git add $dpath --ignore-removal
        else
                echo $spath' no exist!'
        fi
}

copy_fun $1
echo $1' end...'

