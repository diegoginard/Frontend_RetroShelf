// Jukebox v1.0
// By Yaron
//////////////////////////////////////////////////////////////////////////////////////////////////



music_file <- ""
song_num <- 0
local list, _loop
local title_visibile = true
local title_anim_speed = 1000
local first_song = true
rnd_new <- 0

sound <- fe.add_sound( "" )
sound.playing = false

music_delay <- 0
try{ music_delay = my_config["set_music_delay"].tointeger() } catch(e) { music_delay = 0 }  // free text used in layout option so use try/catch

// limit music delay time between 0 and 300,000 milliseconds (up to 5 minutes)
if( music_delay < 0 )
	music_delay = 0
if( music_delay > 300000 )
	music_delay = 300000


music_path <- my_config["music_path"]
if( music_path != "" )
{
	if( music_path.len()-1 != '/' && music_path.len()-1 != '\\' )
		music_path += "/"
}
else  // use default path
	music_path = FeConfigDirectory+"gtc-common/music/"


if( my_config["music_play_method"] == "Loop Song" )
	_loop = true
else
	_loop = false


// create music list
if( my_config["enable_ambience"] == "Music" )
{
	// create a list of files in the music folder
	list = zip_get_dir( music_path )
	if( list.len() > 0 )
	{
		if( my_config["music_play_method"] == "Shuffle" )
		{
			if( list.len() > 1 )
			{
				song_num = random( 0, list.len()-1 )
				rnd_new = song_num
			}
			else
				song_num = 0
		}

		music_file = music_path + list[song_num]
	}
}


// song titles
if( my_config["enable_ambience"] == "Music" && my_config["enable_song_title"] == "Yes" )
{
	clean_song_title <- function( ioffset )
	{
		local name = list[song_num]
		if( name.len() > 0 )
		{
			name = split( name, "." )[0] // remove file name extension from song title
			name = strip( name ) // remove white-space-only from the beginning or end of the song title
		}

		return name
	}


	// song title and frame
	local song_title_frame = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/frame.png", 0, flh*-1.2, flw, flh*0.06 )
	song_title_frame.zorder = 1
	song_title_frame = Inertia( song_title_frame, title_anim_speed, "x", "y" )

	song_title.align = Align.MiddleCentre
	song_title.zorder = 2
	song_title = Inertia( song_title, title_anim_speed, "x", "y" )


	// timers
	title_delay <- my_config["song_title_time"].tointeger()
	title_play <- title_delay
	update_time_stitle <- false

	fe.add_signal_handler( "show_song_title" )
	show_song_title <- function( str )
	{
		if( title_visibile == true && !first_song )
		{
			title_visibile = false
			if( list.len() > 0 )
			{
				song_title.msg = clean_song_title(0)

				song_title_frame.y = flh*-1.5
				song_title.y = flh*-1.5

				song_title_frame.to_y = 0
				song_title.to_y = song_title_frame.height / 2.0 - song_title.height / 2.0

				update_time_stitle = true
			}
		}

		return false
	}

	fe.add_ticks_callback( "ticks_show_song_title" )
	ticks_show_song_title <- function( tick_time )
	{
		if( update_time_stitle )
		{
			title_delay = tick_time
			update_time_stitle = false
		}

		if( tick_time - title_play >= title_delay )
		{
			song_title_frame.to_y = flh*-0.5
			song_title.to_y = flh*-0.5
		}
	}
}


fe.add_ticks_callback( "music_tick" )
function music_tick( ttime )
{
	if( my_config["enable_ambience"] == "It's 1983" )
	{
		if( !sound.playing )
		{
			sound.file_name = FeConfigDirectory+"gtc-common/sounds/Arcade_1983.mp3"
			sound.playing = true
		}
	}
	else if( my_config["enable_ambience"] == "It's 1992" )
	{
		if( !sound.playing )
		{
			sound.file_name = FeConfigDirectory+"gtc-common/sounds/Arcade_1992.mp3"
			sound.playing = true
		}
	}
	else if( my_config["enable_ambience"] == "Amiga" )
	{
		if( !sound.playing )
		{
			sound.file_name = FeConfigDirectory+"gtc-common/sounds/amiga_disk_drive.mp3"
			sound.playing = true
		}
	}
	else if( my_config["enable_ambience"] == "Apple II" )
	{
		if( !sound.playing )
		{
			sound.file_name = FeConfigDirectory+"gtc-common/sounds/apple2_boot.mp3"
			sound.playing = true
		}
	}
	else if( my_config["enable_ambience"] == "Vintage PC" )
	{
		if( !sound.playing )
		{
			sound.file_name = FeConfigDirectory+"gtc-common/sounds/System startup long.mp3"
			sound.playing = true
		}
	}

	// delay playing first song for duration decided by the user
	if( my_config["enable_ambience"] == "Music" )
	{
		if( ttime >= music_delay && list.len() > 0 && first_song )
		{
			first_song = false
			sound.file_name = music_file
			sound.playing = true

			if( my_config["enable_song_title"] == "Yes" )
			{
				title_visibile = true
				show_song_title("")
			}
		}
		else if( first_song == false )
		{
			// loop song
			if( ! sound.playing && _loop )
				sound.playing = true

			// loop list or shuffle
			if( ! sound.playing && ! _loop )
			{
				if( my_config["music_play_method"] == "Loop List" )
				{
					song_num++
					if( song_num > list.len()-1 )
						song_num = 0
				}

				if( my_config["music_play_method"] == "Shuffle" )
				{
					// don't repeat same song twice in a row
					if( list.len() > 1 )
					{
						while( song_num == rnd_new )
							rnd_new = random( 0, list.len()-1 )

						song_num = rnd_new
					}
					else
						song_num = 0
				}

				sound.file_name = music_path + list[song_num]
				sound.playing = true

				if( my_config["enable_song_title"] == "Yes" )
				{
					title_visibile = true
					show_song_title("")
				}
			}
		}
	}
}


function music_selection( selection="" )
{
	if( first_song == false )
	{
		if( my_config["music_play_method"] == "Shuffle" )
		{
			if( list.len() > 1 )
			{
				// don't repeat same song twice in a row
				while( song_num == rnd_new )
					rnd_new = random( 0, list.len()-1 )

				song_num = rnd_new
			}
			else
				song_num = 0
		}
		else
		{
			if( selection == "next" )
			{
				song_num++
				if( song_num > list.len()-1 )
					song_num = 0  //go back to first song in list
			}

			if( selection == "prev" )
			{
				song_num--
				if( song_num < 0 )
					song_num = list.len()-1  //go to last song in list
			}
		}

		music_file = music_path + list[song_num]
		sound.playing = false
		sound.file_name = music_file
		sound.playing = true

		if( my_config["enable_song_title"] == "Yes" )
		{
			title_anim_speed = 200
			title_visibile = true
			show_song_title("")
		}
	}
}


// music playback controls
fe.add_signal_handler( this, "music_nav_signal" )
function music_nav_signal( str )
{
	if( my_config["enable_ambience"] == "Music" && list.len() > 0 )
	{
		switch( str )
		{
			case my_config["user_nextsong_key"].tolower():
				music_selection("next")
			break
			case my_config["user_prevsong_key"].tolower():
				music_selection("prev")
			break
		}
	}

	return false
}
