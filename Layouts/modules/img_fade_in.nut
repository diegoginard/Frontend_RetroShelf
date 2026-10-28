//////////////////////////////////////////////////////////////////////////////////////////////////
// img_fade_in module
//
// By Yaron
//////////////////////////////////////////////////////////////////////////////////////////////////


class img_fade_in
{
	img = null
	speed = 1
	
	constructor( _img, _speed )
	{
		img = _img
		img.alpha = 0
		speed = _speed

		fe.add_ticks_callback( this, "tick_image_fadein" )
	}

	function tick_image_fadein( ttime )
	{
		if( img.alpha < 255 )
		{
			if( img.alpha + speed > 255 )
				img.alpha = 255
			else
				img.alpha += speed
		}
	}
}
