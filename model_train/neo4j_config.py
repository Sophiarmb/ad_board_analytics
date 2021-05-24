neo4j_config = {
    'neo4j_bolt_server'          : 'bolt://127.0.0.1:7687',
    'neo4j_user'                 : 'neo4j',
    'neo4j_password'             : 'Ch1c@g0!',
    'node'                       : {
        'term': {
            'label' : 'term',
            'uid'   : 'term',
            'attrs' : {
                'ngram_type' : 'ngram_type'
            },
        },
        'document': {
            'label' : 'document',
            'uid'   : 'filename',
            'attrs' : {
                'source'      : 'source',
                'filename'    : 'filename',
                'text'        : 'text',
                'word_length' : 'word_length',
            },
        },
        'corpus': {
            'label' : 'corpus',
            'uid'   : 'name',
            'attrs' : {
                'name'        : 'name',
                'description' : 'description',
            },
        },
        'document_corpus': {
            'label' : 'document_corpus',
            'uid'   : 'document_corpus',
            'attrs' : {
                'document_corpus' : 'document_corpus',  ## use the form `documentName_corpusName` for this
            },
        },
        'document_category': {
            'label' : 'document_category',
            'uid'   : 'category',
            'attrs' : {},
        },
        'named_entity_tag':{
            'label' : 'named_entity_tag',
            'uid'   : 'named_entity_tag',
            'attrs' : {},
        },
        'concept': {
            'label' : 'concept',
            'uid'   : 'concept_name',
            'attrs' : {},
        },
    },
    'relationship' : {
        'term_frequency': {
            'label'     : 'term_frequency',
            'from_node' : 'term',
            'from_node_uid': 'term',
            'to_node'   : 'document',
            'to_node_uid' : 'filename',
            'uid'       : '',
            'attrs'     : {
                'value': 'value',
            },
        },
        'in_corpus': {
            'label'     : 'in_corpus',
            'from_node' : 'document',
            'from_node_uid': 'filename',
            'to_node'   : 'corpus',
            'to_node_uid': 'name',
            'uid'       : '',
            'attrs'     : {},
        },
        'document_frequency': {
            'label'     : 'document_frequency',
            'from_node' : 'term',
            'from_node_uid': 'term',
            'to_node'   : 'corpus',
            'to_node_uid': 'name',
            'uid'       : '',
            'attrs'     : {
                'value': 'value',
            },
        },
        'tfidf': {
            'label'     : 'tfidf',
            'from_node' : 'term',
            'from_node_uid': 'term',
            'to_node'   : 'document_corpus',
            'to_node_uid': 'document_corpus',
            'uid'       : '',
            'attrs'     : {
                'value': 'value',
            },
        },
        'related_to_corpus' : {
            'label'     : 'related_to_corpus',
            'from_node' : 'document_corpus',
            'from_node_uid': 'document_corpus',
            'to_node'   : 'corpus',
            'to_node_uid': 'name',
            'uid'       : '',
            'attrs'     : {},
        },
        'related_to_document': {
            'label'     : 'related_to_document',
            'from_node' : 'document_corpus',
            'from_node_uid': 'document_corpus',
            'to_node'   : 'document',
            'to_node_uid': 'filename',
            'uid'       : '',
            'attrs'     : {},
        },
        'most_frequent_term': {
            'label'     : 'most_frequent_term',
            'from_node' : 'document',
            'from_node_uid': 'filename',
            'to_node'   : 'term',
            'to_node_uid': 'term',
            'uid'       : '',
            'attrs'     : {
                'value' : 'value',  ## word count
            },
        },
        'in_document_category': {
            'label'     : 'in_document_category',
            'from_node' : 'document',
            'from_node_uid': 'filename',
            'to_node'   : 'document_category',
            'to_node_uid': 'category',
            'uid'       : '',
            'attrs'     : {},
        },
        'related_to_tag': {
            'label'     : 'related_to_tag',
            'from_node' : 'term',
            'from_node_uid': 'term',
            'to_node'   : 'named_entity_tag',
            'to_node_uid': 'named_entity_tag',
            'uid'       : '',
            'attrs'     : {},
        },
        'related_to_concept': {
            'label'     : 'related_to_concept',
            'from_node' : 'document',
            'from_node_uid': 'filename',
            'to_node'   : 'concept',
            'to_node_uid': 'concept_name',
            'uid'       : '',
            'attrs'     : {
                'value' : 'value',  ## MLP score
            },
        },
    },
}
