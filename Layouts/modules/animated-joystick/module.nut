/*
================================================================================

Attract-Mode Frontend - animated-joystick module v1.1
Modern version of the Hyperspin's joystick icon

by Oomek - Radek Dutkiewicz 2021
customized by Yaron
https://github.com/oomek/attract-extra

================================================================================

INITIALIZATION:
--------------------------------------------------------------------------------

local joy = AnimatedJoystick( color, direction )



FUNCTION ARGUMENTS:
--------------------------------------------------------------------------------

color - "red" , "blue"

direction - see PROPERTIES



OBJECT PROPERTIES: ( examples for "x" property )
--------------------------------------------------------------------------------

x, y - Joystick's coordinates, origin is at the base of the stick.

width - the width of the joystick

stick_scale - scale of the stick's height, default is 1.0

time - how fast the stick is moving, in milliseconds

angle - how much it should move in degrees, default 20

direction - animation direction, can be one of the following:

AnimatedJoystickDirection.Neutral
AnimatedJoystickDirection.Up
AnimatedJoystickDirection.Down
AnimatedJoystickDirection.Left
AnimatedJoystickDirection.Right



EXAMPLES:
--------------------------------------------------------------------------------

fe.load_module("animated-joystick")

local joy = AnimatedJoystick( "red", AnimatedJoystickDirection.Left )
joy.width = 200
joy.x = 500
joy.y = 800

// you can change the direction in transitions
joy.direction = AnimatedJoystickDirection.Right

================================================================================
*/

AnimatedJoystickDirection <-
{
	Neutral = 0,
	Up      = 1,
	Down    = 2,
	Left    = 3,
	Right   = 4
}

class AnimatedJoystick
{
	static VERSION = 1.00

	x = null
	y = null
	width = null
	stick_scale = null
	perspective = null
	angle = null
	neutral_angle = null
	time = null
	direction = null
	style = "realistic"
	
	_guard = null
	_stick = null
	_guard_mask = null
	_ball = null
	_color = "red"
	_dx = null
	_dy = null
	_timer = null

	static radian = PI / 180.0

	constructor( color, dir )
	{
		_color = color
		_guard = fe.add_image( fe.module_dir + style + "/guard.png" )
		_stick = fe.add_image( fe.module_dir + style + "/stick.png" )
		_guard_mask = fe.add_image( fe.module_dir + style + "/guard-mask.png" )
		_ball = fe.add_image( fe.module_dir + style + "/ball-" + _color + ".png" )

		// zorder added by Yaron
		_guard.zorder = 30
		_stick.zorder = 31
		_guard_mask.zorder = 32
		_ball.zorder = 33
		
		_guard_mask.blend_mode = BlendMode.Premultiplied
		_guard.mipmap = true
		_guard_mask.mipmap = true
		_stick.mipmap = true
		_ball.mipmap = true

		x = fe.layout.width / 2.0
		y = fe.layout.height - fe.layout.height / 14.0
		width = fe.layout.height * 0.075
		stick_scale = 1.0
		perspective = 0.2
		angle = 20
		neutral_angle = 110
		time = 800
		direction = dir
		_dx = 0
		_dy = neutral_angle
		_timer = 0

		fe.add_ticks_callback( this, "joystick_ticks_callback" )
		fe.add_transition_callback( this, "joystick_transition_callback" )
	}

	function joystick_ticks_callback( ttime )
	{
		switch ( direction )
		{
			case AnimatedJoystickDirection.Up:
				_dx = 0.0
				_dy = -angle * 1.75
				break

			case AnimatedJoystickDirection.Down:
				_dx = 0.0
				_dy = angle * 1.75
				break

			case AnimatedJoystickDirection.Left:
				_dx = -angle
				_dy = 0.0
				break

			case AnimatedJoystickDirection.Right:
				_dx = angle
				_dy = 0.0
				break

			case AnimatedJoystickDirection.Neutral:
			default:
				_dx = 0.0
				_dy = 0.0
				break
		}

		_timer += 2000.0 / ScreenRefreshRate / time
		if ( _timer > 2.0 ) _timer = 0.0
		local ds = sin( _timer * PI )
		local dx = ds < 0.0 ? 0.0 : ds * _dx
		local dy = ds < 0.0 ? neutral_angle : neutral_angle + ds * _dy

		_ball.width = _ball.width = width
		_guard.width = _guard.texture_width * _ball.width / _ball.texture_width
		_guard.height = _guard.width * _guard.texture_height / _guard.texture_width

		_stick.width = _stick.texture_width * _ball.width / _ball.texture_width
		_stick.height = _stick.width * _stick.texture_height / _stick.texture_width

		_guard.x = _stick.x = _ball.x = _guard_mask.x = x
		_guard.y = _stick.y = _ball.y = _guard_mask.y = y
		_guard.origin_x = _guard_mask.origin_x = _guard.width / 2.0
		_guard.origin_y = _guard_mask.origin_y = _guard.height / 2.0
		_guard_mask.width = _guard.width
		_guard_mask.height = _guard.height

		local stick_pos = sin( dy * radian )
		local ball_scale = cos( dy * radian )
		ball_scale = 1.0 / ( ball_scale * perspective + 1.0 )

		_ball.width = width * ball_scale
		_ball.height = _ball.width
		_ball.origin_x = _ball.width / 2.0
		_ball.origin_y = _ball.height / 2.0

		_stick.pinch_x = _stick.width * ball_scale * 1.5 - _stick.width * 1.5
		_stick.width = _stick.width + _stick.pinch_x * 2.0
		_stick.origin_x = _stick.width / 2.0
		_stick.origin_y = _stick.height - _stick.height / 16.0

		_stick.subimg_height = (( 1.0 + ball_scale - stick_pos ) * 0.4 + 0.4 ) * _stick.texture_height

		local stick_scaled = _stick.height * stick_pos * ( stick_scale + 0.1 )
		_stick.height = stick_scaled
		_stick.origin_y = stick_scaled - _stick.height / 16.0

		_stick.rotation = dx
		_ball.x = _stick.x + stick_scaled * sin( _stick.rotation * radian )
		_ball.y = _stick.y - stick_scaled * cos( _stick.rotation * radian )
	}
	
	function joystick_transition_callback( ttype, var, ttime )
	{
		if( ttype == Transition.StartLayout )
		{
			_guard.file_name = fe.module_dir + style + "/guard.png"
			_stick.file_name = fe.module_dir +style + "/stick.png"
			_guard_mask.file_name = fe.module_dir + style + "/guard-mask.png"
			_ball.file_name = fe.module_dir + style + "/ball-" + _color + ".png"
		}
	}
}
