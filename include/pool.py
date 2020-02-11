from __future__ import print_function
import concurrent.futures

from include.colored import info

def pool(func, links, t_count):
    """
     Creates threadpool for processing URLS and executing function.
    """
    links = list(links)
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=t_count)

    processes = (threadpool.submit(func,links) for link in links)

    for c,_ in enumerate(concurrent.futures.as_completed(processes),1):
        if c == len(links) or c % t_count == 0:
            print('%s Progress: %i/%i' % (info, c, len(links)), end='\n')
