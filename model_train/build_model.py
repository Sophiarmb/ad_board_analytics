## @package kmeans_clustering
#
# Copyright (C) rMark Bio, Inc. - All Rights Reserved, 2015 - 2018.
# Unauthorized copying, use or distribution of this file, via any medium,
# without express written permission is strictly prohibited.
# Proprietary and Confidential.
# Filename:    kmeans_clustering/run_kmeans_clustering.py
# Written by:  Sofiya Mujawar <smujawar@rmarkbio.com>
# Description: This file calls the appropriate functions to prep training data and run kmeans clustering algorithm

import json
import os
import io
import logging
from datetime import datetime
from collections import Counter
import tarfile
from kmeans_clustering.kmeans_clustering import kmeans_clustering
from tfidf.tfidf import TF_IDF
from aws_s3_interface.aws_s3_interface import AWS_s3_interface
from neo4j_config import neo4j_config
from neo4j_build import NEO4J_BUILD
from tools import get_or_create_directory, local_corpus_filenames

NEO4J_USERNAME = os.environ['NEO4J_USERNAME']
NEO4J_PASSWORD = os.environ['NEO4J_PASSWORD']
NEO4J_BOLT = os.environ['NEO4J_BOLT']

neo4j_credentials = {
    'neo4j_username': NEO4J_USERNAME,
    'neo4j_password': NEO4J_PASSWORD,
    'neo4j_bolt': NEO4J_BOLT,
}

