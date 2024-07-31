from yt_dlp import YoutubeDL
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal


class YouTube(QObject):
    send_video_name = pyqtSignal(str)
    send_receiv_value = pyqtSignal(int)
    send_formats = pyqtSignal(dict, dict)

    def __init__(self) -> None:
        super().__init__()
        self.path_save = ''
        self.ydl_options = {
            # 'format': '248+140',
            # 'format': 'best',
            # 'format': 'bestvideo+bestaudio/best',
            'outtmpl': self.path_save + '/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress],
        }
        
        self.list_format_video = ["2160p60", "2160p", "1440p60", "1440p", "1080p60", "1080p", "720p60", "720p", "480p", "360p"]
        self.dict_format_video = {format: {} for format in self.list_format_video}
        self.type_file_video = ['webm', 'mp4']

        self.list_format_audio = ["high", "medium", "low"]
        self.dict_format_audio = {format: {} for format in self.list_format_audio}
        self.type_file_audio = ['webm', 'mp4', 'm4a']

    def set_patch(self, path_save):
        self.path_save = path_save

    def info_video(self, video_url):
        with YoutubeDL(self.ydl_options) as ydl:
            result = ydl.extract_info(video_url, download=False)

            if 'entries' in result:
                video = result['entries'][0]
            else:
                video = result

            video_title = video['title']
            self.send_video_name.emit(video_title)
            #########################################

            available_formats = self.get_all_available_formats(result)
            for item in available_formats:
                print(item)
                self.add_format(item, self.list_format_video, self.type_file_video, self.dict_format_video)
                # Обертка для аудио форматов
                self.add_format(item, self.list_format_audio, self.type_file_audio, self.dict_format_audio)

            self.send_formats.emit(self.dict_format_video, self.dict_format_audio)
            print(self.dict_format_video)
            print(self.dict_format_audio)
            
    
     # Универсальная функция для добавления форматов
    def add_format(self, item, format_list, type_list, format_dict):
        for format in format_list:
            for file_type in type_list:
                if format == item[3] and item[1] == file_type:
                    if file_type not in format_dict[format]:
                        format_dict[format][file_type] = item[0]
    
     # получаем список всех доступных форматов
    def get_all_available_formats(self, response):
        formats = response.get('formats', [])
        available_formats = [
            [f.get('format_id'), f.get('ext'), f.get('resolution', 'audio only'), f.get('format_note')]
            for f in formats if f.get('format_id') and f.get('ext') and f.get('format_note')
        ]
        reverse_list = available_formats[::-1]
        # print('reverse_list', reverse_list)
        return reverse_list

    def download(self, video_url, yt_format_video_id, yt_format_audio_id):
        self.ydl_options['format'] = f'{yt_format_video_id}+{yt_format_audio_id}'
        print(self.ydl_options['format'])
        try:
            with YoutubeDL(self.ydl_options) as ydl:
                ydl.extract_info(video_url, download=True)
        except Exception as error:
            print(error)

    def progress(self, percent):
        if percent['status'] == 'downloading':
            result = round(percent['downloaded_bytes'] / percent['total_bytes'] * 100, 1)
            self.send_receiv_value.emit(int(result))
