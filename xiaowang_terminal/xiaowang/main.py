import argparse
import json
import os
import ast
import sys

import click
import pyarrow as pa
from dora import Node
from mofa.utils.install_pkg.load_task_weaver_result import extract_important_content

RUNNER_CI = True if os.getenv("CI") == "true" else False




def clean_string(input_string:str):
    return input_string.encode('utf-8', 'replace').decode('utf-8')
def send_task_and_receive_data(node):
    while True:
        data = input("说吧，什么事:")
        #click.echo(f"111")
        node.send_output("data", pa.array([clean_string(data)]))
        #click.echo(f"222")
        event = node.next(timeout=200)
        #click.echo(f"333")
        if event is not None:
            while True:
                if event is not None:
                    #处理任务结果选择性展示
                    #print(event)
                    #print("-------------------------")
                    #print(event['id'])
                    node_results = json.loads(event['value'].to_pylist()[0])
                    results = node_results.get('node_results')
                    is_dataflow_end = node_results.get('dataflow_status', False)
                    layer=node_results.get('layer',-1)
                    #print(results)
                    if event['id']=="agent_DLCout":
                        layer=node_results.get('layer')
                        #这是动态规划节点不做任何操作
                        print(f"DynamicNeuron:{layer}")

                    if event['id']=="agent_generateout":
                        layer=node_results.get('layer')
                        #agent节点，看情况决定是否最终输出
                        print(f"-{layer+1}-agent:{results}")

                    if event['id']=="agent_reflectionout":
                        #layer=node_results.get('layer')
                        #agent节点，看情况决定是否最终输出
                        #print("------========")
                        print(f"reflectionagent:{results}")
                    if layer==0:
                        is_dataflow_end=True
                    sys.stdout.flush()
                    #if input("是否继续？(y/n)") == "n":
                        #ptint("好的")
                        #break
                    if is_dataflow_end:
                        print("回答结束")
                        break
                    #print(is_dataflow_end)
                    event = node.next(timeout=200)
                    #sys.exit()
def main():

    # Handle dynamic nodes, ask for the name of the node in the dataflow, and the same values as the ENV variables.
    parser = argparse.ArgumentParser(description="Simple arrow sender")

    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="The name of the node in the dataflow.",
        default="xiaowang_terminal",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=False,
        help="Arrow Data as string.",
        default=None,
    )

    args = parser.parse_args()

    data = os.getenv("DATA", args.data)

    node = Node(
        args.name
    )  # provide the name to connect to the dataflow if dynamic node

    if data is None and os.getenv("DORA_NODE_CONFIG") is None:
        send_task_and_receive_data(node)


if __name__ == "__main__":
    main()
