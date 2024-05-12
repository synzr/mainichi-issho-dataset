MAINICHI_ISSHO_EPISODE_PLAYLIST="https://www.youtube.com/playlist?list=PLxo_hu9V0ASJmpY5Br7Ntpog26Bd9m2eU"

yt-dlp \
    -S "res:360,ext:mp4:m4a" \
    -o "./episodes/%(title)s.%(ext)s" \
    $MAINICHI_ISSHO_EPISODE_PLAYLIST
