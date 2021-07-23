import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import os
import re
from scipy.stats import gmean

pwd = Path(os.path.dirname(os.path.realpath(__file__)))


def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod()**(1.0 / len(a))


def match_block_thread_size(line):
    """
    Args:
        line: a line of text.
    Return:
        Returns None if not matched.
        Returns OMP_NUM_THREADS value if matched.
    Ref:
        https://www.tutorialspoint.com/python/python_reg_expressions.htm
    """
    pattern = r"^# OPEN3D_PARFOR_BLOCK: ([0-9]+), OPEN3D_PARFOR_THREAD: ([0-9]+)"
    match = re.match(pattern, line)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None


def match_runtime(line):
    """
    Args:
        line: a line of text.
    Return:
        Returns None if not matched.
        Returns the runtime value (float) if the value is matched.
    Ref:
        https://stackoverflow.com/a/14550569/1255535
    """
    pattern = r"^.* +(\d+(?:\.\d+)?) ms +.*ms +([0-9]+)$"
    match = re.match(pattern, line)
    if match:
        return float(match.group(1)) / float(match.group(2))
    else:
        return None


def extract_cpu_prefix(filename):
    """
    Input:
        benchmark_Intel(R)_Core(TM)_i5-8265U_CPU_with_dummy.log
    Output:
        benchmark_Intel(R)_Core(TM)_i5-8265U_CPU
    """
    pattern = r"^(.*_CPU).*$"
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid log file {filename}")


def parse_file(log_file):
    """
    Returns: results, a list of directories, e.g.
        [
            {"num_threads": xxx, "gmean": xxx, "ICP": xxx, "Tensor": xxx},
            {"num_threads": xxx, "gmean": xxx, "ICP": xxx, "Tensor": xxx},
        ]
    """
    results = []
    with open(log_file) as f:
        lines = [line.strip() for line in f.readlines()]

        current_block_thread_size = None
        current_runtimes = []
        for line in lines:
            # Parse current line
            num_thread = match_block_thread_size(line)
            runtime = match_runtime(line)
            print(runtime)

            if num_thread:
                # If we already collected, save
                if current_block_thread_size:
                    results.append({
                        "block_size": current_block_thread_size[0],
                        "thread_size": current_block_thread_size[1],
                        "gmean": gmean(current_runtimes)
                    })
                # Reset to fresh
                current_block_thread_size = num_thread
                current_runtimes = []
            elif runtime:
                current_runtimes.append(runtime)

        # Save the last set of data
        if current_block_thread_size:
            results.append({
                "block_size": current_block_thread_size[0],
                "thread_size": current_block_thread_size[1],
                "gmean": gmean(current_runtimes)
            })
    return results


if __name__ == '__main__':

    log_file = pwd / "benchmark_simple.log"
    results = parse_file(log_file)
    print(results)

    # fig = plt.figure()
    # ax = fig.add_subplot(num_log_files, 1, idx + 1)
    # title = Path(log_file).name[len("benchmark_"):-len(".log")]
    # title = title.replace("_", " ")
    # xs = [result["num_threads"] for result in results]
    # ys = [result["gmean"] for result in results]
    # ax.plot(xs, ys, 'b-')
    # ax.plot(xs, ys, 'b*')
    # for x, y in zip(xs, ys):
    #     ax.annotate(f"{y:.2f}", xy=(x, y))
    # ax.set_ylim(ymin=0)
    # ax.set_title(title)
    # ax.set_xticks(np.arange(min(xs), max(xs) + 1, 1.0))
    # # ax.set_xlabel("# of threads")
    # ax.set_ylabel("Runtime gmean (ms)")
    # fig.tight_layout()

    # plt.show()

    # Y-axis
    block_sizes = [
        "cucumber", "tomato", "lettuce", "asparagus", "potato", "wheat",
        "barley"
    ]
    # X-axis
    thread_sizes = [
        "Farmer Joe", "Upland Bros.", "Smith Gardening", "Agrifun",
        "Organiculture", "BioGoods Ltd.", "Cornylee Corp."
    ]

    runtimes = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
                         [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
                         [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
                         [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
                         [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
                         [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
                         [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])

    fig, ax = plt.subplots()
    im = ax.imshow(runtimes)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(thread_sizes)))
    ax.set_yticks(np.arange(len(block_sizes)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(thread_sizes)
    ax.set_yticklabels(block_sizes)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(),
             rotation=45,
             ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(block_sizes)):
        for j in range(len(thread_sizes)):
            text = ax.text(j,
                           i,
                           runtimes[i, j],
                           ha="center",
                           va="center",
                           color="w")

    ax.set_title("Geometric-mean runtime v.s. block/thread size")
    ax.set_xlabel("block_sizes")
    fig.tight_layout()
    plt.show()