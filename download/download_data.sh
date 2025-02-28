#!/bin/sh
_VAN_DE_VEN_NAME="VanDeVenEtAl_2023_NCC_outputs"
_VAN_DE_VEN_ZIPFILE="${_VAN_DE_VEN_NAME}".zip
curl 'https://zenodo.org/records/7767193/files/VanDeVenEtAl_2023_NCC_outputs.zip?download=1' > ${_VAN_DE_VEN_ZIPFILE}
unzip ${_VAN_DE_VEN_ZIPFILE} -d ${_VAN_DE_VEN_NAME}
rm ${_VAN_DE_VEN_ZIPFILE}

