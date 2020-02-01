
input_type=$1
input_args=$2
database_string=$3
logfile=$4
working_directory=$5
output_filename=$6

hc identify timemaps -i ${input_type} -ia ${input_args} -cs ${database_string} -l ${logfile} -o ${working_directory}/timemaps.tsv
hc filter include-only on-topic -i timemaps -ia ${timemap_file} -cs ${database_string} -l ${logfile} -o ${working_directory}/ontopic.tsv
hc filter exclude near-duplicates -i mementos -ia ${working_directory}/ontopic.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/non-duplicates.tsv
hc filter include-only languages --lang en -i mementos -ia ${working_directory}/non-duplicates.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/english-only.tsv
hc cluster time-slice -i mementos -ia ${working_directory}/english-only.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/sliced.tsv
hc cluster dbscan -i mementos -ia ${working_directory}/sliced.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/sliced-and-clustered.tsv --feature tf-simhash
hc rank dsa1-ranking -i mementos -ia ${working_directory}/sliced-and-clustered.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/ranked.tsv
hc filter include-only highest-rank-per-cluster -i mementos -ia ${working_directory}/ranked.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/highest-ranked.tsv
hc order pubdate-else-memento-datetime -i mementos -ia ${working_directory}/highest-ranked.tsv -cs ${database_string} -l ${logfile} -o ${working_directory}/ordered.tsv

cp ${working_directory}/ordered.tsv ${output_filename}