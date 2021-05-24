#!/bin/bash
# Copyright (C) rMark Bio, Inc. - All Rights Reserved, 2015 - 2018.
# Unauthorized copying, use or distribution of this file, via any medium,
# without express written permission is strictly prohibited.
# Proprietary and Confidential.
#
# Filename:    model_train/driver.sh
# Written by:  Sofiya Mujawar <smujawar@rmarkbio.com>
# Description: This driver script controls the build of an kmeans clustering
#              model for any kind of text documents
#              This repository is used to perform clustering on pubmed data

# For recording run times
res1=$(date +%s)

export PYTHONEXE=/usr/bin/python
export ABVHOME=$(pwd)

# Set logging location
export LOGHOME='/home/rmarkbio/logs/'

# Model directory, name and version number
export MODEL_DIRECTORY='saved_models'
export MODEL_NAME='adboard_data.pickle'
export MODEL_VERSION='1.0'

# AWS buckets
#export S3_DOWNLOAD_BUCKET='rmb-datascience-pubmed-legacy-2019'
export S3_NEO4J_BUCKET='rmb-datascience-scratch-neo4j'
export S3_UPLOAD_BUCKET='rmb-datascience-scratch-models'
#export S3_NEO4J_BUCKET='rmb-datascience-scratch-neo4j'
#export S3_UPLOAD_BUCKET='rmb-datascience-scratch-models'

# Download a blob file to a local temporary directory
export DATA_DIRECTORY='data/'

#------------------------------------------------------------------------------------------
# TF-IDF Keyword Paramters
#------------------------------------------------------------------------------------------

# Corpus name: This uniquely identifies a corpus, which is represented by
# a node in a Neo4j database.
export CORPUS_NAME='adboard_data'
export CORPUS_DIR='data/adboard_data/'
#export DATAFILE='pubmed_2019.tar.gz'

# Set a limit on the number of corpus files to process.  Use `-1` for no limit (i.e. the full corpus)
export CORPUS_DOCUMENT_LIMIT=1000

# There can be ~10^5 terms to compute the document frequency for, so we
# need to split this up.  The `DOCUMENT_FREQUENCY_BATCH_SIZE` is the number of term nodes
# to retrieve at once.  The `N_EPOCH_DOCUMENT_FREQUENCY` and `N_PROCESSES_DOCUMENT_FREQUENCY`
# parameters determine how that particular batch will be multiprocessed.
# I am also using these for parallel computation of TF-IDF values.
export DOCUMENT_FREQUENCY_BATCH_SIZE=1000
export N_EPOCH_DOCUMENT_FREQUENCY=1           # keep this 1
export N_PROCESSES_DOCUMENT_FREQUENCY=100

## Phrase identification hyper parameters
export COLLOCATIONS_FINDER=true
export PHRASE_IDENTIFICATION=false
export NAMED_ENTITY_RECOGNITION=false
export FREQUENCY_FILTER=1
export NUMBER_OF_NGRAMS=10

#------------------------------------------------------------------------------------------
# Term dictionary parameters
#------------------------------------------------------------------------------------------

# This is the number of distinct terms to use in the kmeans clustering training, as ranked by
# average TF-IDF value in the corpus.  If you want to just use all the terms in the corpus
# set this to "-1", which you will want to do for large modeling cases where computing
# every `tfidf` value in the corpus is far too computationally onerous.
# `VOCAB_SIZE` is used only with the "avg_tfidf" selection of `TERM_DICTIONARY_SELECTION`.
export VOCAB_SIZE=50000

# This is the threshold value for terms to select when "document_frequency" is
# the value used in `TERM_DICTIONARY_SELECTION`.  For example, if `VOCAB_THRESHOLD` is 5,
# then a term must appear in at least 6 documents in the corpus to be part of the
# word vector training.
export VOCAB_THRESHOLD=2
# A quick way of ignoring extremely frequent words ("stop words") in the training. Instead of manually
# specifying (e.g. by a list in a file), this allows one to ignore words that appear in more than a certain
# fraction of documents in the corpus. In this way, the list of stop words is somewhat tuned to the subject matter of
# the corpus with minimal effort. Set to 1.0 to disable.
export VOCAB_LIMIT_FRACTION=0.1 # Set this to ~0.2 or lower to get rid of really common words

# This specifies how we select terms to use when `VOCAB_SIZE` is greater than 0. We will be using avg_tfidf for kmeans.
export TERM_DICTIONARY_SELECTION="avg_tfidf"

#------------------------------------------------------------------------------------------
# Kmeans clustering parameters
#------------------------------------------------------------------------------------------

# For example for 100000 files the `BATCH_SIZE` = 1000 and the `NUMBER_OF_BATCHES` = 100. Hence, 1000 files will
# be processed for 100 batches. This allows kmeans training without causing memory problems.
export BATCH_SIZE=41
export NUMBER_OF_BATCHES=1

# `K_LOWER`, `K_UPPER` and `K_STEP` are the flags used for the `ELBOW_METHOD`, which determines the optimal number of `K_CLUSTERS`
# Clustering is performed from values `K_LOWER` to `K_UPPER` incremented by `K_STEP` values to determine the best value for `K_CLUSTERS`
# For example, for `K_LOWER`=2, `K_UPPER`=6 and `K_STEP`=2 the k-values elbow method will be tested for will be [2,4,6]
export K_LOWER=2
export K_UPPER=8
export K_STEP=1

# Seed selection hyperparameter
export OVERSAMPLING_FACTOR=2

# The elbow method plot will determine the optimal `K_CLUSTERS` value.
export K_CLUSTERS=6
export HARD_STOP_ITERATIONS=100

