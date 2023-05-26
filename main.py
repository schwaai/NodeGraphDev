import asyncio
import os
import shutil
import threading

from args import args

if os.name == "nt":
    import logging

    logging.getLogger("xformers").addFilter(
        lambda record: 'A matching Triton is not available' not in record.getMessage())

import yaml

import execution
import folder_paths
import server
from nodes import init_custom_nodes


def exec_worker(q, server):
    e = execution.PromptExecutor(server)
    while True:
        item, item_id = q.get()
        e.execute(item[2], item[1], item[3], item[4])
        q.task_done(item_id, e.outputs_ui)


async def run(server, address='', port=8188, verbose=True, call_on_start=None):
    await asyncio.gather(server.start(address, port, verbose, call_on_start), server.publish_loop())


def hijack_progress(server):
    def hook(value, total):
        server.send_sync("progress", {"value": value, "max": total}, server.client_id)
    # comfy.utils.set_progress_bar_global_hook(hook)


def cleanup_temp():
    temp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def load_extra_path_config(yaml_path):
    with open(yaml_path, 'r') as stream:
        config = yaml.safe_load(stream)
    for c in config:
        conf = config[c]
        if conf is None:
            continue
        base_path = None
        if "base_path" in conf:
            base_path = conf.pop("base_path")
        for x in conf:
            for y in conf[x].split("\n"):
                if len(y) == 0:
                    continue
                full_path = y
                if base_path is not None:
                    full_path = os.path.join(base_path, full_path)
                print("Adding extra search path", x, full_path)
                folder_paths.add_model_folder_path(x, full_path)


server_obj_holder = [{"server_strings":{}}]
if __name__ == "__main__":
    from nodes import init_custom_nodes

    init_custom_nodes()
    cleanup_temp()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server_tmp = server.ExecServer(loop)
    server.PromptServer = server_tmp
    server = server_tmp

    q = execution.ExecQueue(server)

    server.add_routes()
    hijack_progress(server)

    threading.Thread(target=exec_worker, daemon=True, args=(q, server,)).start()

    address = args.listen

    port = args.port

    call_on_start = None

    if os.name == "nt":
        try:
            loop.run_until_complete(
                run(server, address=address, port=port, call_on_start=call_on_start))
        except KeyboardInterrupt:
            pass
    else:
        loop.run_until_complete(
            run(server, address=address, port=port, call_on_start=call_on_start))

    cleanup_temp()
