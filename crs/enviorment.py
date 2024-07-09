output_folder = r'../videos'
ydl_opts = {
    'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
    'quiet': True,
    'nopart': False,

}
