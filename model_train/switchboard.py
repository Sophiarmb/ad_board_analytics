## @package nlp_tfidf
# This module defines the options with which kmeans_clustering.py can be run.
#
# Copyright (C) rMark Bio, Inc. - All Rights Reserved, 2015 - 2018.
# Unauthorized copying, use or distribution of this file, via any medium,
# without express written permission is strictly prohibited.
# Proprietary and Confidential.
#
# Filename:    kmeans_clustering/switchboard.py
# Written by:  Sofiya Mujawar <smujawar@rmarkbio.com>
# Description: This module translates arguments from a bash driver script to
#              perform kmeans clustering


import sys
import argparse
import json
from build_model import clustering_main

## These are string arguments that are always used
# format is name:help_text
STRING_ARGS = {
    'log_path'                          : 'Filename for the logger',
    'model_directory'                   : 'Directory to write the model to and read from',
    'model_name'                        : 'Model name',
    'model_version'                     : 'Model version',
    's3_download_bucket'                : 'AWS S3 bucket with data files',
    's3_neo4j_bucket'                   : 'AWS S3 bucket for neo4j graph files',
    's3_upload_bucket'                  : 'AWS S3 bucket for uploading model files',
    'download_blob'                     : 'True/False: download blob file to a local temp directory',
    'data_directory'               : 'Temporary directory to download blob file to',
    'corpus_name'                       : 'Name and unique string identifier of a corpus',
    'corpus_dir'                        : 'Directory of the local corpus files',
    'datafile'                          : 'Name of the data file to be downloaded from azure blob storage',
    'corpus_document_limit'             : 'Limit the number of documents processed',
    'document_frequency_batch_size'     : 'Number of term nodes to query for document frequency calculations at once',
    'phrase_identification'             : 'Flag to set the phrase identification functionality on',
    'named_entity_recognition'          : 'Flag to set the named entity recognition functionality on',
    'collocations_finder'               : 'Flag to set collocations finder functionality on',
    'frequency_filter'                  : 'Minimum frequency to be considered as an ngram',
    'number_of_ngrams'                  : 'Total number of ngrams to be added to the final token list for tf-idf calculations',
    'elbow_method'                      : 'Flag to find the optimal k value for clustering',
    'k_lower'                           : 'Lower limit of k for the elbow method',
    'k_upper'                           : 'Upper limit of k for the elbow method',
    'k_step'                            : 'The step size for elbow method',
    'seed_selection'                    : 'Opt in to select seeds using kmeans ++ scalable algorithm',
    'k_clusters'                        : 'The number of clusters',
    'oversampling_factor'               : 'The number of samples to be picked for a new centroid',
    'batch_size'                        : 'Batch size for the data to be processed in',
    'number_of_batches'                 : 'Number of batches to train the kmeans model',
    'hard_stop_iterations'              : 'Number of iterations to break training at, no exceptions',
    'empty_graph_container_blobs'       : 'Delete all blobs files in the Azure container pertaining to the TF-IDF graph',
    'delete_existing_graph'             : 'Delete the existing graph database',
    'create_graph_constraints'          : 'Create database constraints in the Neo4j graph according to the `neo4j_config.py`',
    'create_corpus_node'                : 'Create a singular node in the graph representing the corpus',
    'process_pubmed_data'               : 'Process pubmed text for clustering.',
    'build_graph_csv_files_1'           : 'Build the CSV files that build a graph, excluding the document frequency and TF-IDF relationships',
    'upload_graph_csv_files_1'          : 'Upload the CSV files to Azure blob storage',
    'build_graph_1'                     : 'Build the Neo4j graph from CSVs in blob storage, excluding the document frequency and TF-IDF relationships',
    'build_document_frequency_files'    : 'Build document frequency relationship data into a CSV file',
    'upload_document_frequency_file'    : 'Upload the CSV file for document frequency relationships',
    'build_document_frequency_graph'    : 'Build the document frequency relationships into the graph',
    'build_tfidf_files'                 : 'Build TF-IDF relationship CSV file',
    'upload_tfidf_files'                : 'Upload the TF-IDF CSV file',
    'build_tfidf_graph'                 : 'Build TF-IDF graph',
    'term_dictionary_selection'         : 'Term dictionary selection using average tfidf or document frequency',
    'vocab_size'                        : 'Number of terms (ranked by highest avg. TF-IDF values) to use in the word2vec model',
    'vocab_threshold'                   : 'Document frequency threshold for terms to be included in the kmeans clustering model',
    'vocab_limit_fraction'              : 'Maximum document frequency (fraction of documents) for terms to be included in the kmeans clustering model',
    'build_term_dictionaries'           : 'Build the term/label dictionaries and reverse dictionaries',
    'build_df_training_data'            : 'Build the input training data using document frequency',
    'build_training_data'               : 'Build the input training data',
    'run_training'                      : 'Flag set to begin training kmeans model',
    'run_testing'                       : 'Flag set to test new data on the kmeans model',
    'internal_validation_metrics'       : 'Calculates internal validation metrics on the model when there is no ground truth available',
    'upload_model_files'                : 'Upload model files',
    'delete_blob_temp_directory'        : 'Delete the directory of the downloaded temp blob file',
    }


# Parse arguments from the bash driver script or terminal command.
# @param args Terminal arguments for running sentiment model polarity.
# @retval None
def main(args):
    parser = argparse.ArgumentParser(description='run pipeline for sentiment model polarity')

    #string arguments, required
    for arg, help_text in STRING_ARGS.items():
        parser.add_argument('--' + arg, type = str, help = help_text, required = True)

    #parse and print out arguments
    args = parser.parse_args()
    build_options = json.dumps(vars(args), indent = 4)
    clustering_main(build_options)

### Execution starts here
if __name__ == '__main__':
    main(sys.argv[1:])  #because argv[0] is always the filename followed by positional arguments
