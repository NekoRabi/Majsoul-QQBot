import asyncio


def finish_all_asytasks(task_funs:list)->list:
    tasks = []
    for task in task_funs:
        tasks.append(asyncio.ensure_future(task))
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)
    content = []
    for results in tasks.result():
        content.append(results)
    return content