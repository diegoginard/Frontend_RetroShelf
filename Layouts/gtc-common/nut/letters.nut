// Code adapted from the PCCA theme by pcca-matrix


local rtime = 0
local glob_time = 0
local glob_delay = my_config["set_ms_delay"].tointeger()
if( glob_delay > 1000 )
	glob_delay = 1000

local trigger_letter = false

local letters = fe.add_image( "", flw*0.5 - (flw*0.140 * 0.5), flh*0.5 - (flh*0.280 * 0.5), flw*0.140, flh*0.280 )

fe.add_transition_callback( "letters_transition" )
function letters_transition( ttype, var, ttime )
{
	if( ttype == Transition.ToNewList )
		rtime = glob_time
}

fe.add_ticks_callback( "letters_tick" )
function letters_tick( ttime )
{
	glob_time = ttime

	if( glob_time - rtime > glob_delay )
		letters.visible = false   // hide letter search if present

    if( trigger_letter == true )
	{
		local firstl = fe.game_info(Info.Title)
		/*if( fe.filters[fe.list.filter_index].sort_by == Info.Manufacturer )
			firstl = fe.game_info(Info.Manufacturer);*/

		if( my_config["letters_type"] != "No" )
		{
			if( my_config["letters_type"] == "Default" )
				letters.file_name = FeConfigDirectory + "gtc-common/letters/default/" + firstl.slice(0,1).tolower() + ".png"
			else   // by system display name
				letters.file_name = FeConfigDirectory + "gtc-common/letters/" + fe.displays[fe.list.display_index].name + "/" + firstl.slice(0,1).tolower() + ".png"

			letters.visible = true
		}
		trigger_letter = false
    }
}

fe.add_signal_handler(this, "on_signal_letters")
function on_signal_letters(str)
{
	switch( str )
	{
		case "next_letter":
		case "prev_letter":
			rtime = glob_time
			trigger_letter = true
		break
	}

    return false
}
