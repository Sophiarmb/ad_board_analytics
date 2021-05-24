import os

## Gather a list of filenames of the entire corpus.
#  @brief                  Assuming that a corpus of documents is saved to a local directory
#                          and each of those documents is its own text file, pass the relative
#                          path to the directory of that corpus and get a list of all file names
#                          in that directory.  It is assumed that each of those file names
#                          corresponds to a document text file that is part of the corpus to
#                          be processed into the graph database we're building.
# @param corpus_path       The relative path to the directory of the corpus.
# @param limit             Limit the number of files to this integer--used for testing and development.
# @retval corpus_filenames A list of strings that are the file names.
def local_corpus_filenames(
        corpus_path,
        limit = None,
    ):

    # Prepare a list of file names
    corpus_filenames = []
    i = 0
    for entry in os.scandir(corpus_path):
        if not entry.name.startswith('.') and entry.is_file():
            if limit is not None:
                if i >= limit:
                    break
            corpus_filenames.append(os.path.join(corpus_path, entry.name))
            i += 1

    return corpus_filenames

## Get the path for a directory by name `directory` for log file location.
#  @brief Log files are typically saved in a directory called `log` next to the
#         repository directory.  Get the path to that directory and create
#         if necessary.
#  @param directory The directory name for the log files.
#  @param now       A datetime for the current datetime, which will be the
#                   subdirectory that log files are actually saved to for a
#                   particular run of the code.
#  @retval log_path The final constructed path were log files should be saved.
def get_or_create_directory(directory, now):
    log_path          = directory + now
    directory_exists  = os.path.exists(log_path)

    if directory_exists == False:
        os.mkdir(log_path)
    return log_path

## This is a helper function specifically for `get_parallelization_epochs`.
#  @param n_size
#  @param n_start
#  @param n_chunks
#  @reval ranges
def get_ranges(n_size, n_start, n_chunks):
    ranges = []

    if n_size >= n_chunks:
        range_size = int(float(n_size) / n_chunks)
    else:
        range_size = 1

    for i in range(0, min((n_chunks-1)*range_size, n_size), range_size):
        ranges.append([n_start+i, n_start+i+range_size])

    if (n_chunks-1)*range_size < n_size:
        ranges.append([n_start+(n_chunks-1)*range_size, n_start+n_size])

    return ranges

## Partition a single list of indices into roughly equal segments to help
#  plan how work done using multiprocessing will be divided up.
#  @brief                         Suppose a list of indexes from 0 to `max_id` corresponds to some
#                                 processing work that needs to be done and we want to break it up into some number
#                                 of parallel processes over some other number of epochs.  This will produce a plan
#                                 for how to optimally divide up the work represented by those indices.
#  @param logger                  logging object
#  @param max_id                  The length of the list representing work to be done
#  @param N_epochs                The number of blocks to be executed in series.
#  @param N_execution_blocks      The number of blocks to be executed in parallel within each epoch.
#  @param is_list_of_list
#  @param id_pars
#  @retval epochs                 The execution plan
def get_parallelization_epochs(
        logger,
        max_id,
        N_epochs,
        N_execution_blocks,
        is_list_of_list = False,
        id_pairs = None,
    ):
    if N_epochs < 0 or N_execution_blocks < 0:
        return None

    epoch_ranges = get_ranges(max_id, 0, N_epochs)

    epochs = []
    for epoch_range in epoch_ranges:
        epoch_size = epoch_range[1] - epoch_range[0]
        execution_ranges = get_ranges(epoch_size, epoch_range[0], N_execution_blocks)
        epochs.append({
            'start_epoch'       : epoch_range[0],
            'end_epoch'         : epoch_range[1],
            'epoch_ranges'      : execution_ranges,
        })

    logger.info('-------------------------------')
    logger.info('Parallelization Execution Plan:')

    start_block, end_block = None, None
    for epoch in epochs:

        logger.info('    epoch start: ' + str(epoch['start_epoch']))
        logger.info('    epoch end  : ' + str(epoch['end_epoch']))

        for block in epoch['epoch_ranges']:
            if not is_list_of_list:
                logger.info('        Parallel block: ' + str(block))

            else:
                start_block = 0 if start_block is None else end_block
                end_block = start_block + sum([len(v) for v in id_pairs[block[0]:block[1]]])
                logger.info('        Parallel block: ' + str([start_block, end_block]))

    logger.info('-------------------------------')

    return epochs
