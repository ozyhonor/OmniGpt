from moviepy.editor import TextClip

print(TextClip.list("font"))


from moviepy.editor import TextClip

# Create a TextClip with the default font
text_clip = TextClip("Hello World!", fontsize=36, color="white", font="fonts/Netflix-(Graphique-Pro).ttf").set_duration(2)
text_clip.write_videofile('Goood.mp4')