#!/usr/bin/python
# coding: utf8
#
import json
import os
import sys
import importlib
importlib.reload(sys)
import io
import unidecode
import csv
import logging
import pandas as pd
import numpy as np
import string
import en_coref_sm
from datetime import datetime
from collections import Counter
import tarfile
import pickle
from kmeans_clustering.kmeans_clustering import kmeans_clustering
from aspectextraction.aspect_extraction import AspectExtraction
from tfidf.tfidf import TF_IDF
from aws_s3_interface.aws_s3_interface import AWS_s3_interface
#from neo4j_config import neo4j_config
#from neo4j_build import NEO4J_BUILD
from tools import get_or_create_directory, local_corpus_filenames

NEO4J_USERNAME = os.environ['NEO4J_USERNAME']
NEO4J_PASSWORD = os.environ['NEO4J_PASSWORD']
NEO4J_BOLT = os.environ['NEO4J_BOLT']

neo4j_credentials = {
    'neo4j_username': NEO4J_USERNAME,
    'neo4j_password': NEO4J_PASSWORD,
    'neo4j_bolt': NEO4J_BOLT,
}

# -------------------------------------------------------------------------------------------------
# Logging
logger = logging.getLogger('PubMed NLP Logging')
logger.setLevel(logging.DEBUG)   # determine the level of severity to pass to handlers
log_directory = '/home/rmarkbio/logs/'
#log_directory = str(options['log_path'])
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

# Instantiate aspect extraction class
aspect_extraction_class = AspectExtraction(
    logger             = logger,
    log_path           = log_path,
    input_filepath     = 'data/',
    output_filepath    = 'data/',
    separate_sentences = False,
    batch_size         = 4,
    )

# Read csv files
csv_1 = pd.read_csv('data/members-transcript_abbott-2020-02-17-steering-committee_abbott-food-for-thought-february-session.csv', skiprows = [0])
csv1_select = csv_1[['Subtopic','Question Title', 'Advisor Comment', 'Replied to Response']]

csv_2 = pd.read_csv('data/members-transcript_abbvie-2020-12-02-duopa-treatment-team-virtual-advisory-board_duopa-treatment.csv')
csv2_select = csv_2[['Subtopic','Question Title', 'Advisor Comment', 'Replied to Response']]

# Combine csvs
csv_3 = pd.concat([csv1_select, csv2_select], ignore_index=True)

# Replace nans with ''
csv_4 = csv_3.replace(np.nan, '', regex=True)
csv_4['Review'] = [ ' '.join([str(x), str(y)]) for x, y in zip(csv_4['Advisor Comment'], csv_4['Replied to Response'])]

# Group by questions
#grouped_subtopic = csv_4.groupby(['Subtopic','Review'])
csv_4['Review'] = csv_4.groupby(['Subtopic'])['Review'].transform(lambda x : ' '.join(x))
csv_5 = csv_4[['Subtopic','Review']]
csv_5 = csv_5.drop_duplicates() 
csv_5.to_csv('data/groupedby_suptopic.csv')
corpus_directory = 'data'
subtopic_aspect_terms = []

### Perform aspect extraction for each subtopic
#for idx,textrow in csv_5.iterrows():
#    subtopic = textrow['Subtopic']
#    review_text = textrow['Review']
#    unaccented_string = unidecode.unidecode(review_text)
#    text_tuple = tuple((corpus_directory, unaccented_string))
#    aspect_terms = aspect_extraction_class.process_string(review = text_tuple, top_n = 10)
#    subtopic_aspect_terms.append(aspect_terms[0]['aspect_terms'])
#
#csv_5['aspect_terms'] = subtopic_aspect_terms
#csv_5.to_csv('data/subtopic_aspects.csv', index=False)

## Question level aspect terms
##qdf = csv_3.replace(np.nan, '', regex=True)
##qdf['Review'] = [ ' '.join([str(x), str(y)]) for x, y in zip(qdf['Advisor Comment'], qdf['Replied to Response'])]
###grouped_qs = qdf.groupby(['Question Title','Review'])
##qdf['all_reviews'] = qdf.groupby(['Question Title'])['Review'].transform(lambda x : ' '.join(x))
##csv_6 = qdf[['Question Title','all_reviews']]
##csv_7 = csv_6.drop_duplicates()
##print(csv_7.head)
##print(csv_7.shape)
##
##csv_7.to_csv('data/grouped_qs.csv', header = ['Question Title', 'all_reviews'], index = False)
##
##i=0
###print(len(csv_7))
###
##for index, row in csv_7.iterrows():
##    rowtext = unidecode.unidecode(row[1])
##    print("\n\n\n")
##    print(rowtext)
##    if i > len(csv_7):
##       break
##    else:
##       f = open('data/'+str(i)+'.txt', 'w')
##       f.write(rowtext)
##       f.close()
##       i+=1
#
#
#question_aspect_terms = []
#### Perform aspect extraction for each subtopic
#for idx,textrow in csv_7.iterrows():
#    subtopic = textrow['Question Title']
#    review_text = textrow['all_reviews']
#    unaccented_string = unidecode.unidecode(review_text)
#    text_tuple = tuple((corpus_directory, unaccented_string))
#    aspect_terms = aspect_extraction_class.process_string(review = text_tuple, top_n = 10)
#    question_aspect_terms.append(aspect_terms[0]['aspect_terms'])
#
#csv_7['question_aspect_terms'] = question_aspect_terms

cdf = pd.read_csv('data/question_level_aspects.csv')
aterms = cdf['QUESTION_LEVEL_ASPECT_TERMS']

from nltk.corpus import wordnet
for arow in aterms:
    for eachword in arow:
        syn = wordnet.synsets(eachword)
        print(syn.hypernyms())
#csv_7.to_csv('data/question_level_aspects.csv', index=False)


# Sentence level aspect extraction


# Perform document clustering on each response 
raw_filenames = local_corpus_filenames(
    corpus_path = 'data/adboard_text/',
    limit = 50,
    )

# Read cluster files
#with open('saved_models/cluster_assignments.pickle', 'rb') as pickle_file:
#    final_assignments = pickle.load(pickle_file)
#    for rowx in final_assignments:
#        print("\ndocument id")
#        print(rowx['document_id'])
#        print("\n cluster assignment")
#        print(rowx['cluster_assignment'])

# Do aspect extraction on each cluster
#aspect_terms = aspect_extraction_class.process_files(
#            corpus_filepath    = 'data/cluster_files/',
#            top_n              = 20
#        )
#
#cluster_ids = []
#cluster_topics = []
#print(aspect_terms)
#    print(eachrow[0])
#    cluster_id = eachrow['filename']
#    topics = eachrow['aspect_terms']
#    cluster_ids.append(cluster_ids)
#    cluster_topics.append(topics)
#
#cluster_topics_df = pd.DataFrame({'cluster_id' : cluster_ids, 'cluster_topics': cluster_topics})
#cluster_topics_df.to_csv('data/cluster_topics.csv', index=False)




