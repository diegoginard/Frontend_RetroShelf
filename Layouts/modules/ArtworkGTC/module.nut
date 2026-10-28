////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// ArtworkGTC class v1.1
// By Yaron
//
// Shaders by pcca-matrix, liquid8d
////////////////////////////////////////////////////////////////////////////////////////////////////////////


class ArtworkGTC
{
	// class variables

	img = null
	img_clone = null

	do_once = true
	can_start = false

	fade_in = false
	fade_in_out = false
	reverse_fade = false
	fade_speed = 1
	fade_ini = false
	rotate = false
	hover = false
	hover_sideways = false
	hover_tilt = false
	conveyor = false
	pulse = false
	rock = false
	enable_shader = false
	pulse_zoom = false
	zoom = false

	move_to_x = null
	move_to_y = null
	move_from_x = null
	move_from_y = null

	move_delay = 0
	_move_delay = 0
	pulse_delay = 0
	_pulse_delay = 0
	fade_delay = 0
	_fade_delay = 0
	zoom_delay = 0
	_zoom_delay = 0
	pulse_zoom_delay = 0
	_pulse_zoom_delay = 0
	rotate_delay = 0
	_rotate_delay = 0
	rock_delay = 0
	_rock_delay = 0
	hover_delay = 0
	_hover_delay = 0

	new_speed = 0
	enable_delay = true
	tween = ""
	easing = ""
	tail = 0
	start_to_y = true
	start_to_x = true
	set_speed_once = true
	from_speed = 1
	to_speed = 1
	rotation_speed = 1
	pulse_zoom_speed = 1000
	pulse_zoom_scale = 1.1
	pulse_zoom_loop = -1  // loop by default

	hover_speed = 5000
	hover_from_x = 0
	hover_from_y = 0
	hover_to_x = 0
	hover_to_y = 0
	hover_switch_sides = 0

	s_p = 0.0
	shader = ""
	shader_name = ""
	shader_ini = false

	pulse_value = 0.0
	pulse_freq = 0.33 // times per second
	pulse_scale = 0.3

	rock_delay_time = 0
	rock_speed = 500
	rock_counter = 0
	rock_loop = -1  // loop by default

	mass_rotation = 0.2
	time_rotation = 3000.0
	original_width = 0
	original_height = 0
	pulse_zoom_counter = 0
	rotate_counter = 0
	rotate_loop = -1  // loop by default
	rotate_direction = "right"
	rock_switch_sides = false
	pulse_zoom_switch = false

	zoom_speed = 1000
	from_scale = 0
	to_scale = 1.0
	mass = 0.0

	constructor( _img )
	{
		img = _img
		img.mipmap = true
		img.x += img.width * 0.5
		img.y += img.height * 0.5
		img.origin_x = img.width * 0.5
		img.origin_y = img.height * 0.5

		img_clone = fe.add_clone( img )
		img_clone.visible = false

		img = Inertia( img, 1000, "x", "y", "width", "height", "rotation", "alpha" )

		fe.add_ticks_callback( this, "tick_ArtworkGTC" )
		fe.add_transition_callback( this, "transitions_ArtworkGTC" )
	}


	// -- internal functions --
	function random_num(minNum, maxNum)
	{
		return floor(((rand() % 10000 ) / 10000.0) * (maxNum - (minNum - 1)) + minNum)
	}

	function set_tween()
	{
		switch( tween )
		{
			case "Inertia":
				img.tween = Tween.Inertia
			break
			case "Linear":
				img.tween = Tween.Linear
			break
			case "Quad":
				img.tween = Tween.Quad
			break
			case "Cubic":
				img.tween = Tween.Cubic
			break
			case "Quart":
				img.tween = Tween.Quart
			break
			case "Quint":
				img.tween = Tween.Quint
			break
			case "Exp":
				img.tween = Tween.Expo
			break
			case "Back":
				img.tween = Tween.Back
			break
			case "QuartSine":
				img.tween = Tween.QuartSine
			break
			case "HalfSine":
				img.tween = Tween.HalfSine
			break
			case "FullSine":
				img.tween = Tween.FullSine
			break
			case "Circle":
				img.tween = Tween.Circle
			break
			case "Bounce":
				img.tween = Tween.Bounce
			break
			case "Elastic":
				img.tween = Tween.Elastic
			break
			default:
				// we set 'img.tween_x/y = Tween.Inertia' in reset_art.nut
			break
		}
	}

