# pylint: disable=missing-function-docstring,missing-module-docstring
import yt_dlp
from file_info import FileInfo
from file_manager import get_new_file_name

EXT="wav"
exceptions = {'Video': [], 'WAV': []}

def download_all_uris(urls_and_timestamps, logger, include_vid=False):
    logger.info("2. Downloading URLs")
    files_info = []
    for _, url in enumerate(urls_and_timestamps):
        try:
            download(link=url[0], logger=logger, preferred_codec=EXT, download_video=include_vid)
            append_file_to_file_list(files_info, url)
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            exit(1)
        except Exception as e:
            logger.error("Encountered exception: ", e, "for file: ", url)
    logger.info("2. Finished downloading")
    return files_info

def append_file_to_file_list(files_info, url):
    title = get_new_file_name(files_info)
    fi = FileInfo(f"{title}", url[1], url[0])
    files_info.append(fi)


def download(link, logger, preferred_codec='wav', download_video=False):
# Download audio
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': preferred_codec,
        'preferredquality': '320'
        }],
    'outtmpl': '%(title)s.%(ext)s'
    }

    logger.info(f"Downloading {link}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link)
            #ydl.download([link])
            return info['title']
    except Exception as e:
        logger.error(f"Exception while downloading WAV for {link}", exc_info=e)
        logger.error(e)
        exceptions['WAV'].append(link)

    # Download Video
    if download_video is True:
        ydl_video = {
            'format': 'best',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_video) as ydl:
                ydl.download([link])
        except Exception as e:
            logger.error(f"Exception while downloading Video for {link}", exc_info=e)
            logger.error(e)
            exceptions['Video'].append(link)
