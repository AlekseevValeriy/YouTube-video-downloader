from pydub import AudioSegment
name = 'アイアンメイデン・ジャンク  みつあくま feat 初音ミク (Iron Maiden Junk).webm'
webm_audio = AudioSegment.from_file(name, 'webm')
webm_audio.export(name.split('.')[0] + '.mp3', 'mp3')