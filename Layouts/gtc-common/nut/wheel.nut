// Code by Yaron
// Wheel and Inertia modules by Oomek 
//////////////////////////////////////////////////////////////////////////////////////////////////



// wheel and pointer speed
local wheel_speed = my_config["transition_ms"].tointeger()

// number of wheel slots, + 2 to compensate for two off screen slots
local wheel_slots = my_config["wheel_slots"].tointeger() + 2



//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel background

local wheel_bg
local wheel_bg_alpha = 0

if( my_config["enable_wl_bg"] != "No" )
{
	local x = flx*0.72

	if( my_config["wheel_poisition"] == "Adjust Left" )
		x = flx*0.67

	if( my_config["wheel_type"] == "Round" )
		wheel_bg = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/wheel_art.png", x, 0, flw*0.36, flh )
	else
		wheel_bg = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/wheel_vert.png", x, 0, flw*0.22, flh )

	if( my_config["enable_wl_bg"] == "Light" )
		wheel_bg_alpha = 80
	else if( my_config["enable_wl_bg"] == "Medium" )
		wheel_bg_alpha = 160
	else if( my_config["enable_wl_bg"] == "Dark" )
		wheel_bg_alpha = 255

	wheel_bg.alpha = wheel_bg_alpha
}



//////////////////////////////////////////////////////////////////////////////////////////////////
// Pointer

local pointer
if( my_config["enable_pointer"] == "Yes" )
{
	local start_x = 0.91

	pointer = fe.add_image( "default.png", flx*start_x, fly*0.325, flw*0.2, flh*0.35 )
	pointer.preserve_aspect_ratio = true

	// for best results keep inertia value same as wheel speed
	pointer = Inertia( pointer, wheel_speed, "x", "y" )

	fe.add_transition_callback( "transition_pointer" )
	transition_pointer <- function( ttype, var, ttime )
	{
		switch( ttype )
		{
			case Transition.ToNewSelection:
				pointer.to_x = flx*0.889
			break
			case Transition.EndNavigation:
				pointer.to_x = flx*start_x
			break
		}

		return false
	}
}



//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel

// wheel configuration
local wheel_config =
{
    function init()
    {
        // Wheel global parameters
		if( my_config["wheel_poisition"] == "Adjust Right" )
			x <- flw * 0.83
		else  // adjust left
			x <- flw * 0.78

        y <- flh * 0.5
        width <- flw
        height <- flh
        slots <- wheel_slots
        speed <- wheel_speed

        artwork_label <- "wheel"
        video_flags <- Vid.ImagesOnly
		if( my_config["wheel_logo_aspect"] == "Yes" )
			preserve_aspect_ratio <- true
		else
			preserve_aspect_ratio <- false

        zorder <- 1
        trigger <- Transition.ToNewSelection

        preset <- "arch-vertical"

        // Arch preset parameters
		if( my_config["wheel_type"] == "Round" )
			arch <- 85.0
		else
			arch <- 0.0

        // Dynamic table override defines to be updated in update()
        layout.width <- []
        layout.height <- []
    }

    function update()
    {
        for( local i = 0; i < slots; i++ )
        {
			layout.width[i] = flh * 0.3
			layout.height[i] = flh * 0.3 / 2.5
        }

		// current slot
		layout.width[slots/2] = flh * 0.45
		layout.height[slots/2] = flh * 0.45 / 2.5
    }
}

// create wheel
local wheel = fe.add_wheel( wheel_config )


// Favourite games marker
local favourite_marker
if( my_config["enable_favstar"] == "Left of Wheel" || my_config["enable_favstar"] == "Right of Wheel" )
{
	favourite_marker = fe.add_image( "[!FavStar]", wheel.x - (flw*0.176), wheel.y - (flh*0.026), flw*0.03, flw*0.03 )
	favourite_marker.zorder = 10
	favourite_marker.mipmap = true

	if( my_config["enable_favstar"] == "Right of Wheel" )
		favourite_marker.x = wheel.x + (flw*0.133)

	// compensate for wheel inertia delay
	fe.add_ticks_callback( "ticks_fav_wheel" )
	ticks_fav_wheel <- function( ttime )
	{
		if( wheel.velocity.get < 0.25 && wheel.velocity.get > -0.25 )
			favourite_marker.visible = true
		else
			favourite_marker.visible = false
	}
}


//Wheel fading code starts here
local _alpha, _partially = 30