## Begin use of the `kmeans_clustering` class.
#  @brief               This illustrates the use of the class to execute unsupervised kmeans clustering algorithm.
#  @param build_options All parameters sent from the driver script to control how the data is clustered
#  @retval None
def clustering_main(build_options):

    ## @var Convert from JSON string to python dictionary
    build_options = json.loads(build_options)
    # Logging
    logger = logging.getLogger('Logging')
    logger.setLevel(logging.DEBUG)   # determine the level of severity to pass to handlers
    log_directory = str(build_options['log_path'])
    now           = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path      = get_or_create_directory(log_directory, now)
    log_filename  = 'central.log'

    # This handler will cover the primary logging file.
    file_handler = logging.FileHandler(log_path + '/' + log_filename)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # This handler will cover printing to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    #------------------------------------------------------------------------------------------
    # Order of operations
    #------------------------------------------------------------------------------------------
    download_blob                  = build_options['download_blob']                  == 'true'
    empty_graph_container_blobs    = build_options['empty_graph_container_blobs']    == 'true'
    delete_blob_temp_directory     = build_options['delete_blob_temp_directory']     == 'true'
    delete_existing_graph          = build_options['delete_existing_graph']          == 'true'
    create_graph_constraints       = build_options['create_graph_constraints']       == 'true'
    create_corpus_node             = build_options['create_corpus_node']             == 'true'
    process_pubmed_data            = build_options['process_pubmed_data'] == 'true'
    build_graph_csv_files_1        = build_options['build_graph_csv_files_1']        == 'true'
    upload_graph_csv_files_1       = build_options['upload_graph_csv_files_1']       == 'true'
    build_graph_1                  = build_options['build_graph_1']                  == 'true'
    build_document_frequency_files = build_options['build_document_frequency_files'] == 'true'
    upload_document_frequency_file = build_options['upload_document_frequency_file'] == 'true'
    build_document_frequency_graph = build_options['build_document_frequency_graph'] == 'true'
    build_tfidf_files              = build_options['build_tfidf_files']              == 'true'
    upload_tfidf_files             = build_options['upload_tfidf_files']             == 'true'
    build_tfidf_graph              = build_options['build_tfidf_graph']              =='true'
    build_term_dictionaries        = build_options['build_term_dictionaries']        == 'true'
    build_df_training_data         = build_options['build_df_training_data']         == 'true'
    build_training_data            = build_options['build_training_data']            == 'true'
    run_training                   = build_options['run_training']                   == 'true'
    run_testing                    = build_options['run_testing']                    == 'true'
    internal_validation_metrics    = build_options['internal_validation_metrics']    == 'true'
    upload_model_files             = build_options['upload_model_files']             == 'true'
    seed_selection                 = build_options['seed_selection']                 == 'true'
    elbow_method                   = build_options['elbow_method']                   == 'true'

    # Model directory and name
    model_directory = str(build_options['model_directory'])
    model_name      = str(build_options['model_name'])
    model_version   = str(build_options['model_version'])

    # Parameters from the driver script
    s3_download_bucket        = str(build_options['s3_download_bucket'])
    s3_neo4j_bucket           = str(build_options['s3_neo4j_bucket'])
    s3_upload_bucket          = str(build_options['s3_upload_bucket'])
    corpus_name               = str(build_options['corpus_name'])
    corpus_dir                = str(build_options['corpus_dir'])
    datafile_name             = str(build_options['datafile'])
    term_dictionary_selection = str(build_options['term_dictionary_selection'])
    data_directory            = str(build_options['data_directory'])

    # Variables for TF-IDF pre processing
    frequency_filter              = build_options['frequency_filter']
    number_of_ngrams              = build_options['number_of_ngrams']
    collocations_finder           = build_options['collocations_finder']
    phrase_identification         = build_options['phrase_identification']
    named_entity_recognition      = build_options['named_entity_recognition']
    corpus_document_limit         = int(build_options['corpus_document_limit'])
    document_frequency_batch_size = int(build_options['document_frequency_batch_size'])

    # Variables for building term dictionary
    vocab_size = int(build_options['vocab_size'])
    vocab_threshold      = int(build_options['vocab_threshold'])
    vocab_limit_fraction = float(build_options['vocab_limit_fraction'])

    # Variables for clustering
    k_lower              = int(build_options['k_lower'])
    k_upper              = int(build_options['k_upper'])
    k_step               = int(build_options['k_step'])
    batch_size           = int(build_options['batch_size'])
    number_of_batches    = int(build_options['number_of_batches'])
    k_clusters           = int(build_options['k_clusters'])
    oversampling_factor  = int(build_options['oversampling_factor'])
    hard_stop_iterations = int(build_options['hard_stop_iterations'])

    # JSON filenames for term/label dictionaries.  These are used in multiple places.
    term_dictionary_filename = os.path.join(
        model_directory, model_name + '_term_dictionary.json',
    )
    reversed_term_dictionary_filename = os.path.join(
        model_directory, model_name + '_reversed_term_dictionary.json',
    )
    document_dictionary_filename = os.path.join(
        model_directory, model_name + '_document_dictionary.json',
    )
    reversed_document_dictionary_filename = os.path.join(
        model_directory, model_name + '_reversed_document_dictionary.json',
    )
    tfidf_vector_filename = os.path.join(
        model_directory, model_name + '_tfidf_vector_dictionary.json',
    )
    centroid_filepath = os.path.join(model_directory, 'centroid_list.json')

    # Demonstrate downloading blob file from Azure to local temp directory
    if download_blob:
        print('Download Blob From S3 bucket')
        s3_interface = AWS_s3_interface(bucket_name = s3_download_bucket)
        bucket_items = s3_interface.list_blobs()
        s3_interface.download_file(
            local_data_directory = data_directory,
            blob_file_name       = datafile_name,
        )

        # Extract the tarball
    #    target_data_fullpath = os.path.join(data_directory, datafile_name)
    #    with tarfile.open(target_data_fullpath) as tar_obj:
    #        # Extract all the contents of the tarfile in current directory
    #        tar_obj.extractall(data_directory)

    #    remove_tarball_str = 'rm %s' % (target_data_fullpath,)
    #    logger.debug(remove_tarball_str)
    #    os.system(remove_tarball_str)

    # Instantiate the `TF_IDF` class
    tf_idf = TF_IDF(
        logger                         = logger,
        log_path                       = log_path,
        neo4j_config                   = neo4j_config,
        neo4j_credentials              = neo4j_credentials,
        NEO4J_BUILD                    = NEO4J_BUILD,
        corpus_name                    = corpus_name,
        corpus_path                    = corpus_dir,
        corpus_filenames_retriever     = local_corpus_filenames,
        blob_temp_directory            = data_directory,
        MAX_RECORDS_PER_FILE           = 250000,
    )

    # Delete all files in aws which is used to build the graph
    if empty_graph_container_blobs:
        logger.info('Delete Neo4j build files from the S3 bucket')
        graph_s3_interface = AWS_s3_interface(bucket_name = s3_neo4j_bucket)
        bucket_items = graph_s3_interface.list_blobs()
        for bucket_item in bucket_items:
            graph_s3_interface.delete_file(
                blob_file_name = bucket_item,
            )

    # Delete the entire graph database
    if delete_existing_graph:
        logger.info('Delete the Prior TF-IDF Graph')
        tf_idf.delete_graph(batch_size = 10000)

    # Implement uniqueness constraints as specified by the Neo4j schema in `neoj_config.py`,
    # which was passed during instantiation.
    if create_graph_constraints:
        tf_idf.create_neo4j_constraints()

    # Create the corpus node
    if create_corpus_node:
        logger.info('Creating/Merging corpus node %s', (corpus_name,))
        tf_idf.create_corpus_node(
            name        = corpus_name,
            description = 'This is a test corpus of research paper abstracts',
        )

    # Process pubmed data abstracts
    if process_pubmed_data:
        logger.info('-------------------------------------------------------------------------------------------------')
        logger.info('Process PubMed Abstract Text Files\n')

        raw_pubmed_filenames = local_corpus_filenames(
            corpus_path = corpus_dir,
            limit = corpus_document_limit,
        )

        N_raw_files = len(raw_pubmed_filenames)

        # Iterate through the PubMed files downloaded from blob storage
        logger.info('Writing TF-IDF Training Files From %s Source Files' % (N_raw_files,))

        file_counter         = 0
        error_counter        = Counter()
        for i, raw_pubmed_filename in enumerate(raw_pubmed_filenames):

            if i % 1000 == 0:
                logger.info('Writing %s' % (i,))

            # Only open files that end in ".json"
            _, filename_extension = os.path.splitext(raw_pubmed_filename)
            if filename_extension != '.json':
                continue

            # Open the JSON file to retrieve the title, abstract, and labels ("macroconcepts")
            with io.open(raw_pubmed_filename, 'r', encoding = 'utf8', errors = "ignore") as raw_pubmed_file:
                try:
                    raw_pubmed_json = json.load(raw_pubmed_file)
                except:
                    logger.error('Error loading %s.  Moving along...' % (raw_pubmed_file,))
                pubmed_id       = raw_pubmed_json['pmid']

                # Retrieve the article title, if the field is present.
                pubmed_article_title = ''
                try:
                    pubmed_article_title = raw_pubmed_json['title']
                except:
                    logger.debug('%s : No article title field found' % (raw_pubmed_filename,))
                    error_counter['article title'] += 1
                    pass

                # Retrieve the article abstract, if the field is present.
                pubmed_abstract = ''
                try:
                    pubmed_abstract = raw_pubmed_json['abstract']
                except:
                    logger.debug('%s : No abstract field found' % (raw_pubmed_filename,))
                    error_counter['abstract'] += 1
                    pass

                pubmed_tfidf_text = pubmed_article_title + pubmed_abstract
                pubmed_tfidf_text = pubmed_tfidf_text.encode().decode("ascii" , "ignore")

                # Create a 2nd copy in a unified directory with all files prepended by their
                # macroconcept string value.  Note that the macroconcept string in the file names
                # are being prepended with a double underscore ("__") on which to split the string value later.
                # This, of course, is based on the implicit assumption that these category labels will
                # never have double underscores in them.
                label_directory_path = os.path.join(data_directory, 'pubmed_text/')
                if not os.path.exists(label_directory_path):
                    os.mkdir(label_directory_path)

                if len(pubmed_tfidf_text) > 0:
                    pubmed_tfidf_filename = str(pubmed_id) + '.txt'
                    pubmed_tfidf_filename_fullpath = os.path.join(label_directory_path, pubmed_tfidf_filename)
                    with io.open(pubmed_tfidf_filename_fullpath, 'w', encoding = 'utf8') as pubmed_tfidf_file:
                        pubmed_tfidf_file.write(pubmed_tfidf_text)
                        file_counter                += 1

        # Write a summary to terminal
        logger.info('')
        logger.info('    Total Files Generated     : %s' % (file_counter,))

    # This builds CSV files for building the first stage of the TF-IDF graph:
    #   - document nodes
    #   - term nodes
    #   - document_corpus nodes
    #   - doucment_category nodes
    #   - term_frequency relationships
    #   - most_frequent_term relationships
    #   - in_document_category relationships
    #   - in_corpus relationships
    #   - related_to_document relationships
    #   - related_to_corpus relationships
    if build_graph_csv_files_1:
        pubmed_data_fullpath = os.path.join(data_directory, 'adboard_text/')

        logger.info('Processing corpus documents to build term and document nodes')
        document_limit = int(corpus_document_limit)
        if document_limit <= 0:
            document_limit = None

        tf_idf.process_corpus_documents(
            file_limit                     = document_limit,
            corpus_path                    = pubmed_data_fullpath,
            document_categories            = ['training_data','test_data', 'validation_data'],
            training_prob                  = 1,
            test_prob                      = 0,
            validation_prob                = 0,
            phrase_identification          = phrase_identification,
            named_entity_recognition       = named_entity_recognition,
            collocations_finder            = collocations_finder,
            frequency_filter               = frequency_filter,
            number_of_ngrams               = number_of_ngrams,
            blob_temp_directory            = data_directory,
            document_processing_batch_size = document_frequency_batch_size,
            corpus_name                    = corpus_name,
            delete_existing_files          = True,
            max_word_length                = None,
        )

    # Upload the CSV files we just generated to blob storage
    if upload_graph_csv_files_1:
        neo4j_data_directory = os.path.join(data_directory, 'neo4j')
        TF_IDF.upload_build_files_aws(
            AWS_s3_interface = AWS_s3_interface,
            logger = logger,
            tf_idf = tf_idf,
            bucket_name = s3_neo4j_bucket,
            upload_directory = neo4j_data_directory,
            upload_named_entity_nodes                 = True,
            upload_document_nodes                     = True,
            upload_term_nodes                         = True,
            upload_document_corpus_nodes              = True,
            upload_document_category_nodes            = True,
            upload_related_to_tag_relationships       = True,
            upload_in_corpus_relationships            = True,
            upload_in_document_category_relationships = True,
            upload_most_frequent_term_relationships   = True,
            upload_term_frequency_relationships       = True,
            upload_related_to_document_relationships  = True,
            upload_related_to_corpus_relationships    = True,
        )

    # Write the blob files generated so far to the Neo4j graph
    if build_graph_1:
        logger.info('------------------------------------------')
        logger.info('Building Neo4j Graph')

        tf_idf.create_document_nodes_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_term_nodes_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_document_corpus_nodes_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_document_category_nodes_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_term_frequency_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_in_corpus_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_related_to_corpus_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_related_to_document_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_most_frequent_term_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

        tf_idf.create_in_document_category_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

    # Build the csv file for the document frequency relationship data
    if build_document_frequency_files:
        tf_idf.compute_document_frequencies(
            batch_size = document_frequency_batch_size,
            corpus_name = corpus_name,
        )

    # Upload the csv file for document frequency relationships to blob storage
    if upload_document_frequency_file:
        neo4j_data_directory = os.path.join(data_directory, 'neo4j')
        TF_IDF.upload_build_files_aws(
            AWS_s3_interface = AWS_s3_interface,
            logger = logger,
            tf_idf = tf_idf,
            bucket_name = s3_neo4j_bucket,
            upload_directory = neo4j_data_directory,
            upload_document_frequency_relationships   = True,
        )

    # Build the document frequency relationships into the graph from blob storage
    if build_document_frequency_graph:
        logger.info('------------------------------------------')
        logger.info('Building Neo4j Graph')
        tf_idf.create_document_frequency_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

    if build_tfidf_files:
        tf_idf.compute_TF_IDF(
            corpus_name = corpus_name,
            batch_size  = document_frequency_batch_size,
        )

    if upload_tfidf_files:
        neo4j_data_directory = os.path.join(data_directory, 'neo4j')
        TF_IDF.upload_build_files_aws(
            AWS_s3_interface = AWS_s3_interface,
            logger = logger,
            tf_idf = tf_idf,
            bucket_name = s3_neo4j_bucket,
            upload_directory = neo4j_data_directory,
            upload_tfidf_relationships = True,
        )

    if build_tfidf_graph:
        logger.info('------------------------------------------')
        logger.info('Building Neo4j Graph')
        tf_idf.create_tfidf_relationships_from_aws(
            AWS_s3_interface = AWS_s3_interface,
            neo4j_config = neo4j_config,
            NEO4J_BUILD = NEO4J_BUILD,
            graph_bucket_name = s3_neo4j_bucket,
        )

    if build_term_dictionaries:
        print("\nBuilding term dictionaries...")

        if not os.path.exists(model_directory):
            os.makedirs(model_directory)

        term_values = []

        # Proceed with modeling using only the top `vocab_size` terms as ranked by their
        # average TF-IDF value in the corpus.
        if term_dictionary_selection == 'avg_tfidf':
            term_values = tf_idf.avg_term_tfidf(
                N_terms = vocab_size,
            )
            term_values = term_values[0]
            term_values = [t['term'] for t in term_values]
            print(len(term_values))

        # Proceed with modeling using every term in the corpus.  For very large modeling
        # cases, this should be used.  Computing the `tfidf` relationships is very
        # time consuming and blows up as the number of terms times the number of documents.
        else:
            neo4j_driver = tf_idf.__get_neo4j_driver__()
            with neo4j_driver.session() as neo4j_session:
                cypher_query = '''
                MATCH (t:{node_term_label}) RETURN t.{node_term_uid} AS term;
                '''.format(
                    node_term_label = neo4j_config['node']['term']['label'],
                    node_term_uid   = neo4j_config['node']['term']['uid'],
                )
                records = tf_idf.__transaction_manager__(neo4j_session, cypher_query)
                term_values = [r['term'] for r in records.data()]

        if len(term_values) == 0:
            raise Exception('Error: there are no terms in `term_values`')

        # Create an encoding that associates all terms with some integer value.  We need a dictionary that associates
        # every term with its index, the reversed version of that dictionary,
        term_dictionary = dict()
        word_index      = 0
        for term in term_values:
            term_dictionary[term] = word_index
            word_index += 1

        # Write to file
        with open(term_dictionary_filename, 'w+', encoding='utf-8') as encoded_file:
            json.dump(term_dictionary, encoded_file)

        # Reverse the keys and values in `term_dictionary` to get a dictionary with integer representations
        # as the keys and word strings as the values.
        reversed_term_dictionary = dict(zip(term_dictionary.values(), term_dictionary.keys()))

        # Write to file
        with open(reversed_term_dictionary_filename, 'w+', encoding='utf-8') as encoded_file:
            json.dump(reversed_term_dictionary, encoded_file)


        # Build document dictionary
        neo4j_driver = tf_idf.__get_neo4j_driver__()
        with neo4j_driver.session() as neo4j_session:
            cypher_query = '''
            MATCH (d:{document_label}) RETURN d.{document_uid} AS filename;
            '''.format(
                document_label = neo4j_config['node']['document_corpus']['label'],
                document_uid   = neo4j_config['node']['document_corpus']['uid'],
            )
            records = tf_idf.__transaction_manager__(neo4j_session, cypher_query)
            unique_docs = [r['filename'] for r in records.data()]

        document_dictionary = dict()
        doc_index = 0
        for doc in unique_docs:
            document_dictionary[doc] = doc_index
            doc_index += 1

        # Write document dictionary to file
        with open(document_dictionary_filename, 'w+', encoding='utf-8') as encoded_file:
            json.dump(document_dictionary, encoded_file)

        reversed_document_dictionary = dict(zip(document_dictionary.values(), document_dictionary.keys()))

        # Write to file
        with open(reversed_document_dictionary_filename, 'w+', encoding='utf-8') as encoded_file:
            json.dump(reversed_document_dictionary, encoded_file)

    # Instantiate kmeans_clustering class
    kmeans = kmeans_clustering(
        logger               = logger,
        log_path             = log_path,
        model_directory      = model_directory,
        model_name           = model_name,
        k_lower              = k_lower,
        k_upper              = k_upper,
        k_step               = k_step,
        batch_size           = batch_size,
        seed_selection       = seed_selection,
        k_clusters           = k_clusters,
        oversampling_factor  = oversampling_factor,
        hard_stop_iterations = hard_stop_iterations,
        )


    # Build tfidf vectors for each document to be used for training
    if build_training_data:
        # Build TF-IDF vectors
        print("Retrieving TF-IDF document vectors")
        tfidf_vector = dict()

        # Read the term dictionary and document dictionary
        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())

        with open(document_dictionary_filename, 'r', encoding='utf-8') as doc_dictionary_file:
            document_dictionary = json.loads(doc_dictionary_file.read())

        top_k_terms = [v for v in term_dictionary]
        tfidf_batch_size = 1000

        # Query in batches only the terms selected in the term dictionary and their tfidf relationships
        # to the documents. This saves us the time to go through the rest of the unwanted terms in the graph
        neo4j_driver = tf_idf.__get_neo4j_driver__()
        with neo4j_driver.session() as neo4j_session:
            for i in range(0, len(top_k_terms), tfidf_batch_size):
                top_terms_batch = top_k_terms[i:i+tfidf_batch_size]
                cypher_query = '''
                    MATCH (t:{term_label})-[r:{tfidf}]-(d:{document_label})
                    WHERE t.{term_uid} IN {term_list}
                    RETURN t.{term_value} as term_text, r.{tfidf_value} as tfidf_value, d.{document_uid} as document
                '''.format(
                    term_label     = neo4j_config['node']['term']['label'],
                    tfidf          = neo4j_config['relationship']['tfidf']['label'],
                    document_label = neo4j_config['node']['document_corpus']['label'],
                    term_uid    = neo4j_config['node']['term']['uid'],
                    term_list   = top_terms_batch,
                    term_value    = neo4j_config['node']['term']['uid'],
                    tfidf_value = neo4j_config['relationship']['tfidf']['attrs']['value'],
                    document_uid = neo4j_config['node']['document_corpus']['uid'],

                )
                records = tf_idf.__transaction_manager__(neo4j_session, cypher_query)
                for record in records:
                    term = record["term_text"]
                    document = record["document"]
                    tfidf_value = record["tfidf_value"]
                    try:
                        term_id = term_dictionary[term]
                        document_id = document_dictionary[document]
                        if document_id in tfidf_vector:
                            tfidf_vector[document_id][term_id] = tfidf_value
                        else:
                            tfidf_vector[document_id] = { term_id : tfidf_value }

                    except (UnicodeEncodeError, KeyError) as ex:
                        pass

        with open(tfidf_vector_filename, 'w+', encoding='utf-8') as encoded_file:
            for key,value in tfidf_vector.items():
                # Sort according to term id
                final_sorted = {k:v for k, v in sorted(value.items(), key=lambda item: item[0])}
                result = { 'document_id' : key,
                           'tfidf_vector' : final_sorted }

                # Write to file
                json.dump(result, encoded_file)
                # Write a newline so that the file is organized to have one record per line.
                encoded_file.write('\n')
            encoded_file.close()


    # Build training data using document frequency
    if build_df_training_data:
        print("Retrieving DF document vectors")
        df_vector = dict()

        # Read the term dictionary and document dictionary
        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            print(len(term_dictionary))

        with open(document_dictionary_filename, 'r', encoding='utf-8') as doc_dictionary_file:
            document_dictionary = json.loads(doc_dictionary_file.read())

        top_k_terms = [v for v in term_dictionary]
        print(len(top_k_terms))
        df_batch_size = 1000

        # Query in batches only the terms selected in the term dictionary and their tfidf relationships
        # to the documents. This saves us the time to go through the rest of the unwanted terms in the graph
        neo4j_driver = tf_idf.__get_neo4j_driver__()
        with neo4j_driver.session() as neo4j_session:
            for i in range(0, len(top_k_terms), df_batch_size):
                top_terms_batch = top_k_terms[i:i+df_batch_size]
                cypher_query = '''
                    MATCH (t:{term_label})-[r:{tf}]-(d:{document_label})-[r1:{related_to_document}]-(dc: {document_corpus_label})
                    WHERE t.{term_uid} IN {term_list}
                    RETURN t.{term_value} as term_text, r.{tf_value} as tf_value, dc.{document_uid} as document
                '''.format(
                    term_label     = neo4j_config['node']['term']['label'],
                    tf             = neo4j_config['relationship']['term_frequency']['label'],
                    document_label = neo4j_config['node']['document']['label'],
                    related_to_document = neo4j_config['relationship']['related_to_document']['label'],
                    document_corpus_label = neo4j_config['node']['document_corpus']['label'],

                    term_uid       = neo4j_config['node']['term']['uid'],
                    term_list      = top_terms_batch,
                    term_value     = neo4j_config['node']['term']['uid'],
                    tf_value       = neo4j_config['relationship']['term_frequency']['attrs']['value'],
                    document_uid   = neo4j_config['node']['document_corpus']['uid'],

                )
                records = tf_idf.__transaction_manager__(neo4j_session, cypher_query)
                for record in records:
                    term = record["term_text"]
                    document = record["document"]
                    tf_value = record["tf_value"]
                    try:
                        term_id = term_dictionary[term]
                        document_id = document_dictionary[document]
                        if document_id in df_vector:
                            df_vector[document_id][term_id] = tf_value
                        else:
                            df_vector[document_id] = { term_id : tf_value }

                    except (UnicodeEncodeError, KeyError) as ex:
                        pass

        with open(tfidf_vector_filename, 'w+', encoding='utf-8') as encoded_file:
            for key,value in df_vector.items():
                # Sort according to term id
                final_sorted = {k:v for k, v in sorted(value.items(), key=lambda item: item[0])}
                result = { 'document_id' : key,
                           'tfidf_vector' : final_sorted }

                # Write to file
                json.dump(result, encoded_file)
                # Write a newline so that the file is organized to have one record per line.
                encoded_file.write('\n')
            encoded_file.close()
    

    # Compute optimal number of clusters
    if elbow_method:
        print("\nComputing optimal number of clusters...")
        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            term_dictionary_size = len(term_dictionary)

        kmeans.elbow_method(
            training_data_json  = tfidf_vector_filename,
            line_batch_size     = batch_size,
            number_of_batches   = number_of_batches,
            corpus_size         = term_dictionary_size,
            )

    if seed_selection:
        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            term_dictionary_size = len(term_dictionary)

        kmeans.seed_selection_algorithm(
            training_data_json = tfidf_vector_filename,
            number_of_batches  = number_of_batches,
            corpus_size        = term_dictionary_size,
            )

    # Run kmeans algorithm on our input data
    if run_training:
        print("Training kmeans model ... ")
        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            term_dictionary_size = len(term_dictionary)

        tf = []
        with open(tfidf_vector_filename, 'r', encoding='utf-8') as tfidf_file:
            for _, line in enumerate(tfidf_file):
                tf.append(json.loads(line))
        tf_size = len(tf)
        print("\nTOTAL NUMBER OF FILES : %s"%(str(tf_size)))

        if os.path.exists(centroid_filepath):
            os.remove(centroid_filepath)

        # Run kmeans clustering training
        final_assignments = kmeans.run_training_from_json(
            training_data_json  = tfidf_vector_filename,
            line_batch_size     = batch_size,
            number_of_batches   = number_of_batches,
            corpus_size         = term_dictionary_size,
            )

        cntr = Counter(final_assignments)
        print("\n***********************************************************")
        print("                        CLUSTERS SUMMARY                     ")
        print("*************************************************************")
        for cluster_id, cluster_count in cntr.items():
            print("\nCluster_%s | Number of documents : %s" %(str(cluster_id), str(cluster_count)))



    # Compute internal evaluation metrics
    if internal_validation_metrics:
        # Retrieve final centroids
        with open(centroid_filepath, 'rb') as cent:
            centroids = []
            for _,value in enumerate(cent):
                centroids.append(json.loads(value))

        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            term_dictionary_size = len(term_dictionary)

        intercluster_metric = kmeans.calculate_internal_validation_metrics(
            centroid_list = centroids,
            corpus_size   = term_dictionary_size,
            )
        for idx, value in enumerate(intercluster_metric):
            print("\nCluster : %s | Inter-Cluster Score : %s" %(str(idx), str(value)))


    # Run testing to retrieve the cluster and the top 10 most similar vectors to our input test vector
    if run_testing:
        print("\nTesting input")
        text_input = '''
        Meditation focused on self-observation of the body impairs metacognitive efficiency.In the last decade of research on metacognition, the literature has been focused on understanding its mechanism, function and scope; however, little is known about whether metacognitive capacity can be trained. The specificity of the potential training procedure is in particular still largely unknown. In this study, we evaluate whether metacognition is trainable through generic meditation training, and if so, which component of meditation would be instrumental in this improvement. To this end, we evaluated participants' metacognitive efficiency before and after two types of meditation training protocols: the first focused on mental cues (Mental Monitoring [MM] training), whereas the second focused on body cues (Self-observation of the Body [SoB] training). Results indicated that while metacognitive efficiency was stable in MM training group, it was significantly reduced in the SoB group after training. This suggests that metacognition should not be conceived as a stable capacity but rather as a malleable skill.
        '''
        # Run input against tfidf model
        TF_x_IDF = tf_idf.process_text(
            text                     = text_input,
            corpus                   = corpus_name,
            phrase_identification    = phrase_identification, #does something
            named_entity_recognition = named_entity_recognition,
            collocations_finder      = collocations_finder, #does something
            frequency_filter         = 2, #4
            number_of_ngrams         = 20,
        )

        with open(term_dictionary_filename, 'r', encoding='utf-8') as term_dictionary_file:
            term_dictionary = json.loads(term_dictionary_file.read())
            term_dictionary_size = len(term_dictionary)

        # Resize test input array
        term_ids = []
        tfidf_values = []
        for v in TF_x_IDF:
            print('%-15s %s' % (str(v[0]), str(v[1])) )
            try:
                term_ids.append(term_dictionary[str(v[0])])
                tfidf_values.append(v[1])
            except:
                pass

        if len(term_ids) > 0:
            # Make input dictionary
            test_vector = sorted(zip(term_ids, tfidf_values))
            top_n, cluster_value = kmeans.run_model(
                test_input = test_vector,
                corpus_size = term_dictionary_size,
                )

            with open(reversed_document_dictionary_filename, 'r', encoding='utf-8') as doc_dictionary_file:
                reversed_document_dictionary = json.loads(doc_dictionary_file.read())

            similar_documents  = []
            for top in top_n:
                similar_documents.append(reversed_document_dictionary[str(top)])

            total = zip(top_n,similar_documents)

            print("\nThe document belongs to cluster: %s" %(str(cluster_value)))
            print("\nThe top 10 most similar document identifiers to our input document are:")
            for val in total:
                print("Document ID: %s | Document Name: %s" %(str(val[0]), str(val[1])))

        else:
            print("\nNot enough terms in the text to be able to find a cluster. Try again with more text")

    # Upload model files
    if upload_model_files:
        logger.info('-------------------------------------------------------------------------------------------------')
        logger.info('Tarball and upload model to blob storage\n')

        # Construct the tarball file name
        cluster_model_filename = model_name + '_' + model_version + '.tar.gz'
        centroid_filename      = 'centroid_list.json'
        optimal_centroids      = 'optimal_seeds.json'
        cluster_assignments    = 'cluster_assignments.pickle'
        # Tarball the model files
        tarball_command = 'tar -cvf saved_models/{0} saved_models/{1} saved_models/{2} saved_models/{3}'.format(
            cluster_model_filename,
            cluster_assignments,
            centroid_filename,
            optimal_centroids,
        )
        logger.debug('Tarballing file...')
        os.system(tarball_command)

        s3_interface = AWS_s3_interface(bucket_name = s3_upload_bucket)
        s3_interface.upload_file(
            local_data_directory = model_directory,
            local_file_name      = cluster_model_filename,
        )

        # Delete the local tarball file
        rm_command = 'rm {0}'.format(os.path.join(model_directory, cluster_model_filename))
        logger.debug('Deleting local tarball')
        os.system(rm_command)

    # Delete temp data directory
    if delete_blob_temp_directory:
        print('Delete local temp directory')
        remove_data = 'rm -r %s' % (data_directory,)
        logger.debug(remove_data)
        os.system(remove_data)
