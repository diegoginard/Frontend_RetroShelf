if( my_config["enable_frame"] == "Yes" )
{
	local frame = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/frame.png", 0, fly*0.94, flw, flh*0.06 )
	frame.zorder = 11

	if( my_config["enable_ini_anim"] == "Yes" )
	{
		local start_transition1 = { when = Transition.StartLayout, property = "y", start = fly*2, end = fly*0.94, time = ini_anim_time }
		animation.add( PropertyAnimation( frame, start_transition1 ) )
	}
}
