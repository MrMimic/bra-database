for YEAR in {2022..2022}
do
    for MONTH in {03..03}
    do
        for DAY in {16..18}
        do
            export BRA_DATE=$YEAR$MONTH$DAY
            export BRA_LOG_FOLDER=/home/emeric/CODE/PERSO/bra-database/logs
            export BRA_PDF_FOLDER=/home/emeric/CODE/PERSO/bra-database/out/$BRA_DATE
            export BRA_IMG_FOLDER=/home/emeric/CODE/PERSO/bra-database/img
            python run.py
        done
    done
done
