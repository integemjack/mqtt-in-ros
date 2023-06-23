#!/bin/bash

# Get_Dist_Name()
# {
#     if grep -Eqii "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release; then
#         DISTRO='CentOS'
#         PM='yum'
#     elif grep -Eqi "Red Hat Enterprise Linux Server" /etc/issue || grep -Eq "Red Hat Enterprise Linux Server" /etc/*-release; then
#         DISTRO='RHEL'
#         PM='yum'
#     elif grep -Eqi "Aliyun" /etc/issue || grep -Eq "Aliyun" /etc/*-release; then
#         DISTRO='Aliyun'
#         PM='yum'
#     elif grep -Eqi "Fedora" /etc/issue || grep -Eq "Fedora" /etc/*-release; then
#         DISTRO='Fedora'
#         PM='yum'
#     elif grep -Eqi "Debian" /etc/issue || grep -Eq "Debian" /etc/*-release; then
#         DISTRO='Debian'
#         PM='apt'
#     elif grep -Eqi "Ubuntu" /etc/issue || grep -Eq "Ubuntu" /etc/*-release; then
#         DISTRO='Ubuntu'
#         PM='apt'
#     elif grep -Eqi "Raspbian" /etc/issue || grep -Eq "Raspbian" /etc/*-release; then
#         DISTRO='Raspbian'
#         PM='apt'
#     else
#         DISTRO='unknow'
#     fi
#     echo $DISTRO;
# }

# Get_Dist_Name

# eval $PM update -y
# eval $PM install curl -y
# eval $PM install expect -y
# eval $PM install rsync -y

rsynDataCore()
{
   if [ $# -eq "3" ];then
    src=$1
    dest=$2
    pwd=$3

    expect -c "
        spawn rsync -avzut --progress --timeout=360 $src $dest
        expect {
                \"*assword\" {set timeout 300; send \"${pwd}\r\";}
                \"yes/no\" {send \"yes\r\"; exp_continue;}
               }
    expect eof"
   fi
}

rsyncData() {
    if [ $# -eq "3" ];then
        echo "Rsync data $1 => $2 ..."
        r=`rsynDataCore $1 $2 $3 | grep -Po 'total size'`
        while [[ $r != "total size" ]];do
            echo "Wait 10s to restart..."
            sleep 10
            r=`rsynDataCore $1 $2 $3 | grep -Po 'total size'`
        done
        echo "Rsync data $1 => $2 is OK!"
    fi
}

rsynDataCore $1 $2 $3