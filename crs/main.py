import asyncio
import multiprocessing
from time import time
from crs.utils import get_urls_of_videos, download_videos, process_videos, get_stats, generate_report

if __name__ == '__main__':
    start_time = time()
    multiprocessing.freeze_support()
    urls = asyncio.run(get_urls_of_videos())
    filenames = download_videos(urls)
    process_videos(filenames)
    processed, problems = get_stats()
    generate_report(processed, time() - start_time, list(problems))
