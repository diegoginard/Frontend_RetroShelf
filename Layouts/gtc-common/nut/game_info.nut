function Manufacturer_Name( ioffset )
{
	local name = fe.game_info( Info.Manufacturer, ioffset )
	if( name.len() > 0 )
	{
		name = split( name, "(" )[0] // shorten the manufacturer name when one of the followig characters exist
		name = split( name, "[" )[0]
		name = split( name, "/" )[0]
		name = split( name, "," )[0]
		name = split( name, "?" )[0]

		name = strip( name )  // remove white-space-only from the beginning or end of the manufacturer name
	}
	return name
}

if( my_config["enable_gameinfo"] != "No" )
{
	local year = ""
	local year_b = "" //black shadow
	local title = ""
	local title_b = "" //black shadow
	local gcount = ""
	local gcount_b = "" //black shadow


	// Year
	year_b = fe.add_text( "[Year]", year_b_pos[0], year_b_pos[1], year_b_pos[2], year_b_pos[3] )
	year = fe.add_text( "[Year]", year_pos[0], year_pos[1], year_pos[2], year_pos[3] )
	year_b.zorder = 11
	year.zorder = 12

	year_b.align = Align.Left
	year_b.charsize = font_size
	year_b.set_rgb(0, 0, 0)

	year.align = Align.Left
	year.charsize = font_size
	year.set_rgb( rgb[0], rgb[1], rgb[2] )

	// Title
	if( my_config["enable_game_manu"] == "Title Only" )
	{
		title_b = fe.add_text( "[Title]", title_b_pos[0], title_b_pos[1], title_b_pos[2], title_b_pos[3] )
		title = fe.add_text( "[Title]", title_pos[0], title_pos[1], title_pos[2], title_pos[3] )
	}
	else
	{
		formatted_text <- function()
		{
			local m = Manufacturer_Name(0)
			local t = "[Title]"

			if(( m.len() > 0 ) && ( t.len() > 0 ))
				return m + ",  " + t

			return t
		}
		title_b = fe.add_text( "[!formatted_text]", title_b_pos[0], title_b_pos[1], title_b_pos[2], title_b_pos[3] )
		title = fe.add_text( "[!formatted_text]", title_pos[0], title_pos[1], title_pos[2], title_pos[3] )
	}
	title_b.zorder = 11
	title.zorder = 12

	title_b.align = Align.Left
	title_b.charsize = font_size
	title_b.set_rgb( 0, 0, 0 )

	title.align = Align.Left
	title.charsize = font_size
	title.set_rgb( rgb[0], rgb[1], rgb[2] )

	// enumerate game list
	if( my_config["enable_gameinfo"] == "Info and Enumerate" )
	{
		// Current game out of total number of games
		gcount_b = fe.add_text( "Game: [ListEntry]/[ListSize]", gcount_b_pos[0], gcount_b_pos[1], gcount_b_pos[2], gcount_b_pos[3] )
		gcount = fe.add_text( "Game: [ListEntry]/[ListSize]", gcount_pos[0], gcount_pos[1], gcount_pos[2], gcount_pos[3] )
		gcount_b.zorder = 11
		gcount.zorder = 12

		gcount_b.align = Align.Right
		gcount_b.charsize = font_size
		gcount_b.set_rgb( 0, 0, 0 )

		gcount.align = Align.Right
		gcount.charsize = font_size
		gcount.set_rgb( rgb[0], rgb[1], rgb[2] )
	}

	// Random color for info text
	if( my_config["enable_colors"] == "Yes" )
	{
		brightrand <- function(){
			return 255-(rand()/255)
		}

		local red, green, blue

		// Color Transitions
		fe.add_transition_callback( "color_transitions" )
		color_transitions <- function( ttype, var, ttime ) {
			switch( ttype )
			{
				case Transition.StartLayout:
				case Transition.ToNewSelection:
					red = brightrand()
					green = brightrand()
					blue = brightrand()
					if( year != "" )
						year.set_rgb( red, green, blue )
					if( title != "" )
						title.set_rgb( red, green, blue )
					if( gcount != "" )
						gcount.set_rgb( red, green, blue )
				break
			}
			return false
		}
	}

	// animate game info
	if( my_config["enable_ini_anim"] == "Yes" )
	{
		// animate year
		local move_transition_year_b = {when = Transition.StartLayout,	property = "x",	start = flx*-2,	end = year_b_pos[0], time = ini_anim_time+350}
		animation.add( PropertyAnimation( year_b, move_transition_year_b ) )

		local move_transition_year = {when = Transition.StartLayout, property = "x", start = flx*-2, end = year_pos[0], time = ini_anim_time+350}
		animation.add( PropertyAnimation( year, move_transition_year ) )

		// animate title
		local move_transition_title_b = {when = Transition.StartLayout,	property = "x",	start = flx*-2, end = title_b_pos[0], time = ini_anim_time+350}
		animation.add( PropertyAnimation( title_b, move_transition_title_b ) )

		local move_transition_title = {when = Transition.StartLayout, property = "x", start = flx*-2, end = title_pos[0], time = ini_anim_time+350}
		animation.add( PropertyAnimation( title, move_transition_title ) )

		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			// animate gcount
			local move_transition_title_b = {when = Transition.StartLayout,	property = "x",	start = flx*2, end = gcount_b_pos[0], time = ini_anim_time+350}
			animation.add( PropertyAnimation( gcount_b, move_transition_title_b ) )

			local move_transition_title = {when = Transition.StartLayout, property = "x", start = flx*2, end = gcount_pos[0], time = ini_anim_time+350}
			animation.add( PropertyAnimation( gcount, move_transition_title ) )
		}
	}
	else
	{
		// fade in year
		local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
		animation.add( PropertyAnimation( year_b, alpha_cfg ) )

		alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
		animation.add( PropertyAnimation( year, alpha_cfg ) )

		// fade in title
		alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
		animation.add( PropertyAnimation( title_b, alpha_cfg ) )

		alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
		animation.add( PropertyAnimation( title, alpha_cfg ) )

		// fade in gcount
		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			// animate title
			alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
			animation.add( PropertyAnimation( gcount_b, alpha_cfg ) )

			alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*1.5}
			animation.add( PropertyAnimation( gcount, alpha_cfg ) )
		}
	}
}