#------------------------------------------------------------------------------------------
# ORDER OF OPERATIONS
#------------------------------------------------------------------------------------------
export DOWNLOAD_BLOB=false
export EMPTY_GRAPH_CONTAINER_BLOBS=false
export DELETE_EXISTING_GRAPH=false
export CREATE_GRAPH_CONSTRAINTS=false
export CREATE_CORPUS_NODE=false
export PROCESS_PUBMED_DATA=false
export BUILD_GRAPH_CSV_FILES_1=false
export UPLOAD_GRAPH_CSV_FILES_1=false
export BUILD_GRAPH_1=false
export BUILD_DOCUMENT_FREQUENCY_FILES=false
export UPLOAD_DOCUMENT_FREQUENCY_FILE=false
export BUILD_DOCUMENT_FREQUENCY_GRAPH=false
export BUILD_TFIDF_FILES=false
export UPLOAD_TFIDF_FILES=false
export BUILD_TFIDF_GRAPH=false
export BUILD_TERM_DICTIONARIES=false
export BUILD_TRAINING_DATA=false
# Use this flag only if you're buildling training data using document frequency
export BUILD_DF_TRAINING_DATA=false
export ELBOW_METHOD=false
export SEED_SELECTION=false
export RUN_TRAINING=true
export INTERNAL_VALIDATION_METRICS=false
export RUN_TESTING=false
export UPLOAD_MODEL_FILES=false
export DELETE_BLOB_TEMP_DIRECTORY=false

$PYTHONEXE model_train/switchboard.py\
    --log_path=$LOGHOME\
    --model_directory=$MODEL_DIRECTORY\
    --model_name=$MODEL_NAME\
    --model_version=$MODEL_VERSION\
    --s3_download_bucket=$S3_DOWNLOAD_BUCKET\
    --s3_neo4j_bucket=$S3_NEO4J_BUCKET\
    --s3_upload_bucket=$S3_UPLOAD_BUCKET\
    --download_blob=$DOWNLOAD_BLOB\
    --data_directory=$DATA_DIRECTORY\
    --corpus_name=$CORPUS_NAME\
    --corpus_dir=$CORPUS_DIR\
    --datafile=$DATAFILE\
    --corpus_document_limit=$CORPUS_DOCUMENT_LIMIT\
    --document_frequency_batch_size=$DOCUMENT_FREQUENCY_BATCH_SIZE\
    --phrase_identification=$PHRASE_IDENTIFICATION\
    --named_entity_recognition=$NAMED_ENTITY_RECOGNITION\
    --collocations_finder=$COLLOCATIONS_FINDER\
    --frequency_filter=$FREQUENCY_FILTER\
    --number_of_ngrams=$NUMBER_OF_NGRAMS\
    --elbow_method=$ELBOW_METHOD\
    --k_lower=$K_LOWER\
    --k_upper=$K_UPPER\
    --k_step=$K_STEP\
    --oversampling_factor=$OVERSAMPLING_FACTOR\
    --seed_selection=$SEED_SELECTION\
    --k_clusters=$K_CLUSTERS\
    --batch_size=$BATCH_SIZE\
    --number_of_batches=$NUMBER_OF_BATCHES\
    --hard_stop_iterations=$HARD_STOP_ITERATIONS\
    --delete_existing_graph=$DELETE_EXISTING_GRAPH\
    --create_graph_constraints=$CREATE_GRAPH_CONSTRAINTS\
    --empty_graph_container_blobs=$EMPTY_GRAPH_CONTAINER_BLOBS\
    --create_corpus_node=$CREATE_CORPUS_NODE\
    --process_pubmed_data=$PROCESS_PUBMED_DATA\
    --build_graph_csv_files_1=$BUILD_GRAPH_CSV_FILES_1\
    --upload_graph_csv_files_1=$UPLOAD_GRAPH_CSV_FILES_1\
    --build_graph_1=$BUILD_GRAPH_1\
    --build_document_frequency_files=$BUILD_DOCUMENT_FREQUENCY_FILES\
    --upload_document_frequency_file=$UPLOAD_DOCUMENT_FREQUENCY_FILE\
    --build_document_frequency_graph=$BUILD_DOCUMENT_FREQUENCY_GRAPH\
    --build_tfidf_files=$BUILD_TFIDF_FILES\
    --upload_tfidf_files=$UPLOAD_TFIDF_FILES\
    --build_tfidf_graph=$BUILD_TFIDF_GRAPH\
    --vocab_size=$VOCAB_SIZE\
    --vocab_threshold=$VOCAB_THRESHOLD\
    --vocab_limit_fraction=$VOCAB_LIMIT_FRACTION\
    --term_dictionary_selection=$TERM_DICTIONARY_SELECTION\
    --build_term_dictionaries=$BUILD_TERM_DICTIONARIES\
    --build_training_data=$BUILD_TRAINING_DATA\
    --build_df_training_data=$BUILD_DF_TRAINING_DATA\
    --run_training=$RUN_TRAINING\
    --run_testing=$RUN_TESTING\
    --internal_validation_metrics=$INTERNAL_VALIDATION_METRICS\
    --upload_model_files=$UPLOAD_MODEL_FILES\
    --delete_blob_temp_directory=$DELETE_BLOB_TEMP_DIRECTORY\

res2=$(date +%s)
dt=$(echo "$res2 - $res1" | bc)
dd=$(echo "$dt/86400" | bc)
dt2=$(echo "$dt-86400*$dd" | bc)
dh=$(echo "$dt2/3600" | bc)
dt3=$(echo "$dt2-3600*$dh" | bc)
dm=$(echo "$dt3/60" | bc)
ds=$(echo "$dt3-60*$dm" | bc)

printf "\nDONE. Total processing time: %d:%02d:%02d:%02d\n" $dd $dh $dm $ds
