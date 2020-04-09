#!/bin/bash

IFS="="

BASEDIR=$(dirname "$0")
ORIGINALDIR=$(pwd)

TIMEOUT=300
MEMOUT=2048

echo 'Making a output directory for' $(date)
TEST_NAME=$(date +'test_%Y-%m-%d_%H-%M-%S')
OUTDIR=$ORIGINALDIR"/tests"/$TEST_NAME
BURNER=$OUTDIR/burner

if [ ! -w tests ]
then 
    mkdir tests
fi
mkdir -p $OUTDIR
mkdir -p $BURNER

OUTFILE=$OUTDIR/test-results_$TEST_NAME.csv
touch $OUTFILE

touch $BURNER/saf-log.txt
touch $BURNER/eqargsolver-log.txt

echo ",,SAF,,,,,,,," >> $OUTFILE
HEADER='WCTIME,CPUTIME,USERTIME,SYSTEMTIME,CPUUSAGE,MAXVM,TIMEOUT,MEMOUT,'
echo 'TASK,FILE,'$HEADER'MATCH' >> $OUTFILE

echo 'Running Enumeration Tests...'

PROBLEM_TASKS=('EE-CO')

for PROBLEM_TASK in ${PROBLEM_TASKS[@]};
do

    for PROBLEM_FILE in $BASEDIR/inputs/*.tgf;
    do
        PROBLEM_FILE_NAME=$(basename -- "$PROBLEM_FILE")
        PROBLEM_FILE_NAME="${PROBLEM_FILE_NAME%.*}"


        echo -n $PROBLEM_TASK >> $OUTFILE
        echo -n ',' >> $OUTFILE
        echo -n $PROBLEM_FILE >> $OUTFILE
        echo -n ',' >> $OUTFILE

        echo '> Running Test: ' $PROBLEM_TASK 'on ' $PROBLEM_FILE

        echo 'Runing SAF...'

        runsolver -w $BURNER/saf-watcher.txt -v $BURNER/saf-varfile.txt -o $BURNER/saf.o -W $TIMEOUT --vsize-limit $MEMOUT solved-af -fo tgf -f $PROBLEM_FILE -p $PROBLEM_TASK

        cat $BURNER/saf-watcher.txt >> $BURNER/saf-log.txt

        echo 'SAF Finished!'

        while read -r name value; do
            [[ "$name" =~ ^[[:space:]]*# ]] && continue
            echo -n $value >> $OUTFILE
            echo -n ',' >> $OUTFILE
        done < $BURNER/saf-varfile.txt

        # echo 'Runing EqArgSolve...'

        # runsolver -w $BURNER/eqargsolver-watcher.txt -v $BURNER/eqargsolver-varfile.txt -o $BURNER/eqargsolver.o -W $TIMEOUT --vsize-limit $MEMOUT eqobj -fo tgf -f ./$PROBLEM_FILE -p $PROBLEM_TASK


        # cat $BURNER/eqargsolver-watcher.txt >> $BURNER/eqargsolver-log.txt


        # echo 'EqArgSolver Finished!'

        # while read -r name value; do
        #     [[ "$name" =~ ^[[:space:]]*# ]] && continue
        #     echo -n $value >> $OUTFILE
        #     echo -n ',' >> $OUTFILE
        # done < $BURNER/eqargsolver-varfile.txt


        MATCH=$(compare-exts-mpz $BURNER/saf.o ~/Downloads/reference-results/$PROBLEM_FILE_NAME.apx-$PROBLEM_TASK.out | tail -1)

        echo $MATCH >> $OUTFILE

        #rm -f $BURNER/*

    done

    telegram-send --format markdown "Problem task *$PROBLEM_TASK* completed!"

done

telegram-send --format markdown "*Test $(date +'%Y-%m-%d_%H-%M-%S') completed!*"
#rm -rf $BURNER

export SOLVED_AF_CURRENT_TASK=""

echo 'Tests Finished!'
