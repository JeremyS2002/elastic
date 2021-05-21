curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_active_2.mp3?id=297 --output audio/target_acquired.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_disabled_4.mp3?id=324 --output audio/shutting_down.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_autosearch_5.mp3?id=308 --output audio/is_anyone_there.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_search_1.mp3?id=347 --output audio/are_you_still_there.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_deploy_5.mp3?id=319 --output audio/there_you_are.mp3
youtube-dl https://www.youtube.com/watch?v=6aUniexlTBo
ffmpeg -i 'Portal Turret -I See You-6aUniexlTBo.mp4' -vn audio/i_see_you.mp3
rm 'Portal Turret -I See You-6aUniexlTBo.mp4'
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_search_4.mp3?id=350 --output audio/searching.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_autosearch_4.mp3?id=307 --output audio/sentry_mode_activated.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_retire_7.mp3?id=346 --output audio/nap_time.mp3
curl http://cdn.frustra.org/sounds/sound_portal1/npc/turret_floor/turret_active_5.mp3?id=300 --output audio/hello_friend.mp3
curl http://cdn.frustra.org/sounds/sound/npc/turret_floor/turret_deploy_6.mp3?id=2613 --output audio/whos_there.mp3

curl https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml --output haarcascade_frontalface_default.xml