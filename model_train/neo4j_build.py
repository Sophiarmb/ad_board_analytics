# Organize parameters relevant to building the *.csv output files
# that will be used to build a Neo4j database.
NEO4J_BUILD = {
    'node': {
        'corpus': {
            'source_uid_column_name' : 'corpus_name',
            'base_target_file_name': 'node_corpus',
            'header': {
                'corpus_name' : 'corpus_name',
            },
            'attrs': {},
        },
        'term' : {
            'source_uid_column_name' : 'term',
            'base_target_file_name': 'node_term',
            'header': {
                'term': 'term',
                'ngram_type': 'ngram_type',
            },
            'attrs': {
                'ngram_type': 'ngram_type',
            },
        },
        'document': {
            'source_uid_column_name' : 'document',
            'base_target_file_name': 'node_document',
            'header': {
                'document': 'document',
                'word_length': 'word_length',
            },
            'attrs': {
                'word_length': 'word_length',
            },
        },
        'document_corpus': {
            'source_uid_column_name' : 'document_corpus',
            'base_target_file_name': 'node_document_corpus',
            'header': {
                'document_corpus': 'document_corpus',
            },
            'attrs': {},
        },
        'document_category': {
            'source_uid_column_name' : 'category',
            'base_target_file_name': 'node_document_category',
            'header': {
                'category': 'category',
            },
            'attrs': {},
        },
        # This second file is for MLP classification nodes, as opposed to
        # training, test, and validation
        'document_category_labels': {
            'source_uid_column_name' : 'category',
            'base_target_file_name': 'node_document_category_labels',
            'header': {
                'category': 'category',
            },
            'attrs': {},
        },
        'named_entity_tag': {
            'source_uid_column_name' : 'named_entity',
            'base_target_file_name': 'node_named_entity',
            'header': {
                'named_entity': 'named_entity',
            },
            'attrs': {},
        },
    },
    'relationship': {
        'term_frequency': {
            'source_uid_from_column_name' : 'term',
            'source_uid_to_column_name' : 'document',
            'base_target_file_name': 'relationship_term_frequency',
            'header': {
                'term': 'term',
                'document': 'document',
                'value': 'value',
            },
            'attrs': {
                'value': 'value',
            },
        },
        'in_corpus': {
            'source_uid_from_column_name' : 'document',
            'source_uid_to_column_name' : 'corpus',
            'base_target_file_name': 'relationship_in_corpus',
            'header': {
                'document': 'document',
                'corpus': 'corpus',
            },
            'attrs': {},
        },
        'document_frequency': {
            'source_uid_from_column_name' : 'term',
            'source_uid_to_column_name' : 'corpus',
            'base_target_file_name': 'relationship_document_frequency',
            'header': {
                'term': 'term',
                'corpus': 'corpus',
                'value': 'value',
            },
            'attrs': {},
        },
        'tfidf': {
            'source_uid_from_column_name' : 'term',
            'source_uid_to_column_name' : 'document_corpus',
            'base_target_file_name': 'relationship_tfidf',
            'header': {
                'term': 'term',
                'document_corpus': 'document_corpus',
                'value': 'value',
            },
            'attrs': {},
        },
        'related_to_corpus' : {
            'source_uid_from_column_name' : 'document_corpus',
            'source_uid_to_column_name' : 'corpus',
            'base_target_file_name': 'relationship_related_to_corpus',
            'header': {
                'document_corpus': 'document_corpus',
                'corpus': 'corpus',
            },
            'attrs': {},
        },
        'related_to_document': {
            'source_uid_from_column_name' : 'document_corpus',
            'source_uid_to_column_name' : 'document',
            'base_target_file_name': 'relationship_related_to_document',
            'header': {
                'document_corpus': 'document_corpus',
                'document': 'document',
            },
            'attrs': {},
        },
        'most_frequent_term': {
            'source_uid_from_column_name' : 'document',
            'source_uid_to_column_name' : 'term',
            'base_target_file_name': 'relationship_most_frequent_term',
            'header': {
                'document': 'document',
                'term': 'term',
                'value': 'value',
            },
            'attrs': {
                'value': 'value',
            },
        },
        'in_document_category': {
            'source_uid_from_column_name' : 'document',
            'source_uid_to_column_name' : 'category',
            'base_target_file_name': 'relationship_in_document_category',
            'header': {
                'document': 'document',
                'category': 'category',
            },
            'attrs': {},
        },
        # This is a second `in_document_category` relationship file specifically for
        # MLP classification categories, as opposed to training, test, and validation.
        'in_document_category_labels': {
            'source_uid_from_column_name' : 'document',
            'source_uid_to_column_name' : 'category',
            'base_target_file_name': 'relationship_in_document_category_labels',
            'header': {
                'document': 'document',
                'category': 'category',
            },
            'attrs': {},
        },
        'related_to_tag': {
            'source_uid_from_column_name' : 'term',
            'source_uid_to_column_name' : 'named_entity_tag',
            'base_target_file_name': 'relationship_related_to_tag',
            'header': {
                'term': 'term',
                'named_entity_tag': 'named_entity_tag',
            },
            'attrs': {},
        },
    }
}
