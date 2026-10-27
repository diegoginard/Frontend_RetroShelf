function Manufacturer_Name( ioffset )
{
	local name = fe.game_info( Info.Manufacturer, ioffset )
	if(name.len() > 0)
	{
		name = split( name, "(" )[0] // shorten the manufacturer name when one of the followig characters exist
		name = split( name, "[" )[0]
		name = split( name, "/" )[0]
		name = split( name, "," )[0]
		name = split( name, "?" )[0]

		name = strip( name ) // remove white-space-only from the beginning or end of the manufacturer name
	}
	return name
}

if( my_config["enable_gameinfo"] != "No" )
{
	local year = ""
	local title = ""
	local gcount = ""

	// Year
	year = fe.add_text( "[Year]", year_pos[0], year_pos[1], year_pos[2], year_pos[3] )
	year.zorder = 11

	year.align = Align.Left
	year.charsize = font_size
	year.set_rgb( rgb[0], rgb[1], rgb[2] )

	// Title
	if( my_config["enable_game_manu"] == "Title Only" )
		title = fe.add_text( "[Title]", title_pos[0], title_pos[1], title_pos[2], title_pos[3] )
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
		title = fe.add_text( "[!formatted_text]", title_pos[0], title_pos[1], title_pos[2], title_pos[3] )
	}
	
	title.zorder = 11
	title.align = Align.Left
	title.charsize = font_size
	title.set_rgb( rgb[0], rgb[1], rgb[2] )

	if( my_config["enable_gameinfo"] == "Info and Enumerate" )
	{
		// Current game out of total number of games
		gcount = fe.add_text( "Game: [ListEntry]/[ListSize]", gcount_pos[0], gcount_pos[1], gcount_pos[2], gcount_pos[3] )
		gcount.align = Align.Right
		gcount.charsize = font_size
		gcount.set_rgb( rgb[0], rgb[1], rgb[2] )
		gcount.zorder = 11
	}

	if( ShadersAvailable == 1 )
	{
		local shader = fe.add_shader( Shader.Fragment "bloom_shader_text.frag" )
		shader.set_texture_param( "bgl_RenderedTexture" )
		if( year != "" )
			year.shader = shader
		if( title != "" )
			title.shader = shader
		if( gcount != "" )
			gcount.shader = shader
	}

	// random color for info text
	if( my_config["enable_colors"] == "Yes" )
	{
		brightrand <- function() {
			return 255-(rand()/255)
		}

		local red, green, blue

		// Color Transitions
		fe.add_transition_callback( "color_transitions" )
		color_transitions <- function( ttype, var, ttime ) {
			switch ( ttype )
			{
				case Transition.StartLayout:
				case Transition.ToNewSelection:
				red = brightrand()
				green = brightrand()
				blue = brightrand()
				if( gcount != "" )
					gcount.set_rgb( red, green, blue )
				if( year != "" )
					year.set_rgb( red, green, blue )
				if( title != "" )
					title.set_rgb( red, green, blue )
				break
			}
			return false
		}
	}

	// fade in game info if the startup animation is disabled
	if( my_config["enable_ini_anim"] == "No" )
	{
		// year
		local alpha_cfg = {	when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2) }
		animation.add( PropertyAnimation( year, alpha_cfg ) )
		animation.add( PropertyAnimation( title, alpha_cfg ) )

		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
			animation.add( PropertyAnimation( gcount, alpha_cfg ) )
	}

	// animate game info
	if( my_config["enable_ini_anim"] == "Yes" )
	{
		// year
		local move_transition_year = { when = Transition.StartLayout, property = "x", start = flx*-2, end = year_pos[0], time = (ini_anim_time+350) }
		animation.add( PropertyAnimation( year, move_transition_year ) )

		// title
		local move_transition_title = {	when = Transition.StartLayout, property = "x", start = flx*-2, end = title_pos[0], time = (ini_anim_time+350) }
		animation.add( PropertyAnimation( title, move_transition_title ) )

		// game count
		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			local move_transition_title = {	when = Transition.StartLayout, property = "x", start = flx*2, end =  gcount_pos[0], time = (ini_anim_time+350) }
			animation.add( PropertyAnimation( gcount, move_transition_title ) )
		}
	}
}