	function set_easing()
	{
		switch( easing )
		{
			case "Out":
				img.easing = Easing.Out
			break
			case "In":
				img.easing = Easing.In
			break
			case "OutIn":
				img.easing = Easing.OutIn
			break
			case "InOut":
				img.easing = Easing.InOut
			break
			default:
				// we set 'img.easing_x/y = Easing.Out' in reset_art.nut
			break
		}
	}

	function set_mass()
	{
		if( mass < 0.0 )
		{
			img.mass = 0.0
			return
		}
		if( mass > 1.0 )
		{
			img.mass = 1.0
			return
		}
		
		img.mass = mass
	}

	function art_pulse()
	{
		img_clone.zorder = img.zorder
		img_clone.visible = true
		pulse_value += pulse_freq / ScreenRefreshRate
		if( pulse_value > 1.0 ) pulse_value = 0.0

		img_clone.x = img.x
		img_clone.y = img.y
		img_clone.width = img.width * ( 1.0 + pulse_value * pulse_scale )
		img_clone.height = img.height * ( 1.0 + pulse_value * pulse_scale )
		img_clone.rotation = img.rotation
		img_clone.origin_x = img.origin_x + img.width * pulse_value * pulse_scale / 2
		img_clone.origin_y = img.origin_y + img.height * pulse_value * pulse_scale / 2
		img_clone.alpha = 150 * ( 1.0 - pulse_value )
	}

	function art_fade_in()
	{
		if( !fade_ini )
		{
			img.alpha = 0
			fade_ini = true
		}

		if( img.alpha < 255 )
		{
			if( img.alpha + fade_speed > 255 )
				img.alpha = 255
			else
				img.alpha += fade_speed
		}
	}

	function art_fade_in_out()
	{
		if( img.alpha < 255 && reverse_fade )
		{
			if( img.alpha + fade_speed > 255 )
				img.alpha = 255
			else
				img.alpha += fade_speed
		}
		else
		{
			if( img.alpha - fade_speed < 0 )
				img.alpha = 0
			else
				img.alpha -= fade_speed
		}

		if( img.alpha == 0 )
			reverse_fade = true
		if( img.alpha == 255 )
			reverse_fade = false

		return
	}

	function greyscale()
	{
		shader = fe.add_shader( Shader.Fragment, FeConfigDirectory + "gtc-common/shaders/greyscale.frag" )
		img.shader = shader
	}

	function greyscale_vector()
	{
		shader = fe.add_shader( Shader.Fragment, FeConfigDirectory + "gtc-common/shaders/greyscale_vector.frag" )
		img.shader = shader
	}

	function ripple_shader()
	{
		shader = fe.add_shader( Shader.Fragment, FeConfigDirectory + "gtc-common/shaders/ripple.frag" )
		shader.set_texture_param("texture")
		img.shader = shader
	}

	function artwork_shaders( idx )
	{
		shader = fe.add_shader( Shader.Fragment, FeConfigDirectory + "gtc-common/shaders/artworks.frag" )
		img.shader = shader
		img.shader.set_texture_param( "Tex0" )
		img.shader.set_param( "datas", idx,0,0,0 )
		img.shader.set_param( "alpha", 1.0 )
	}

	function random_shader()
	{
		return r_shader[random_num(1, 5)]
	}
	// ---------------------------------------------------------------------------------------------------------------------


