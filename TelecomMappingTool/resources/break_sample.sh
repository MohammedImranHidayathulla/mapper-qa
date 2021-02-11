CUSTOMER=asentinel
VENDOR=<<VENDORNAME>>

BINDIR=/home/asentinel/auto_edi/bin
VANROOT=/home/asentinel/auto_edi/vans/${VENDOR}
PATH=/home/asentinel/jdk11/bin:${PATH}

cd ${VANROOT}/${CUSTOMER}/

#rsync --dirs --remove-source-files -e ssh 172.31.2.155:${VANROOT}/${CUSTOMER}/in/ ./in/
find ./transferin/ -type f -mmin +10 -exec mv {} ./in/ \;

#-------------------------------------------------------------------------------
# Unzip files
#-------------------------------------------------------------------------------
#find ./in/ -type f -iname "*.ZIP" -exec 7za x -y -o./in/ {} \; -exec rm -f {} \;
#find ./in/ -type f -iname "*.GZ" -exec gzip -dfq {} \;

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
java -cp $BINDIR/oirxmlgenerator2/oirxmlgenerator2.jar:$BINDIR/oirxmlgenerator2/* oirxmlgenerator.vendor.<<MAPPERNAME>> ./in/ ./complete/ ./in_archive/ ./errordir/

#-------------------------------------------------------------------------------
# Register the file in EDIINBOUNDFILES
#-------------------------------------------------------------------------------
java -jar ${BINDIR}/EdiFileRegister.jar ${VANROOT}/${CUSTOMER}/complete/ ./errordir/

#-------------------------------------------------------------------------------
# Prepare files for move to the customer folders
#-------------------------------------------------------------------------------
find ./complete/ -type f -exec mv {} ./transferout/ \;
find ./undefined/ -type f -exec mv {} ./transferout/ \;

find ./transferout/ -maxdepth 1 -iname <<FILEPATTERN>> -exec mv {} /home/asentinel/editransfer/<<CLIENTNAME>>/in/ \;

find ./transferout/ -maxdepth 1 -type f -exec mv {} ./undefined/ \;

cd ${VANROOT}

