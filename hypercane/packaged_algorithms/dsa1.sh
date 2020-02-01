#!/bin/sh

set -e

function report_and_execute_command() {
    command=$1
    echo "`date '+%Y%m%d %H%M%S'` [INFO] Executing subcommand: ${command}"
    $command
}

input_type=$1
input_args=$2
database_string=$3
working_directory=$4
output_filename=$5
logfile=$6

if [ -z ${logfile} ]; then
    logging_arg=""
else
    logging_arg="-l ${logfile}"
fi

report_and_execute_command "hc identify timemaps -i ${input_type} -ia ${input_args} -cs ${database_string} -o ${working_directory}/timemaps.tsv ${logging_arg}"

report_and_execute_command "hc filter include-only on-topic -i timemaps -ia ${working_directory}/timemaps.tsv -cs ${database_string} -o ${working_directory}/ontopic.tsv ${logging_arg}"

report_and_execute_command "hc filter exclude near-duplicates -i mementos -ia ${working_directory}/ontopic.tsv -cs ${database_string} -o ${working_directory}/non-duplicates.tsv ${logging_arg}"

report_and_execute_command "hc filter include-only languages --lang en -i mementos -ia ${working_directory}/non-duplicates.tsv -cs ${database_string} -o ${working_directory}/english-only.tsv ${logging_arg}"

report_and_execute_command "hc cluster time-slice -i mementos -ia ${working_directory}/english-only.tsv -cs ${database_string} -o ${working_directory}/sliced.tsv ${logging_arg}"

report_and_execute_command "hc cluster dbscan -i mementos -ia ${working_directory}/sliced.tsv -cs ${database_string} -o ${working_directory}/sliced-and-clustered.tsv --feature tf-simhash ${logging_arg}"

report_and_execute_command "hc rank dsa1-ranking -i mementos -ia ${working_directory}/sliced-and-clustered.tsv -cs ${database_string} -o ${working_directory}/ranked.tsv ${logging_arg}"

report_and_execute_command "hc filter include-only highest-rank-per-cluster -i mementos -ia ${working_directory}/ranked.tsv -cs ${database_string} -o ${working_directory}/highest-ranked.tsv ${logging_arg}"

report_and_execute_command "hc order pubdate-else-memento-datetime -i mementos -ia ${working_directory}/highest-ranked.tsv -cs ${database_string} -o ${working_directory}/ordered.tsv ${logging_arg}"

report_and_execute_command "cp ${working_directory}/ordered.tsv ${output_filename}"