from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import os
from scipy.interpolate import interp1d
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np


def merge_runs(dir_path, new_dir_name, tensorboard=False):
    summary_iterators = [EventAccumulator(os.path.join(dir_path, dname)).Reload() for dname in os.listdir(dir_path)]
    tags = summary_iterators[0].Tags()['scalars']
    for it in summary_iterators:
        assert it.Tags()['scalars'] == tags
    to_merge = ['episode_reward']
    for tag in to_merge:
        summaries_events = [summary.Scalars(tag) for summary in summary_iterators]
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

        fig, ax = plt.subplots(1)
        ax.plot(steps, mean, lw=2, label='mean', color='blue')
        ax.fill_between(steps, mean + sigma, mean - sigma, facecolor='blue', alpha=0.5)
        ax.set_title(r'title')
        ax.legend(loc='upper left')
        ax.set_xlabel('steps')
        ax.set_ylabel('episode reward')
        ax.grid()
        plt.show()

        if tensorboard:
            merged_data_ = tf.placeholder(tf.float32)
            summary_op = tf.summary.histogram(tag + '_merged', merged_data_)
            with tf.Session() as sess:
                writer = tf.summary.FileWriter('./log/' + new_dir_name)
                for step in steps:
                    merged_summary = sess.run(summary_op, feed_dict={merged_data_: [data(step).item(0) for data in interpolated_data]})
                    writer.add_summary(merged_summary, step)


if __name__ == '__main__':
    merge_runs('./log', 'merged')





