#!/bin/sh

cd /home/harpo/karaoke
#CDNAME=$2
read -p 'name of cd? ' CDNAME
mkdir $CDNAME
cd $CDNAME
cdrdao read-cd \
	--driver generic-mmc-raw \
	--device $1\
	--read-subchan rw_raw \
	--with-cddb \
	--eject \
	$CDNAME.toc &&
eject $1 &&
python ~/cdgtools-0.3.2/cdgrip.py \
	--with-cddb \
	$CDNAME.toc &&
rm data.bin
