import re
import sys

import networkx as nx


class Task:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def run(self, context, *args, **kwargs):
        print(f"Running task {self.name}")
        func = getattr(self, self.name, None)
        return func(context, *args, **kwargs)

    @staticmethod
    def start(context, value=100):
        context["value"] = value
        print("start with value %d" % value)
        return "success"

    @staticmethod
    def opx3p1(context):
        context["value"] = context.get("value") * 3 + 1
        print("value after *3+1: %d" % context["value"])
        return "success"

    @staticmethod
    def op_divide_by_2(context):
        context["value"] = context.get("value") // 2
        print("value after /2: %d" % context["value"])
        return "success"

    @staticmethod
    def is_odd(context):
        if context.get("value") % 2 == 0:
            return "no"
        else:
            return "yes"

    @staticmethod
    def is_one(context):
        if context.get("value") == 1:
            return "yes"
        else:
            return "no"

    @staticmethod
    def end(context):
        print("value end: %d" % context["value"])
        return "end"


def add_tasks_to_dag(dag, tasks: dict, op: str, next_op: str):
    match = re.match(r'(\w+)\((\w+)\)', op)
    try:
        if match:
            op_name, op_condition = match.groups()[0:2]
        else:
            op_name, op_condition = op, "success"
    except:
        op_name, op_condition = op, "success"
    if op_name not in tasks:
        tasks[op_name] = Task(op_name)
        dag.add_node(tasks[op_name])
    if next_op not in tasks:
        tasks[next_op] = Task(next_op)
        dag.add_node(tasks[next_op])
    dag.add_edge(tasks[op_name], tasks[next_op], condition=op_condition)


def flow2dag(flow_str: str) -> nx.DiGraph:
    dag = nx.DiGraph()
    tasks = {}
    for line in flow_str.split("\n"):
        parts = line.split('->')
        if len(parts) < 2:
            continue
        for i in range(0, len(parts) - 1):
            op, next_op = parts[i], parts[i + 1]
            add_tasks_to_dag(dag, tasks, op, next_op)
    return dag


init_value = int(sys.argv[1]) if len(sys.argv) > 1 else 100

'''
dag = nx.DiGraph()

task_start = Task("start")
task_opx3p1 = Task("opx3p1")
task_op_divide_by_2 = Task("op_divide_by_2")
task_is_odd = Task("is_odd")
task_is_one = Task("is_one")
task_end = Task("end")

dag.add_node(task_start)
dag.add_node(task_opx3p1)
dag.add_node(task_op_divide_by_2)
dag.add_node(task_is_odd)
dag.add_node(task_is_one)

dag.add_node(task_end)

dag.add_edge(task_start, task_is_one)
dag.add_edge(task_is_one, task_end, condition="stop")
dag.add_edge(task_is_one, task_is_odd, condition="continue")
dag.add_edge(task_is_odd, task_opx3p1, condition="odd")
dag.add_edge(task_is_odd, task_op_divide_by_2, condition="even")
dag.add_edge(task_opx3p1, task_is_one)
dag.add_edge(task_op_divide_by_2, task_is_one)

'''


def find_node_by_name(graph: nx.DiGraph, name):
    for node, _ in graph.nodes(data=True):
        if node.name == name:
            return node
    return None


flowchart = '''
```flow
start->is_one
is_one(yes)->end
is_one(no)->is_odd
is_odd(yes)->opx3p1
is_odd(no)->op_divide_by_2
opx3p1->is_one
op_divide_by_2->is_one
```
'''

dag = flow2dag(flowchart)
context = {}
current_task = find_node_by_name(dag, "start")
status = current_task.run(context, 10)

while current_task.name != "end":
    next_task = None
    for successor in dag.successors(current_task):
        edge_data = dag.get_edge_data(current_task, successor)
        if edge_data.get("condition", "success") == status:
            next_task = successor
            break
    if not next_task:
        print("No valid next task found, terminating.")
        break
    current_task = next_task
    status = current_task.run(context)

# current_task.run(context)