if( my_config["wheel_fadeout"] != "No" )
{
	first_tick <- 0
	stop_fading <- true
	wheel_fade_ms <- my_config["wheel_fade_ms"].tointeger()

	if( wheel_fade_ms > 0 )
	{
		fe.add_transition_callback( "transition_wheel_fade" )
		transition_wheel_fade <- function( ttype, var, ttime )
		{
			if( ttype == Transition.ToNewSelection || ttype == Transition.ToNewList )
			{
				first_tick = -1
				wheel_delay = fe.layout.time
				if( my_config["enable_pointer"] != "No" )
					pointer.alpha = 255
				if( my_config["enable_wl_bg"] != "No" )
					wheel_bg.alpha = wheel_bg_alpha
			}

			return false
		}

		fe.add_ticks_callback( "ticks_wheel_alpha" )
		ticks_wheel_alpha <- function( ttime )
		{
			local _elpased = 0
			if( first_tick == -1 )
				stop_fading = false

			// handle wheel alpha after keyboard search
			if( first_tick > 0 )
				_elpased = ttime - first_tick

			if( _elpased < wheel_fade_ms )
			{
				wheel.alpha = 255
				if( my_config["enable_favstar"] == "Left of Wheel" || my_config["enable_favstar"] == "Right of Wheel" )
					favourite_marker.alpha = 255
			}


			// Wheel fading
			if( !stop_fading && ttime - wheel_delay >= wheel_play )
			{
				local elapsed = 0

				if( first_tick > 0 )
					elapsed = ttime - first_tick

				if( elapsed > wheel_fade_ms )
				{
					if( my_config["wheel_fadeout"] == "Partially" )
						wheel.alpha = _partially
					else
						wheel.alpha = 0
				}
				else
				{
					_alpha = (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms
					if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
						_alpha = _partially

					wheel.alpha = _alpha

					if( my_config["enable_pointer"] != "No" )
						pointer.alpha = _alpha

					if( my_config["enable_favstar"] == "Left of Wheel" || my_config["enable_favstar"] == "Right of Wheel" )
						favourite_marker.alpha = _alpha

					if( my_config["enable_wl_bg"] != "No" )
					{
						_alpha = (wheel_bg_alpha * (wheel_fade_ms - elapsed)) / wheel_fade_ms
						if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
							_alpha = _partially
						wheel_bg.alpha = _alpha
					}
				}

				if( elapsed > wheel_fade_ms )
				{
					//So we don't keep doing the loop above when all values have 0 alpha
					stop_fading = true
				}

				if( first_tick == -1 )
					first_tick = ttime
			}
		}
	}
}

// pulse current wheel logo
if( my_config["wheel_pulse"] != "No" )
{
	local pulse_once = false

	local pulse_slot = fe.add_clone( wheel.sel_slot )
	pulse_slot.zorder = wheel.cfg.zorder + wheel.selected_slot_idx - 2

	local pulse = 0.0
	local pulse_freq = 0.33 // times per second
	local pulse_scale = 0.3

	 // no need for animation, just drop it in tick
	update_pulse <- function()
	{
		if( pulse_once )
			return

		if( !wheel.velocity.running )
			pulse += pulse_freq / ScreenRefreshRate
		else
			pulse = 0.0

		if( pulse > 1.0 ) pulse = 0.0

		local sel = wheel.sel_slot
		pulse_slot.x = sel.x
		pulse_slot.y = sel.y
		pulse_slot.width = sel.width * ( 1.0 + pulse * pulse_scale )
		pulse_slot.height = sel.height * ( 1.0 + pulse * pulse_scale )
		pulse_slot.rotation = sel.rotation
		pulse_slot.origin_x = sel.origin_x + sel.width * pulse * pulse_scale / 2
		pulse_slot.origin_y = sel.origin_y + sel.height * pulse * pulse_scale / 2
		pulse_slot.alpha = 150 * ( 1.0 - pulse )

		if(( pulse_slot.alpha == 1 && my_config["wheel_pulse"] == "Once" ) || ( pulse_slot.alpha == 1 && my_config["wheel_fadeout"] != "No" ))
			pulse_once = true
	}

	fe.add_ticks_callback( "tick_pulse" )
	tick_pulse <- function( ttime )
	{
		update_pulse()
	}

	fe.add_transition_callback( "transition_pulse" )
	transition_pulse <- function( ttype, var, ttime )
	{
		if( ttype == Transition.ToNewSelection || ttype == Transition.ToNewList )
		{
			pulse = 0.0
			pulse_once = false
		}

		return false
	}
}



//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel navigation sounds

local sound_name = ""
local nav_sound = []
sid <- 0

for( local i = 0; i < 10; i++ )
	nav_sound.push( fe.add_sound(sound_name) )

fe.add_transition_callback( "nav_sound_transitions" )
function nav_sound_transitions( ttype, var, ttime )
{
	if( my_config["enable_nav_sound"] != "No" )
	{
		switch( my_config["enable_nav_sound"] )
		{
			case "Random":
				sound_name = FeConfigDirectory+"gtc-common/sounds/GS"+random(1, 322)+".mp3"
			break

			case "Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/click.mp3"
			break

			case "Arcade Joystick":
				sound_name = FeConfigDirectory+"gtc-common/sounds/joystick.mp3"
			break

			case "Mouse Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/Mouse_click.mp3"
			break

			case "Amstrad Key":
				sound_name = FeConfigDirectory+"gtc-common/sounds/amstrad_keyboard.mp3"
			break

			case "Apple2 Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/apple2_keyboard.mp3"
			break

			case "Atari Key Beep":
				sound_name = FeConfigDirectory+"gtc-common/sounds/atari_key_beep.mp3"
			break

			case "Atari Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/atari_keyboard.mp3"
			break

			case "C64 Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/c64_key.mp3"
			break

			case "VIC-20 Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/vic20_key.mp3"
			break

			case "PC Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/pc_kb.mp3"
			break

			case "XBox Select":
				sound_name = FeConfigDirectory+"gtc-common/sounds/xbox_select.mp3"
			break

			case "Xbox360 Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/Xbox360_select.mp3"
			break

			case "Wii Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/wii_click.mp3"
			break

			case "Sharp Keyboard":
				sound_name = FeConfigDirectory+"gtc-common/sounds/sharp_keyboard.mp3"
			break

			case "PS2 Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/ps2_click.mp3"
			break

			case "PS3 Click":
				sound_name = FeConfigDirectory+"gtc-common/sounds/ps3_click.mp3"
			break
		}

		switch( ttype )
		{
			case Transition.StartLayout:
			case Transition.EndNavigation:
				sid++
				if( sid > 9 )  // if reached end of the array go to the beginning
					sid = 0
				nav_sound[sid].file_name = sound_name
				nav_sound[sid].playing = true
			break
		}
	}

	return false
}
