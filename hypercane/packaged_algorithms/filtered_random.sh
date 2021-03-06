#!/bin/sh

set -e

input_type=$1
input_args=$2
database_string=$3
working_directory=$4
output_filename=$5
logfile=$6
errorfilename=$7
other_arguments=`echo $8 | sed 's/^"//g' | sed 's/"$//g'`

if [ -z ${logfile} ]; then
    logging_arg=""
else
    logging_arg="-l ${logfile}"
fi

if [ -z ${errorfilename} ]; then
    errorfile_arg=""
else
    errorfile_arg="-e ${errorfilename}"
fi

function report_and_execute_command() {
    command=$1
    echo "`date '+%Y-%m-%d %H:%M:%S'` [INFO] Executing subcommand: ${command}" >> ${logfile}
    $command
}

report_and_execute_command "hc identify timemaps -i ${input_type} -ia ${input_args} -cs ${database_string} -o ${working_directory}/timemaps.tsv ${logging_arg} -v ${errorfile_arg}"

report_and_execute_command "hc filter include-only on-topic -i timemaps -ia ${working_directory}/timemaps.tsv -cs ${database_string} -o ${working_directory}/ontopic.tsv ${logging_arg} ${errorfile_arg}"

report_and_execute_command "hc filter exclude near-duplicates -i mementos -ia ${working_directory}/ontopic.tsv -cs ${database_string} -o ${working_directory}/non-duplicates.tsv ${logging_arg} ${errorfile_arg}"

report_and_execute_command "hc sample true-random -i mementos -ia ${working_directory}/non-duplicates.tsv -o ${output_filename} ${logging_arg} ${errorfile_arg} ${other_arguments}"
