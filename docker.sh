#!/bin/bash
# docker file
# This script is intended to streamline the use of docker during development.
# We want to establish and follow some standards for building, running, and
# deploying between GitHub and Docker.  This script should be edited to control that.

# ARGUMENTS:
# "build"   : Build Docker Image
# "run"     : Create Docker Container From Image
# "release" : Tag and push to both GitHub and Docker Hub
# "terminal": Go to a running docker container in the terminal
# "start"   : Start an existing docker container that has been stopped.

set -e

# Project: Don't change this.  It sets the project name, for the purposes of this script,
# to the current directory name (sans the path), which should be the repo name.
PROJECT=${PWD##*/}
echo $PROJECT

# Version (JIRA Ticket Number AND git branch name)
VERSION="(untracked)"
branch_name="$(git symbolic-ref -q HEAD)"
VERSION=${branch_name:11}||$VERSION
echo $VERSION

# Don't change this.  Our base docker images have an
# established user called "rmarkbio" inside the container whose password
# is "##rmarkbio%%".
USER_NAME=rmarkbio

# This is the base docker image that we are starting with
IMAGE_NAME=$PROJECT

# This is the name of your local docker container that you will be developing in.
CONTAINER_NAME=$PROJECT\_$VERSION

# Take a user argument for what kind of docker action we want to do
ACTION=$1
MESSAGE=$2

case $ACTION in

    rmi)
        echo 'rmi: remove docker image'
        docker rmi rmarkbio/$IMAGE_NAME:$VERSION
        ;;

    rm)
        echo 'rm: remove docker container'
        docker rm $CONTAINER_NAME
        ;;

    build)
        echo 'build: Build Docker Image'

        # Build an image tagged with the JIRA ticket version
        docker build -t $USER_NAME/$IMAGE_NAME:$VERSION . --no-cache
        ;;

    run)
        echo 'run: Create Docker Container From Image'

        # Capture the AWS Access Key and set as an environmental variable.
        echo ''
        echo 'Enter the AWS Access Key'
        read aws_access_key_id
        if [ "$aws_access_key_id" = "" ]; then
            echo 'WARNING: No AWS Access Key value was set.'
            :
        else
            export AWS_ACCESS_KEY_ID=$aws_access_key_id
        fi

        # Capture the AWS Secret Access Key and set as an environmental variable.
        echo ''
        echo 'Enter the AWS Secret Access Key'
        read aws_secret_access_key
        if [ "$aws_secret_access_key" = "" ]; then
            echo 'WARNING: No AWS Secret Access Key value was set.'
            :
        else
            export AWS_SECRET_ACCESS_KEY=$aws_secret_access_key
        fi

        # Capture the AWS Default Region and set as an environmental variable.
        echo ''
        echo 'Enter the AWS Default Region'
        read aws_default_region
        if [ "$aws_default_region" = "" ]; then
            echo 'WARNING: No AWS Access Key value was set.'
            :
        else
            export AWS_DEFAULT_REGION=$aws_default_region
        fi

        # Capture the AWS Default Output and set as an environmental variable.
        echo ''
        echo 'Enter the AWS Default Output'
        read aws_default_output
        if [ "$aws_default_output" = "" ]; then
            echo 'WARNING: No AWS Default Output was set.'
            :
        else
            export AWS_DEFAULT_OUTPUT=$aws_default_output
        fi

        # Capture the Gemfury token and set as an environmental variable.
        echo ''
        echo 'Enter the Gemfury Access Token'
        read gemfury_token
        if [ "$gemfury_token" = "" ]; then
            echo 'WARNING: No Azure account name value was set.'
            :
        else
            export GEMFURY_TOKEN=$gemfury_token
        fi

        # Capture the Neo4j username and set as an environmental variable.
        echo ''
        echo 'Enter the Neo4j username'
        read neo4j_username
        if [ "$neo4j_username" = "" ]; then
            echo 'WARNING: No Azure account name value was set.'
            :
        else
            export NEO4J_USERNAME=$neo4j_username
        fi

        # Capture the Neo4j password and set as an environmental variable.
        echo ''
        echo 'Enter the Neo4j password'
        read neo4j_password
        if [ "$neo4j_password" = "" ]; then
            echo 'WARNING: No Azure account name value was set.'
            :
        else
            export NEO4J_PASSWORD=$neo4j_password
        fi

        # Capture the Neo4j Bolt address and set as an environmental variable.
        echo ''
        echo 'Enter the Neo4j Bolt address'
        read neo4j_bolt
        if [ "$neo4j_bolt" = "" ]; then
            echo 'WARNING: No Azure account name value was set.'
            :
        else
            export NEO4J_BOLT=$neo4j_bolt
        fi

        # -i for "interactive";
        # -t for "terminal";
        # --net="host" is for accessing the host (system) network from inside the container....
        #              ...which I need to access the bolt address.
        # -v to map the current directory to the container's working directory
        docker run -i -t \
            --entrypoint /bin/bash \
            --net="host" \
            --name=$CONTAINER_NAME \
            -v $PWD:/home/rmarkbio/project \
            -v $PWD/../logs:/home/rmarkbio/logs \
            -v ~/.ssh/id_rsa:/root/.ssh/id_rsa \
            -e GEMFURY_TOKEN=$GEMFURY_TOKEN \
            -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
            -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
            -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
            -e AWS_DEFAULT_OUTPUT=$AWS_DEFAULT_OUTPUT \
            -e NEO4J_USERNAME=$NEO4J_USERNAME \
            -e NEO4J_PASSWORD=$NEO4J_PASSWORD \
            -e NEO4J_BOLT=$NEO4J_BOLT \
            -e SAVED_MODELS=$SAVED_MODELS \
            $USER_NAME/$IMAGE_NAME:$VERSION
        ;;
    terminal)
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;

    stop)
        docker stop $CONTAINER_NAME
        ;;

    start)
        docker start -ai $CONTAINER_NAME
        ;;

    commit)
        if [ $# -eq 2 ]; then
            echo 'commit'
            echo 'VERSION: '$VERSION
            echo 'MESSAGE: '$MESSAGE

            # Commit message
            COMMIT_MESSAGE=$MESSAGE

            # Git commit
            git commit -am "$VERSION : $COMMIT_MESSAGE"

            # Commit, tag, and push the docker image for this update.
            docker commit $CONTAINER_NAME $USER_NAME/$IMAGE_NAME:$VERSION
            docker tag $USER_NAME/$IMAGE_NAME:$VERSION $USER_NAME/$IMAGE_NAME:latest
        else
            echo 'To commit, enter a commit message as a second argument in quotes.'
        fi
        ;;


    push)

        if [ $# -eq 2 ]; then
            echo 'push: Commit and push to both GitHub and Docker Hub'
            echo 'VERSION: '$VERSION
            echo 'MESSAGE: '$MESSAGE

            # Commit message
            COMMIT_MESSAGE=$MESSAGE

            # Git commit
            git commit -am "$VERSION : $COMMIT_MESSAGE"

            # Push the git branch to the origin
            git push origin $VERSION

            # Commit, tag, and push the docker image for this update.
            docker commit $CONTAINER_NAME $USER_NAME/$IMAGE_NAME:$VERSION
            docker tag $USER_NAME/$IMAGE_NAME:$VERSION $USER_NAME/$IMAGE_NAME:latest
        else
            echo 'To push, enter a commit message as a second argument in quotes.'
        fi
        ;;

esac
