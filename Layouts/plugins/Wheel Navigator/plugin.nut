/////////////////////////////////////////////////////////////////
// Wheel Navigator plugin v1.1
//
// Navigate the wheel randomly or forward one game at a time
//
// By Yaron
// 2021
/////////////////////////////////////////////////////////////////


class UserConfig
{
	</ label="Navigation type", help="Navigate the wheel randomly or navigate forward (down), one game at a time", options="Random,Forward", order=1 /> nav_type="Random"
	</ label="Idle for X seconds", help="The amount of time in seconds until navigation begins", order=1 /> idle_time=300
	</ label="Switch game every X seconds", help="After initial Idle time has passed, navigate the wheel every X seconds", order=2 /> switch_time=30
}
local my_config = fe.get_config()


idle_time <- 0
try { idle_time = my_config["idle_time"].tointeger() } catch ( e ) { idle_time = 300 }
if( idle_time < 0 )
	idle_time = 300

idle_time *= 1000  // multiply by 1000 to turn milliseconds into seconds

switch_time <- 0
try { switch_time = my_config["switch_time"].tointeger() } catch ( e ) { switch_time = 30 }
if( switch_time <= 0 )
	switch_time = 30

switch_time *= 1000  // multiply by 1000 to turn milliseconds into seconds
switch_delay <- switch_time


fe.add_ticks_callback( "ticks_timers" )
function ticks_timers( ttime )
{
	if( ttime > switch_time )
	{
		if( !fe.overlay.is_up && !ScreenSaverActive && !IntroActive )
		{
			if( my_config["nav_type"] == "Random" )
				fe.signal( "random_game" )
			else
				fe.list.index++

			switch_time = ttime + switch_delay
		}
	}
}


fe.add_transition_callback(this, "transitions_start_idle")
function transitions_start_idle( ttype, var, ttime )
{
    if( ttype == Transition.ToNewList || ttype == Transition.FromGame )
		switch_time = fe.layout.time + idle_time + switch_delay

    return false
}


fe.add_signal_handler(this, "signal_restart_idle")
function signal_restart_idle(str)
{
	// reset switch_time in case user *manually* navigates wheel
	switch( str )
	{
		case "up":
		case "down":
		case "up":
		case "down":
		case "prev_letter":
		case "next_letter":
			switch_time = fe.layout.time + idle_time + switch_delay
		break
	}

    return false
}
