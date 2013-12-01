#!/bin/bash

BASEDIR="/home/chris/OxygenRefit2"

SIZES_TO_SYNC="16x16 22x22 24x24 32x32 48x48 64x64 72x72 96x96"

DIRS_TO_SYNC="actions apps apps-extra apps-evolution emblems categories devices mimetypes places status emotes"

TEMPLATE_SIZE="128x128"

echo "==============="
echo "Starting"
rm -rf $SIZES_TO_SYNC

sleep 2

cd $BASEDIR

cd $TEMPLATE_SIZE

for category in actions apps categories devices mimetypes places status; do cd $category
echo "===============" && echo -e "icon-mapping for 128x128/$category" && \
/usr/lib/icon-naming-utils/icon-name-mapping  -c $category >/dev/null && cd ..; \
done

sleep 2

cd $BASEDIR

for size in $SIZES_TO_SYNC; do cp -r 128x128 $size && \
for dir in $DIRS_TO_SYNC; do echo "===============" && \
echo -e "creating $size/$dir" && cd $size/$dir && \
mogrify -resize $size! *.png && cd $BASEDIR; \
done; \
done

echo "==============="
echo "cleaning up"
cd $BASEDIR
rm -f *~

chmod -R 755 *

echo "==============="
echo "Finished"
echo "==============="
