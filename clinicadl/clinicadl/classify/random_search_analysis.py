"""
Produces a tsv file to analyze the performance of one launch of the random search.
"""
import os
from os import path
import pandas as pd
import numpy as np
from warnings import warn


def random_search_analysis(launch_dir, splits):

    jobs_list = os.listdir(launch_dir)
    jobs_list = [job for job in jobs_list if job[0:4] == 'job_']

    for selection in ['balanced_accuracy', 'loss']:

        columns = ['run', '>0.5', '>0.55', '>0.6', '>0.65', '>0.7', '>0.75', '>0.8', '>0.85', '>0.9', '>0.95', 'folds']
        output_df = pd.DataFrame(columns=columns)
        thresholds = np.arange(0.5, 1, 0.05)
        thresholds = np.insert(thresholds, 0, 0)

        for job in jobs_list:

            valid_accuracies = []
            for fold in splits:
                performance_path = path.join(launch_dir, job, f'fold-{fold}', 'cnn_classification', f'best_{selection}')
                if path.exists(performance_path):
                    valid_df = pd.read_csv(path.join(performance_path, 'validation_image_level_metrics.tsv'), sep='\t')
                    valid_accuracies.append(valid_df.loc[0, 'balanced_accuracy'].astype(float))
                else:
                    warn(f"The fold {fold} doesn't exist for job {job}")

            # Find the mean value of all existing folds
            if len(valid_accuracies) > 0:
                bac_valid = np.mean(valid_accuracies)
                row = (bac_valid > thresholds).astype(int)
            else:
                row = np.zeros(len(thresholds), dtype=int)
            row = np.concatenate([row, [len(valid_accuracies)]])
            row_df = pd.DataFrame(index=[job], data=row.reshape(1, -1), columns=columns)
            output_df = pd.concat([output_df, row_df])

        total_df = pd.DataFrame(np.array(output_df.sum()).reshape(1, -1), columns=columns, index=['total'])
        output_df = pd.concat([output_df, total_df])
        output_df.sort_index(inplace=True)

        output_df.to_csv(path.join(launch_dir, "analysis_" + selection + '.tsv'), sep='\t')