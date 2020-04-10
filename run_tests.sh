#!/bin/bash

if [ $# -eq 0 ]
then
    echo "usage: ./run_tests.sh solver-cmd inputs ref-solutions timeout memout problem-task[s]"
    exit 0
fi


BASEDIR=$(dirname "$0")
ORIGINALDIR=$(pwd)

SOLVER=$1
INPUTS=${2:-"inputs"}
REFS=${3:-"reference-results"}
TIMEOUT=${4:-300}
MEMOUT=${5:-2048}

echo 'Making a output directory for' $(date)
TEST_NAME=$(date +'%Y-%m-%d_%H-%M-%S-')$SOLVER

if [ "$SOLVER" == "solved-af" ]
then
    TEST_NAME+="_$(git rev-parse HEAD | cut -c 1-8)"
fi

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

touch $BURNER/log.txt
echo "Timeout is set for $TIMEOUT seconds, Memout is set for $MEMOUT MB" >> $OUTFILE
HEADER='WCTIME,CPUTIME,USERTIME,SYSTEMTIME,CPUUSAGE,MAXVM,TIMEOUT,MEMOUT'
echo 'TASK,FILE,'$HEADER'MATCH' >> $OUTFILE

PROBLEM_TASKS="${@:6}"

echo 'Beginning Tests for '${PROBLEM_TASKS[@]}' on '$SOLVER'...'

telegram-send --format markdown "*$(hostname)*: Beginning testing for * ${PROBLEM_TASKS[@]} * on $SOLVER!"

for PROBLEM_TASK in ${PROBLEM_TASKS[@]};
do

    for PROBLEM_FILE in $BASEDIR/$INPUTS/*.tgf;
    do
        PROBLEM_FILE_NAME=$(basename -- "$PROBLEM_FILE")
        PROBLEM_FILE_NAME="${PROBLEM_FILE_NAME%.*}"


        echo -n $PROBLEM_TASK >> $OUTFILE
        echo -n ',' >> $OUTFILE
        echo -n $PROBLEM_FILE >> $OUTFILE
        echo -n ',' >> $OUTFILE

        echo '>>  Running Test: ' $PROBLEM_TASK 'on ' $PROBLEM_FILE

        runsolver -w $BURNER/watcher.txt -v $BURNER/varfile.txt -o $BURNER/solver.o -W $TIMEOUT --vsize-limit $MEMOUT $SOLVER -fo tgf -f $PROBLEM_FILE -p $PROBLEM_TASK

        cat $BURNER/watcher.txt >> $BURNER/log.txt


	IFS="="
        while read -r name value
        do
            [[ "$name" =~ ^[[:space:]]*# ]] && continue
            echo -n $value >> $OUTFILE
            echo -n ',' >> $OUTFILE
        done < $BURNER/varfile.txt
	unset IFS

        MATCH=$(compare-exts-mpz "$BURNER"/solver.o "$REFS"/"$PROBLEM_FILE_NAME".apx-"$PROBLEM_TASK".out | tail -1)

        echo $MATCH >> $OUTFILE

	echo "$MATCH"

    done

    telegram-send --format markdown "*$(hostname)*: Problem task *$PROBLEM_TASK* completed!"

done

telegram-send --format markdown "$(hostname): *Test $(date +'%Y-%m-%d_%H-%M-%S') completed!*"

echo 'Tests Finished!'
