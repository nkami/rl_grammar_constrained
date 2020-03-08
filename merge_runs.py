from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import os
from scipy.interpolate import interp1d
import tensorflow as tf


def merge_runs(dir_path, new_dir_name):
    summary_iterators = [EventAccumulator(os.path.join(dir_path, dname)).Reload() for dname in os.listdir(dir_path)]
    tags = summary_iterators[0].Tags()['scalars']
    for it in summary_iterators:
        assert it.Tags()['scalars'] == tags
    to_merge = ['episode_reward']
    for tag in to_merge:
        summaries_events = [summary.Scalars(tag) for summary in summary_iterators]
        end_point = min([events[-1].step for events in summaries_events])
        start_point = max([events[0].step for events in summaries_events])
        interpolated_data = []
        for events in summaries_events:
            steps = [event.step for event in events]
            data = [event.value for event in events]
            interpolated_data.append(interp1d(steps, data))

        merged_data_ = tf.placeholder(tf.float32)
        summary_op = tf.summary.histogram(tag + '_merged', merged_data_)
        with tf.Session() as sess:
            writer = tf.summary.FileWriter('./log/' + new_dir_name)
            for step in range(start_point, end_point + 1):
                merged_summary = sess.run(summary_op, feed_dict={merged_data_: [data(step).item(0) for data in interpolated_data]})
                writer.add_summary(merged_summary, step)


if __name__ == '__main__':
    merge_runs('./log', 'merged')

    # merged_data_ = tf.placeholder(tf.float32)
    # summary_op = tf.summary.histogram('test', merged_data_)
    # with tf.Session() as sess:
    #     writer = tf.summary.FileWriter('./log/tmp')
    #     for step in range(0, 100):
    #         merged_summary = sess.run(summary_op, feed_dict={merged_data_: [x for x in range(step, step + 10)]})
    #         writer.add_summary(merged_summary, step)




