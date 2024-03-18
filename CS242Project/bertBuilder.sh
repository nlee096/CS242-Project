
if [ $# -ne 1 ]
then
    echo "Usage: $0 <input_data_file>"
    exit 1
fi

input_data_file=$1

if [ ! -f "$input_data_file" ]
then
    echo "File path is wrong or input data file does not exist: $input_data_file"
    exit 1
fi
python3 BERT_FAISS_indexer.py $input_data_file  
mv multi_full_index_no_mask.index webapp/
