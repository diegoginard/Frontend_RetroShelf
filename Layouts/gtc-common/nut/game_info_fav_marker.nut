if( my_config["enable_favstar"] == "With Game Info" )
{
	local favourite_marker = fe.add_image( "[!FavStar]", fav_x, fav_y, fav_wh, fav_wh )
	favourite_marker.mipmap = true
	favourite_marker.zorder = 11

	if( my_config["enable_ini_anim"] == "No" )
	{
		// fade in if startup animation is set to No
		local alpha_cfg = {	when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2) }
		animation.add( PropertyAnimation( favourite_marker, alpha_cfg ) )
	}
	else
	{
		// animate with game info
		local move_transition_year = { when = Transition.StartLayout, property = "x", start = flx*-2, end = fav_x, time = (ini_anim_time+350) }
		animation.add( PropertyAnimation( favourite_marker, move_transition_year ) )
	}
}
