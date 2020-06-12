from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import os
from scipy.interpolate import interp1d
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import argparse


def get_rid_of_num(name):
    while(name[-1].isdigit()):
        del name[-1]
    return ''.join(name)


def merge_runs(dir_path, result_name, new_dir_name='tf_merged', tensorboard=False):
    diff_run_types = list(set([get_rid_of_num(list(name)) for name in os.listdir(dir_path) if name != 'merge_runs.py']))
    summary_iterators = []
    for name in diff_run_types:
        summary_iterators.append([EventAccumulator(os.path.join(dir_path, dname)).Reload()
                                  for dname in os.listdir(dir_path) if name in dname])
    tags = [iterator[0].Tags()['scalars'] for iterator in summary_iterators]
    for idx, sum_it in enumerate(summary_iterators):
        for it in sum_it:
            assert it.Tags()['scalars'] == tags[idx]
    to_merge = ['episode_reward']
    for tag in to_merge:
        fig, ax = plt.subplots(1)
        ax.set_title(tag)
        ax.set_xlabel('steps')
        ax.set_ylabel('episode reward')
        ax.grid()
        colors = ['red', 'green', 'blue', 'yellow']
        fig.tight_layout()
        for idx, sum_it in enumerate(summary_iterators):
            summaries_events = [summary.Scalars(tag) for summary in sum_it]
            end_point = min([events[-1].step for events in summaries_events])
            start_point = max([events[0].step for events in summaries_events])
            steps = [step for step in range(start_point, end_point + 1)]
            interpolated_data = []
            for events in summaries_events:
                event_steps = [event.step for event in events]
                event_data = [event.value for event in events]
                interpolated_data.append(interp1d(event_steps, event_data))

            matrix_form = []
            for step in steps:
                matrix_form.append([data(step).item(0) for data in interpolated_data])

            matrix_form = np.asarray(matrix_form)
            max_values = np.amax(matrix_form, axis=1)
            min_values = np.amin(matrix_form, axis=1)
            mean = matrix_form.mean(axis=1)
            sigma = matrix_form.std(axis=1)

            #fig, ax = plt.subplots(1)
            ax.plot(steps, mean, lw=1, label=diff_run_types[idx], color=colors[idx % len(colors)])
            ax.fill_between(steps, mean + sigma, mean - sigma, facecolor=colors[idx % len(colors)], alpha=0.5)

            if tensorboard:
                merged_data_ = tf.placeholder(tf.float32)
                summary_op = tf.summary.histogram(tag + '_merged', merged_data_)
                with tf.Session() as sess:
                    writer = tf.summary.FileWriter('./log/' + new_dir_name)
                    for step in steps:
                        merged_summary = sess.run(summary_op, feed_dict={merged_data_: [data(step).item(0) for data in interpolated_data]})
                        writer.add_summary(merged_summary, step)
        lgd = ax.legend(loc='upper left')
        plt.savefig(result_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.close()
        # plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('work_directory', type=str, help='work directory path')
    parser.add_argument('result_name', type=str, help='result graph name')
    args = parser.parse_args()
    merge_runs(args.work_directory, args.result_name)





