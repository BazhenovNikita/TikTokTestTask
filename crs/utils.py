from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
import concurrent.futures
from TikTokApi import TikTokApi, exceptions
from yt_dlp import YoutubeDL, DownloadError
import ffmpeg
import os
from enviorment import *
errors_list = set()
processed = 0


async def get_urls_of_videos(needed_videos=5):
    global processed
    processed = needed_videos
    list_of_urls = []
    count = 0
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, headless=False)
        while count < needed_videos:
            async for video in api.trending.videos(count=20):
                if count >= needed_videos:
                    break
                url = f'https://www.tiktok.com/@{video.author.username}/video/{video.id}'
                list_of_urls.append(url)
                count += 1
    return list_of_urls


def __download_video(video_url):
    global errors_list, processed
    try:
        ydl = YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(video_url, download=True)
        processed += 1
        return ydl.prepare_filename(info_dict).replace('\\', '/')
    except DownloadError as e:
        errors_list.add(str(e))
    except Exception as e:
        errors_list.add(str(e))


def download_videos(video_urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for video_url in video_urls:
            future = executor.submit(__download_video, video_url)
            futures.append(future)
    return futures


def process_videos(filenames):
    with ProcessPoolExecutor(max_workers=4) as executor:
        for filename in filenames:
            filename = filename.result()
            print(filename)
            executor.submit(__process_video, filename)


def __process_video(video_path, audio_path='../song.mp3'):
    global processed
    try:
        output_path = os.path.join('../videos', f"temp_{os.path.basename(video_path)}")
        (
            ffmpeg
            .input(video_path)
            .filter('setpts', f'PTS/{0.9}')
            .filter('scale', f'trunc(iw*{0.9}/2)*2', f'trunc(ih*{0.9}/2)*2')
            .output(output_path, vcodec='libx264', acodec='aac', preset='ultrafast')
            .global_args('-y')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        video_part = ffmpeg.input(output_path)
        audio_part = ffmpeg.input(audio_path)
        (
            ffmpeg
            .output(audio_part.audio, video_part.video, video_path, shortest=None, vcodec='copy')
            .global_args('-y')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        os.remove(output_path)
        processed += 1
    except exceptions as e:
        errors_list.add(str(e))
    except Exception as e:
        errors_list.add(str(e))


def generate_report(video_count, time, issues):
    markdown_report = f"""
    # Отчет о выполненных действиях

    **Количество обработанных видео:** {video_count}

    **Время, затраченное на весь процесс:** {time:.2f} секунд

    ## Проблемы, с которыми столкнулись и их решения

    """
    if issues:
        for issue in issues:
            markdown_report += f"- {issue}\n"
    else:
        markdown_report += "Не было проблем.\n"

    with open('../report.md', 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_report)


def get_stats():
    return processed, errors_list