	// -- services exposed to the user (true / false) --
	function tick_ArtworkGTC( ttime )
	{
		// delay timer
		if( enable_delay )
		{
			if( move_delay > 0 )
				_move_delay = ttime + move_delay

			if( pulse_delay > 0 )
				_pulse_delay = ttime + pulse_delay

			if( fade_delay > 0 )
				_fade_delay = ttime + fade_delay

			if( zoom_delay > 0 )
				_zoom_delay = ttime + zoom_delay

			if( pulse_zoom_delay > 0 )
				_pulse_zoom_delay = ttime + pulse_zoom_delay

			if( rotate_delay > 0 )
				_rotate_delay = ttime + rotate_delay

			if( rock_delay > 0 )
				_rock_delay = ttime + rock_delay

			if( hover_delay > 0 )
				_hover_delay = ttime + hover_delay

			enable_delay = false
		}

		if( move_from_x != null )
		{
			img.from_x = move_from_x
		}

		if( move_from_y != null )
		{
			img.from_y = move_from_y
		}

		if( move_to_x != null )
		{
			if( _move_delay < ttime && start_to_x )
			{
				img.to_x = move_to_x
				start_to_x = false
			}
		}

		if( move_to_y != null )
		{
			if( _move_delay < ttime && start_to_y )
			{
				img.to_y = move_to_y
				start_to_y = false
			}
		}

		if( pulse )
		{
			if( _pulse_delay < ttime )
				art_pulse()
		}

		if( fade_in )
		{
			if( _fade_delay < ttime )
				art_fade_in()
		}

		if( fade_in_out )
		{
			if( _fade_delay < ttime )
				art_fade_in_out()
		}

		if( zoom )
		{
			if( _zoom_delay < ttime )
			{
				if( !img.running )
					can_start = true

				if( can_start && do_once )
				{
					set_tween()
					set_easing()
					set_mass()
					
					img.time = zoom_speed
					img.x += img.width * 0.5
					img.y += img.height * 0.5
					img.to_width = original_width * to_scale
					img.to_height = original_height * to_scale

					do_once = false
				}
			}
		}

		if( pulse_zoom )
		{
			if( _pulse_zoom_delay < ttime )
			{
				// idiot proofing
				if( pulse_zoom_loop == 0 )
					pulse_zoom = false

				if( !img.running )
					can_start = true

				if( can_start && do_once )
				{
					//set_tween()
					set_easing()
					set_mass()
					//img.time = pulse_zoom_speed

					do_once = false
				}

				if( can_start )
				{
					if( !img.running && pulse_zoom_counter != pulse_zoom_loop )
					{
						if( !pulse_zoom_switch )
						{
							// increase size
							img.time = pulse_zoom_speed
							set_tween()
							img.to_width = original_width * pulse_zoom_scale
							img.to_height = original_height * pulse_zoom_scale
							
							pulse_zoom_switch = true
						}
						else
						{
							// decrease size
							img.time = pulse_zoom_speed
							img.tween = Tween.Inertia
							img.to_width = original_width
							img.to_height = original_height

							pulse_zoom_switch = false
							pulse_zoom_counter++
						}
					}
				}
			}
		}

		if( rotate )
		{
			if( _rotate_delay < ttime )
			{
				// don't begin animation until into-screen animation ends, if one is played
				// img.running returns true if object is still moving
				if( !img.running )
				{
					can_start = true
				}

				if( can_start && do_once  )
				{
					set_tween()
					set_easing()
					set_mass()
					// limit rotation speed to 50
					if( rotation_speed > 50 )
						rotation_speed = 50
					if( rotation_speed < 0 )
						rotation_speed = 1
					do_once = false
				}

				if( can_start )
				{
					if(	rotate_direction == "right" )
						img.rotation += rotation_speed
					else	// left
						img.rotation -= rotation_speed

					if( img.rotation >= 360 || img.rotation <= -360 )
					{
						rotate_counter++
						img.rotation = 0
					}

					if( rotate_counter == rotate_loop )
						rotate = false
				}
			}
		}

		if( rock )
		{
			if( _rock_delay < ttime )
			{
				// don't begin animation until into-screen animation ends, if one is played
				// img.running returns true if object is still moving
				if( !img.running )
				{
					can_start = true
				}

				if( can_start && do_once )
				{
					set_tween()
					set_easing()
					set_mass()
					do_once = false
				}

				if( can_start )
				{
					if( img.rotation == 11 )
						rock_switch_sides = true
					if( img.rotation == -11 )
						rock_switch_sides = false

					if( !rock_switch_sides && rock_delay_time < ttime )
					{
						img.rotation += 1
						if( img.rotation == 11 )
							rock_delay_time = ttime + rock_speed
					}
					if( rock_switch_sides && rock_delay_time < ttime )
					{
						img.rotation -= 1
						if( img.rotation == -11 )
						{
							rock_delay_time = ttime + rock_speed
							rock_counter++
						}
					}
				}

				if( rock_counter == rock_loop && img.rotation == 0 )
					rock = false
			}
		}

		if( hover || hover_sideways || hover_tilt || conveyor )
		{
			if( _hover_delay < ttime )
			{
				// don't begin animation until into-screen animation ends, if one is played
				// img.running returns true if object is still moving
				if( !img.running )
				{
					set_tween()
					set_easing()
					set_mass()
					can_start = true
				}

				if( !img.running_x && can_start )
				{
					// set speed
					if( hover_speed == -1)
					{
						new_speed = random_num(from_speed, to_speed)
						img.time_x = new_speed
						img.time_y = new_speed * 1.5
					}
					else if(set_speed_once)
					{
						img.time_x = hover_speed
						img.time_y = hover_speed * 1.5
						set_speed_once = false
					}

					// update according to type of hovering
					if( hover )
					{
						img.to_x = random_num( hover_from_x, hover_to_x )
						img.to_y = random_num( hover_from_y, hover_to_y )
					}
					else if( hover_sideways )
					{
						if( img.running )  // allow any to-screen animation to end
							img.from_x = hover_from_x
						img.to_x = hover_to_x

						if( !img.running )
						{
							hover_switch_sides = hover_from_x
							hover_from_x = hover_to_x
							hover_to_x = hover_switch_sides
						}
					}
					else if( hover_tilt )
					{
						if( do_once )
						{
							// increase y speed in this case so the waiting is even shorter
							if( hover_speed == -1)
								img.time_y = new_speed * 2.0
							else
								img.time_y = hover_speed * 2.0
							
							img.mass_rotation = mass_rotation
							img.time_rotation = time_rotation
							do_once = false
						}
						img.to_x = random_num( hover_from_x, hover_to_x )
						img.to_y = random_num( hover_from_y, hover_to_y )
						img.to_rotation = ( img.to_x - img.from_x ) * 0.1
					}
					else if( conveyor )
					{
						img.from_x = hover_from_x
						img.to_x = hover_to_x
					}
				}

				if( hover_tilt )
				{
					if ( fabs( img.from_rotation ) > fabs( img.to_rotation / 2.0 ) )
						img.to_rotation = 0.0
				}
			}
		}


		// -- artwork shaders --
		if( enable_shader )
		{
			switch( shader_name )
			{
				case "ripple":
					if( !shader_ini )
					{
						shader_ini = true
						ripple_shader()
					}

					shader.set_param("ttime", ttime)
				break

				case "pixelate":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(1)
					}

					if( s_p < 1.0 )
						s_p += 0.01

					shader.set_param("progress", s_p)
				break

				case "flag":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(2)
					}

					if( s_p < 1.0 )
						s_p += 0.01

					shader.set_param("progress", s_p)
				break

				case "stripes":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(3)
					}

					if( s_p < 1.0 )
						s_p += 0.01

					shader.set_param("progress", s_p)
				break

				case "stripes2":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(4)
					}

					if( s_p < 1.0 )
						s_p += 0.01

					shader.set_param("progress", s_p)
				break

				case "blur":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(5)
					}

					if( s_p < 1.0 )
						s_p += 0.02

					shader.set_param("progress", s_p)
				break

				case "random":
					if( !shader_ini )
					{
						shader_ini = true
						artwork_shaders(random_num(1,5))
					}

					if( s_p < 1.0 )
						s_p += 0.01

					shader.set_param("progress", s_p)
				break

				case "greyscale":
					if( !shader_ini )
					{
						shader_ini = true
						greyscale()
					}
				break

				case "greyscale_vector":
					if( !shader_ini )
					{
						shader_ini = true
						greyscale_vector()
					}
				break

				default:
				break
			}
		}

		return false
	}


	function transitions_ArtworkGTC( ttype, var, ttime )
	{
		if( ttype == Transition.StartLayout )
		{
			shader_ini = false
		}
		
		if( ttype == Transition.EndNavigation )
		{
			can_start = false
			do_once = false
			enable_delay = true
			start_to_x = true
			start_to_y = true
		}
		
		return false
	}
}
