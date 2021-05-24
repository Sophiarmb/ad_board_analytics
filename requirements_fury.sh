# Warning: do NOT run with `sudo` because $GEMFURY_TOKEN won't be recognized
pip3 install neo4j_interface==2.0.1 --index-url https://$GEMFURY_TOKEN:@pypi.fury.io/rmarkbioinc/
pip3 install svd_recommendation_engine==2.0.0 --index-url https://${GEMFURY_TOKEN}:@pypi.fury.io/rmarkbioinc/
pip3 install nlp_tfidf==3.1.1 --index-url https://${GEMFURY_TOKEN}:@pypi.fury.io/rmarkbioinc/
pip3 install aws_blob_interface==2.0.1 --index-url https://${GEMFURY_TOKEN}:@pypi.fury.io/rmarkbioinc/
pip3 install unsupervised_document_clustering==1.0.1 --index-url https://${GEMFURY_TOKEN}:@pypi.fury.io/rmarkbioinc/
pip3 install aspectextraction==v2.0.0 --index-url https://${GEMFURY_TOKEN}:@pypi.fury.io/rmarkbioinc/

