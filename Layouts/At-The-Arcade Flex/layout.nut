////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
At-The-Arcade Flex layout for Attract-Mode
V1.1
  ______    __            ________ __                        ______                                   __               ________ __                   
 /      \  |  \          |        \  \                      /      \                                 |  \             |        \  \                  
|  ▓▓▓▓▓▓\_| ▓▓_          \▓▓▓▓▓▓▓▓ ▓▓____   ______        |  ▓▓▓▓▓▓\ ______   _______  ______   ____| ▓▓ ______      | ▓▓▓▓▓▓▓▓ ▓▓ ______  __    __ 
| ▓▓__| ▓▓   ▓▓ \  ______   | ▓▓  | ▓▓    \ /      \ ______| ▓▓__| ▓▓/      \ /       \|      \ /      ▓▓/      \     | ▓▓__   | ▓▓/      \|  \  /  \
| ▓▓    ▓▓\▓▓▓▓▓▓ |      \  | ▓▓  | ▓▓▓▓▓▓▓\  ▓▓▓▓▓▓\      \ ▓▓    ▓▓  ▓▓▓▓▓▓\  ▓▓▓▓▓▓▓ \▓▓▓▓▓▓\  ▓▓▓▓▓▓▓  ▓▓▓▓▓▓\    | ▓▓  \  | ▓▓  ▓▓▓▓▓▓\\▓▓\/  ▓▓
| ▓▓▓▓▓▓▓▓ | ▓▓ __ \▓▓▓▓▓▓  | ▓▓  | ▓▓  | ▓▓ ▓▓    ▓▓\▓▓▓▓▓▓ ▓▓▓▓▓▓▓▓ ▓▓   \▓▓ ▓▓      /      ▓▓ ▓▓  | ▓▓ ▓▓    ▓▓    | ▓▓▓▓▓  | ▓▓ ▓▓    ▓▓ >▓▓  ▓▓ 
| ▓▓  | ▓▓ | ▓▓|  \         | ▓▓  | ▓▓  | ▓▓ ▓▓▓▓▓▓▓▓      | ▓▓  | ▓▓ ▓▓     | ▓▓_____|  ▓▓▓▓▓▓▓ ▓▓__| ▓▓ ▓▓▓▓▓▓▓▓    | ▓▓     | ▓▓ ▓▓▓▓▓▓▓▓/  ▓▓▓▓\ 
| ▓▓  | ▓▓  \▓▓  ▓▓         | ▓▓  | ▓▓  | ▓▓\▓▓     \      | ▓▓  | ▓▓ ▓▓      \▓▓     \\▓▓    ▓▓\▓▓    ▓▓\▓▓     \    | ▓▓     | ▓▓\▓▓     \  ▓▓ \▓▓\
 \▓▓   \▓▓   \▓▓▓▓           \▓▓   \▓▓   \▓▓ \▓▓▓▓▓▓▓       \▓▓   \▓▓\▓▓       \▓▓▓▓▓▓▓ \▓▓▓▓▓▓▓ \▓▓▓▓▓▓▓ \▓▓▓▓▓▓▓     \▓▓      \▓▓ \▓▓▓▓▓▓▓\▓▓   \▓▓

Design and Code by tsaylor and Yaron2019 http://forum.attractmode.org/index.php?topic=3979.0
Based on Yaron2019's At-The-Arcade Multi-Cab http://forum.attractmode.org/index.php?topic=3874.0
(with many modifications to support multiple resolutions and pinball cabinets)

Cabinet Art by Gavin Smith of The CoinOps Project
Cabs edited by damonxxx and Yaron2019 http://forum.attractmode.org/index.php?topic=3778.0
Game bezels by The Bezel Project https://github.com/thebezelproject/bezelproject-MAME
CRT screen glow shader by zpaolo11x
Letters and 'System games count' code adapted from pcca theme 
CD Player code by Sony 

Change log:
1.1 Fix potential crashes, auto-rotate snaps for non-fx3 pinball (horizontal/sizeways snaps seem common there)
*/
/////////////////////////////////////////////////////////////////////////////////////////////////////

local orderx = 0;
local divider = "----"

class UserConfig {
	</ label="Enable startup animations", help="Enable system animation when layout starts", 
		options="Yes,No", order=orderx++ /> enable_ini_anim="Yes";
	</ label="Startup animation transition time", 
		help="Startup animation transition time in milliseconds", 
		options="500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000",
		order=orderx++
		/>ini_anim_trans_ms="1000";
	</ label="Select background image", help="Select static, animated or panscan background art", options="Static Arcade,Animated Arcade,Fanart,Flyer,Polygon Trip,Panscan", order=orderx++ /> enable_image="Animated Arcade";   
	</ label="Enable background scanline", help="Show scanline effect on background image", options="No,Light,Medium,Strong", order=orderx++ /> enable_bg_scanline="No";
	</ label="Enable ambience sound", help="Play arcade hall ambience sound or music from the layout's music folder", options="No,It's 1983,It's 1992,Music", order=orderx++ /> enable_ambience="It's 1983";
	</ label="Music folder", 
		help="Path to the music folder, for example: C:\\downloads\\music \n If left empty, music will be played from the default music folder at attract\\layouts\\At-The-Arcade Multi-Cab\\music", 
		options="", order=orderx++ /> music_path="";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx1 = " "

	</ label="Music playing method", help="Loop current song, loop entire song list or shuffle (play random songs)", options="Loop List,Loop Song,Shuffle", 
		order=orderx++ /> music_play_method="Loop List";
	</ label="Previous song key", help="Choose the key to play previous song from the layout music folder", options="Custom1,Custom2,Custom3,Custom4,Custom5,Custom6", order=orderx++ /> user_prevsong_key="Custom4";
	</ label="Next song key", help="Choose the key to play next song from the layout music folder", options="Custom1,Custom2,Custom3,Custom4,Custom5,Custom6", order=orderx++ /> user_nextsong_key="Custom5";
	</ label="Show song title", help="Show the music title - will animate in and out from the top of the screen", options="Yes,No", order=orderx++ /> enable_song_title="Yes";
	</ label="Song title duration", help="The time in milliseconds that the song title will stay on the screen", 
		options="2000,3000,4000,5000,6000,7000,8000", 
		order=orderx++ /> song_title_time="4000";
	</ label="Music delay", help="The time in milliseconds until music starts to play\n Accepts values between 0 and 300,000 (5 minutes)",
		options="", order=orderx++ /> set_music_delay="100";	
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx2 = " "

	</ label="Type of wheel", help="Select round or vertical wheel", options="Round,Vertical", order=orderx++ /> wheel_type="Round";
	</ label="Size of wheel logos", help="Use smaller or larger wheel logos", options="Smaller,Larger", order=orderx++ /> wheel_logo_size="Larger";
	</ label="Preserve wheel logo's aspect ratio", help="Preserve the original aspect ratio of the wheel logos, great for vertical wheel mode", options="Yes,No", order=orderx++ /> wheel_logo_aspect="No";
	</ label="Enable wheel logos mipmap", help="Mipmap reduces aliasing artifacts (jagged edges) for high resolution wheel logos", options="Yes,No", order=orderx++ /> wheel_logo_mipmap="No";
	</ label="Adjust wheel position", help="Adjust wheel position closer to or further from the right side of the screen", options="Adjust Left,Adjust Right", order=orderx++ /> wheel_position="Adjust Left";
	</ label="Enable semitransparent wheel", help="Semitransparent or fully opaque wheel logos", options="Yes,No", order=orderx++ /> wheel_semi_t="No";
	</ label="Number of wheel slots", 
		help="Number of slots in the wheel", 
		options="4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80",
		order=orderx++
		/>wheels="10";
	</ label="Wheel transition time", 
		help="wheel spin tranistion time in milliseconds", 
		options="1,25,50,75,100,125,150,175,200",
		order=orderx++
		/> transition_ms="50";
	</ label="Wheel fade out", help="Fade out wheel after navigation", options="No,Completely,Partially", order=orderx++ /> wheel_fadeout="Completely";
	</ label="Wheel fade out animation time", help="The time (in milliseconds) it takes the wheel to fade", options="500,1000,2000,3000", order=orderx++ /> wheel_fade_ms="500"; 
	</ 	label			= "Delay time",
		help			= "The time (in milliseconds) it takes to start hiding the wheel and pointer",
		options			= "500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000",
		order			= orderx++
	/> 	set_ms_delay	= "1250";	
	</ label="Enable wheel pulse", help="Animate a pulse of the current wheel logo - will pulse only once if wheel fadeout is enabled", options="No,Once,Loop", order=orderx++ /> wheel_pulse="Once";
	</ label="Enable wheel background", help="Show wheel background texture", options="No,Light,Medium,Dark", order=orderx++ /> enable_wl_bg="Light";
	</ label="Wheel background color", help="If showing the wheel background, what color for the shaded background", options="Black,Grey,Blue,Purple,Red,Orange,Green,Yellow", order=orderx++ /> wheel_bg_color="Black";
	</ label="Enable wheel sounds", help="Play sounds when navigating systems wheel", options="No,Random,Click,Arcade Joystick", order=orderx++ /> enable_random_sound="Random"; 
	</ label="Show wheel pointer", help="Show animated pointer", options="Yes,No", order=orderx++ /> enable_pointer="No";
	</ label="Enable Letters", 
		help="Show graphical letters on the screen when pressing the wheel's 'Next Letter' or 'Previous Letter' hotkeys set in the Controls menu.\n 'System Display Name' option will seek the letters in a folder identical to the current system display name (attract/letters/mame for example).", 
		options="No,Default,By System Display Name", order=orderx++ /> letters_type="Default";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx3 = " "

	</ label="Enable game snap aspect ratio", help="Show game snap videos in their original aspect ratio (horizontal or vertical)", options="Yes,No", order=orderx++ /> enable_verticlesnap="No";
	</ label="Enable game snap vertical bezels", help="Show bezels for vertical game snaps, requires 'Enable game snap aspect ratio'", options="No,Bezels with Separators,Bezels without Separators", order=orderx++ /> enable_bezels="No";
	</ label="Enable CRT screen glow shader", 
		help="Enable screen glow effect for the snap video, if user device supports GLSL shaders", 
		options="No,Light,Medium,Strong", order=orderx++ /> enable_crt_screenglow="Medium";
	</ label="Enable CRT bloom or lottes shaders", 
		help="Enable bloom or lottes effects for the snap video, if user device supports GLSL shaders", 
		options="No,CRT Bloom,CRT Lottes", 
		order=orderx++ 
	/> enable_snap_shader="No";
	</ label="Enable CRT scanlines", help="Show CRT scanline effect", options="No,Light,Medium,Dark", order=orderx++ /> enable_crt_scanline="Light";
	</ label="Enable scratches over CRT", help="Show scratches over the CRT for extra authenticity", options="Yes,No", order=orderx++ /> enable_crt_scratches="Yes";
	</ label="Mute game snap videos", help="Mute game snap videos", options="Yes,No", order=orderx++ /> mute_videos="No"; 
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx4= " "

 	</ label="Enable lighted marquee effect", help="Light on or off for the Marquee", options="Yes,No", order=orderx++ /> enable_Lmarquee="Yes";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx5= " "

	</ label="Enable box art", help="Shows the current game box art if available", options="Yes,No", order=orderx++ /> enable_gboxart="No";
	</ label="Enable flyer art", help="Show flyer art - available only when wheel fadeout is set to Partially or Completely", options="Yes,No", order=orderx++ /> enable_gcartart="No";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx6= " "

	</ label="Show game information", help="Show game info", options="No,Info,Info and Enumerate", order=orderx++ /> enable_gameinfo="No";
	</ label="Game name", help="Show game title only or manufacturer and game title. If there is no manufacturer name in the romlist, only the game title will be shown.", 
		options="Title Only,Manufacturer and Title", order=orderx++ /> enable_game_manu="Title Only";
	</ label="Enable random text colors", help="Enable game info random text colors", options="Yes,No", order=orderx++ /> enable_colors="No";
	</ label="Enable text frame", help="Show frame to make game info text standout ", options="Yes,No", order=orderx++ /> enable_frame="No"; 
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx7= " "

	</ label="Mark favourite games", help="Mark favourite games with an icon to the left of the wheel logo or at the bottom with the game info", options="No,Left of Wheel,With Game Info", order=orderx++ /> enable_favstar="Left of Wheel";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx8= " "

	</ label="Search key", help="Choose the key to initiate a search", options="Custom1,Custom2,Custom3,Custom4,Custom5,Custom6", order=orderx++ /> user_search_key="Custom1";
	</ label="Search box size", help="Choose size of the search box", options="Small,Large", order=orderx++ /> user_search_boxsize="Small";
	</ label=divider, help=" ", options = " ", order=orderx++ /> paramxx9 = " "
	
	</ label="Enable key for resolution testing", help="Choose the key to cycle through different aspect ratios for testing purposes", options="None,Custom1,Custom2,Custom3,Custom4,Custom5,Custom6", order=orderx++ /> resolution_test_key="None";
}

/*if( FeVersionNum < 261 ) 
{
	while (!fe.overlay.splash_message( "This theme requires Attract Mode v2.6.1 or higher to work properly. \n You are running "+FeVersion+"\n Press Esc key to exit this message.")) {}
} 
print("AM Version = " + FeVersion + "\n");*/

local my_config = fe.get_config();
fe.layout.font="BigSquareDots";

// modules
fe.load_module("animate");
fe.load_module("fade");
fe.load_module("file");
fe.load_module("file-format");
fe.load_module("conveyor");
fe.load_module("gtc");
fe.load_module("gtc-kb");
fe.load_module("gtc-pas");

// wheel fade delay ini
my_delay <- 0;
try {my_delay = my_config["set_ms_delay"].tointeger();} catch(e) {}
my_play <- my_delay;

local ini_anim_time;
try { ini_anim_time =  my_config["ini_anim_trans_ms"].tointeger(); } catch ( e ) { }

// Letters ini
local rtime = 0;
local glob_time = 0;
local glob_delay;
try { glob_delay =  my_config["set_ms_delay"].tointeger(); } catch ( e ) { }
if( glob_delay > 750 )
	glob_delay = 750;

// Handle aspect ratio, determine width/height...
local aspect_ratio = fe.layout.width / fe.layout.height.tofloat();
fe.layout.preserve_aspect_ratio = true;

// Force full reload if changing list/display but using same layout
local current_list = "";
function list_transition(ttype, var, ttime)
{
	if (ttype == Transition.ToNewList && current_list != "" && fe.list.name != current_list)
	{
		print("Reload due to list change\n");
		fe.signal("reload");
	}

	return false;
}
fe.add_transition_callback("list_transition");
current_list = fe.list.name;

//////////////////////////////////////////////////////////////////////////////////////////////////
// For testing different resolutions, save current aspect in nv table (stored in script.nv)
if ("AtTheArcade_TestResolution" in fe.nv && fe.nv["AtTheArcade_TestResolution"] > 0)
{
	local override_aspect_ratio = fe.nv["AtTheArcade_TestResolution"];
	local new_width = fe.layout.width;
	local new_height = new_width / override_aspect_ratio;
	if (new_height > fe.layout.height)
	{
		new_height = fe.layout.height;
		new_width = new_height * override_aspect_ratio;
	}
	
	print("Testing aspect ratio " + override_aspect_ratio + " => " + new_width + "x" + new_height + "\n");
	fe.layout.width = new_width;
	fe.layout.height = new_height;
	aspect_ratio = new_width / new_height;
}

fe.add_signal_handler( this, "resolutionTestSignal" )
function resolutionTestSignal( str )
{
	// If testing resolutions, determine current aspect ratio in list,
	// and select the next one (storing in the nv table which persists to a file),
	// then reload the layout to display that next resolution.
	if (str == my_config["resolution_test_key"].tolower())
	{
		// 16:9=1.78, 16:10=1.6, 4:3=1.33, 1:1, 3:4=0.75, 10:16=0.625, 9:16=0.56
		local aspect_ratios = [ 1.78, 1.6, 1.33, 1.0, 0.75, 0.625, 0.56 ];
		local current_aspect_ratio = 0;
		for (local i = 0 ; i < aspect_ratios.len() ; i++)
		{
			if (aspect_ratios[i] <= aspect_ratio)
			{
				current_aspect_ratio = i;
				break;
			}
		}

		local new_aspect_ratio = current_aspect_ratio + 1;
		if (new_aspect_ratio >= aspect_ratios.len())
			new_aspect_ratio = 0;

		fe.nv["AtTheArcade_TestResolution"] <- aspect_ratios[new_aspect_ratio];
		fe.signal("reload");
	}
}

local flx = fe.layout.width;
local fly = fe.layout.height;
local flw = fe.layout.width;
local flh = fe.layout.height;

// cab type defines settings below
// for pinball cabs we will also disable video effects
local cab_type = "arcade";
if (fe.list.name.tolower().find("pinball") >= 0)
	cab_type = "pinball";

//////////////////////////////////////////////////////////////////////////////////////////////////
// Coordinates table for different cabinet types
local cabinet_settings = {
	arcade = {
		cabinet = {
			artwork = "cabinets",
			supports_bezels = true,
			supports_crt_effects = true,
			supports_topper = true,
			cab_w = 1300,
			cab_h = 1080,
			cab_visible_w = 1070, // when visible image is smaller than width due to transparency
			cab_visible_h = 1080,
			// cabinet rendering adjustments
			cab_w_min_pct = 30, // min viewable width to show, as screen percentage (try to stretch if smaller)
			cab_w_stretch_pct = 120, // percentage to "stretch" cab to, to help fill space
			cab_w_max_pct = 68, // max viewable width to show, as screen percentage (try to squeeze if larger)
			cab_w_squeeze_pct = 90, // allowable percentage to "squeeze" cab to, before shrinking to fit
			cab_x_extra_pct = 4, // percentage of extra available width to place left of image
			cab_x_offset_pct = 0, // percentage of image to shift right
			cab_h_max_pct = 100, // max height to show, as screen percentage
			cab_y_extra_pct = 80, // percentage of extra available height to place above image
			cab_y_offset_pct = 0, // percentage of image to shift downward
		},
		snap = {
			autorotate = false,
			snap_x = 200,
			snap_y = 318,
			snap_w = 706,
			snap_h = 526,
			snap_pinch_x = 0,
			snap_on_top = false, // render snap over cabinet? (zorder)
		},
		bezel = {
			bezel_sep_w = 580, // 810, // width to render bezel with separators
			bezel_nosep_w = 620, // 786, // width to render bezel without separators
			bezel_side_w = 158, // width of left/right bezel section where snap is hidden
		},
		marquee = {
			marquee_x = 138,
			marquee_y = 0,
			marquee_w = 832,
			marquee_h = 227,
		}
	},
	pinball = {
		cabinet = {
			artwork = "pincabs",
			supports_bezels = false,
			supports_crt_effects = false,
			supports_topper = false,
			cab_w = 400,
			cab_h = 1080,
			cab_visible_w = 400,
			cab_visible_h = 800,
			// cabinet rendering adjustments
			cab_w_min_pct = 30,
			cab_w_stretch_pct = 130,
			cab_w_max_pct = 50,
			cab_w_squeeze_pct = 100, // no squeeze, favor resize instead
			cab_x_extra_pct = 25,
			cab_x_offset_pct = 0,
			cab_h_max_pct = 80,
			cab_y_extra_pct = 75,
			cab_y_offset_pct = 16,
		},
		snap = {
			autorotate = true,
			snap_x = 94,
			snap_y = 326,
			snap_w = 210,
			snap_h = 210,
			snap_pinch_x = -50,
			snap_on_top = true,
		},
		marquee = {
			marquee_x = 50,
			marquee_y = 26,
			marquee_w = 294,
			marquee_h = 200,
		}
	}
}

local settings = {
	color = {
		black = [0, 0, 0],
		grey = [20, 20, 20],
		blue = [0, 0, 50],
		purple = [40, 0, 40],
		red = [30, 0, 0],
		orange = [30, 15, 0],
		green = [0, 30, 0],
		yellow = [40, 40, 0],
	}
}

// Load a setting from the "settings" array
function Setting(id, name)
{
	return LoadSetting(settings, "settings", id, name);
}

// Load a cabinet-specific setting (arcade, pinball, perhaps others?) from the "cabinet_settings" array
function CabSetting(id, name)
{
	if (cab_type in cabinet_settings)
		return LoadSetting(cabinet_settings[cab_type], "cabinet_settings[" + cab_type + "]", id, name);
	else
		print("\tcabinet_settings[" + cab_type + "] does not exist\n");
}

function LoadSetting(settings_table, logging_description, id, name)
{
	id = id.tolower();
	name = name.tolower();
	
	if (id in settings_table && name in settings_table[id])
	{
		print("\tusing " + logging_description + "[" + id + "][" + name + "] : " + settings_table[id][name] + "\n");
		return settings_table[id][name];
	}
	else if (name in settings_table[id] == false)
	{
		print("\t" + logging_description + "[" + id + "][" + name + "] does not exist\n");
	}
}

print("Attract-Mode Version: " + FeVersion + "\n" + "Screen aspect ratio: "+aspect_ratio+"\n" + "Resolution: "+ScreenWidth+"x"+ScreenHeight+"\n" + "Layout resolution: "+flw+"x"+flh+"\n" + "Shader GLSL available: "+ShadersAvailable+"\n" + "OS: "+OS+"\n");

//////////////////////////////////////////////////////////////////////////////////////////////////
// Select background or pan-and-scan 
if( my_config["enable_image"] == "Static Arcade" ) 
	local bg = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/bkg.jpg", 0, 0, flw, flh );

if( my_config["enable_image"] == "Animated Arcade" )
	local bg = fe.add_image( FeConfigDirectory+"gtc-common/videos/bkg_anim.mp4", 0, 0, flw, flh );
	
if( my_config["enable_image"] == "Fanart" || my_config["enable_image"] == "Flyer" ) 
{
	local bg_art;
	local bg_base = FadeArt( "bkg_base", 0, 0, flw, flh );
	
	local art_x = flw * 0.48;
	local art_w = flw * 0.52;
	local bg_art_srf = fe.add_surface( flw*0.53, flh );
	bg_art_srf.set_pos( art_x, 0 );
	
	if( my_config["enable_image"] == "Fanart" ) 
		bg_art = FadeArt( "fanart", 0, 0, art_w, flh, bg_art_srf );
	else	
		bg_art = FadeArt( "flyer", 0, 0, art_w, flh, bg_art_srf );
		
	bg_art.trigger = Transition.EndNavigation

	local leftside_bg = FadeArt( "leftside_bg", 0, 0, flw, flh );

	local _delay = 2.5;
	if( my_config["enable_ini_anim"] == "No" ) 
		_delay = 1;
	
	local alpha_cfg_start = { when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*_delay }
	animation.add( PropertyAnimation( bg_art_srf, alpha_cfg_start ) );
	
	local move_transition_fanart = { when = Transition.StartLayout, property = "x", start = flx*1.5, end = art_x, tween = "cubic", time = ini_anim_time }
	animation.add( PropertyAnimation( bg_art_srf, move_transition_fanart ) );
}

if( my_config["enable_image"] == "Polygon Trip" )
{
	local bg = fe.add_image( FeConfigDirectory+"gtc-common/videos/Polygon Trip.mp4", 0, 0, flw, flh );
	bg.video_flags = Vid.NoAudio;
}

if( my_config["enable_image"] == "Panscan" ) 
{
	local bgart = PanAndScanImage( FeConfigDirectory+"gtc-common/art/arcade/panscan.jpg", 0, 0, flw, flh );
	bgart.trigger = Transition.EndNavigation;
	bgart.preserve_aspect_ratio = false;
	bgart.set_fit_or_fill("fill");
	bgart.set_anchor(::Anchor.Center);
	bgart.set_zoom(0, 0.00008);
	bgart.set_animate(::AnimateType.Bounce, 0.10, 0.10)
	bgart.set_randomize_on_transition(true);
	bgart.set_start_scale(1.1);
	local alpha_cfg = {
		when = Transition.StartLayout,
		property = "alpha",
		start = 0,
		end = 255,
		time = 800
	}
	animation.add( PropertyAnimation( bgart, alpha_cfg ) );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Play ambience sound / music
local music_file = "";
local song_num = 0;
local list, sound, _loop;
local title_visibile = true;
local title_anim_speed = ini_anim_time;
local first_song = true;

music_delay <- 0;
try {music_delay = my_config["set_music_delay"].tointeger();} catch(e) {}
// idiot proofing
if( music_delay < 0 || music_delay > 300000)
	music_delay = 0;
	
music_path <- my_config["music_path"];
if( music_path != "" )
{
	if ( music_path.len()-1 != '/' && music_path.len()-1 != '\\' ) 
		music_path += "/";
}
else  // use default path
	music_path = fe.script_dir + "music/";

if( my_config["music_play_method"] == "Loop Song" )
	_loop = true;
else
	_loop = false;

if( my_config["enable_ambience"] == "Music" && my_config["enable_song_title"] == "Yes" )
{
	cleanSongTitle <- function( ioffset )
	{
		local name = list[song_num];
		if( name.len() > 0 ) 
		{
			name = split( name, "." )[0]; // remove file name extension from song title
			name = strip( name ); // remove white-space-only from the beginning or end of the song title
		}
		return name;
	}
		
	// song title
	local song_title_frame = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/frame.png", 0, fly*-1.2, flw, flh*0.06 );
	song_title_frame.zorder = 1;

	// animation configs for song title frame
	local titleframe_in_transition = { property = "y", start = fly*-1.2, end = fly*0.0, time = title_anim_speed }
	local titleframe_out_transition = { property = "y", start = fly*0.0, end = fly*-1.2, delay = my_config["song_title_time"].tofloat(), time = title_anim_speed }

	local song_title = fe.add_text( "", flx*0.1, fly*-1.2, flw*0.8, flh*0.05 );
	song_title.set_rgb(255, 120, 0);
	song_title.charsize = flh*0.028;
	song_title.align = Align.Centre;
	song_title.zorder = 1;

	if( ShadersAvailable == 1 )
	{
		local shader = fe.add_shader( Shader.Fragment "shaders/bloom_shader_text.frag" );
		shader.set_texture_param("bgl_RenderedTexture"); 
		song_title.shader = shader;
	}

	// animation configs for song title text
	local title_in_transition = { property = "y", start = fly*-1.2, end = fly*0.0, time = title_anim_speed }
	local title_out_transition = { property = "y", start = fly*0.0, end = fly*-1.2, delay = my_config["song_title_time"].tofloat(), time = title_anim_speed }

	fe.add_signal_handler( this, "showSongTitle" )
	showSongTitle <- function( str ) 
	{
		if( title_visibile == true && !first_song )
		{
			title_visibile = false;
			if( list.len() > 0 )
			{
				song_title.msg = cleanSongTitle(0);
				animation.add( PropertyAnimation( song_title_frame, titleframe_in_transition ) );
				animation.add( PropertyAnimation( song_title_frame, titleframe_out_transition ) );	
				animation.add( PropertyAnimation( song_title, title_in_transition ) );
				animation.add( PropertyAnimation( song_title, title_out_transition ) );	
			}
		}
			
		return false;
	}
}

function playSound( path, loop=false ) 
{
	sound = fe.add_sound( path, true );
	sound.playing = true;
}

// ambience sound or music selection
if( my_config["enable_ambience"] != "No" )
{
	if( my_config["enable_ambience"] == "It's 1983" )
		playSound( FeConfigDirectory+"gtc-common/sounds/Arcade_1983.mp3", true );
	else if( my_config["enable_ambience"] == "It's 1992" )
		playSound( FeConfigDirectory+"gtc-common/sounds/Arcade_1992.mp3", true );
	else if( my_config["enable_ambience"] == "Music" )
	{
		// create a list of files in the music folder 
		list = zip_get_dir( music_path );
		if( list.len() > 0 )
		{
			if( my_config["music_play_method"] == "Shuffle" )
				song_num = floor(((rand() % 1000 ) / 1000.0) * list.len());

			music_file = music_path + list[song_num];
		}
	}
}

fe.add_ticks_callback( "music_tick" );
function music_tick( ttime ) 
{
	// delay playing first song for duration decided by the user
	if( my_config["enable_ambience"] == "Music" )
	{
		if( ttime >= music_delay && list.len() > 0 && first_song )
		{
			first_song = false;
			playSound( music_file, _loop );
			
			if( my_config["enable_song_title"] == "Yes" )
			{
				title_visibile = true;
				showSongTitle("");
			}
		}
		else if( first_song == false )
		{
			// loop song
			if( ! sound.playing && _loop )
				sound.playing = true;

			// loop list or shuffle
			if( ! sound.playing && ! _loop ) 
			{
				if( my_config["music_play_method"] == "Loop List" )
				{						
					song_num++;
					if( song_num > list.len()-1 )
						song_num = 0;
				}
				
				if( my_config["music_play_method"] == "Shuffle" )
					song_num = floor(((rand() % 1000 ) / 1000.0) * list.len());
				
				sound.file_name = music_path + list[song_num];
				sound.playing = true;
				
				if( my_config["enable_song_title"] == "Yes" )
				{
					title_visibile = true;
					showSongTitle("");
				}
			}
		}
	}
}

function musicSelection( selection="" ) 
{
	if( first_song == false )
	{
		if( my_config["music_play_method"] == "Shuffle" )  
			song_num = floor(((rand() % 1000 ) / 1000.0) * list.len());
			
		if( selection == "next" ) 
		{
			song_num++;  
			if( song_num > list.len()-1 )
				song_num = 0;  //go back to first song in list
		}
		
		if( selection == "prev" )  
		{
			song_num--;  
			if( song_num < 0 )
				song_num = list.len()-1;  //go to last song in list
		}
		
		music_file = music_path + list[song_num];
		sound.playing = false;	
		playSound(music_file, _loop);
		
		if( my_config["enable_song_title"] == "Yes" )
		{
			title_anim_speed = 200;
			title_visibile = true;
			showSongTitle("");
		}
	}
}

// music playback controls
fe.add_signal_handler( this, "musicNavSignal" )
function musicNavSignal( str ) 
{
	if( my_config["enable_ambience"] == "Music" && list.len() > 0 )
	{
		switch( str ) 
		{
			case my_config["user_nextsong_key"].tolower():
				// play next song from the music folder
				musicSelection("next");
			break;
			case my_config["user_prevsong_key"].tolower():
				// play previous song from the music folder
				musicSelection("prev");
			break;
		}
	}
	
	return false;
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Scanline effect overlay for background art
local bg_scanline;
if( my_config["enable_bg_scanline"] != "No" )
{
	local scanlines = FeConfigDirectory+"gtc-common/art/arcade/scanlines_1920.png"
	if( ScreenWidth < 1920 )
		scanlines = FeConfigDirectory+"gtc-common/art/arcade/scanlines_720.png"
		
	bg_scanline = fe.add_image( scanlines, 0, 0, flw, flh );
	bg_scanline.preserve_aspect_ratio = false;

	if( my_config["enable_bg_scanline"] == "Light" )
		bg_scanline.alpha = 30;
	else if( my_config["enable_bg_scanline"] == "Medium" )
		bg_scanline.alpha = 80;
	else if( my_config["enable_bg_scanline"] == "Strong" )
		bg_scanline.alpha = 150;
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Arcade cabinet and all related art
// Use setting table for cabinet and related art sizing, then resize entire surface to fit.

//////////////////////////////////////////////////////////////////////////////////////////////////
// NOTE: If you are trying to adjust cabinet width or position, you probably don't want to change
// this logic, but instead modify the values that drive it in the "cabinet_settings" object.
//////////////////////////////////////////////////////////////////////////////////////////////////
local cab_w = CabSetting("cabinet", "cab_w");
local cab_h = CabSetting("cabinet", "cab_h");
local cab_ratio = cab_w / cab_h.tofloat();
local cab_visible_w = CabSetting("cabinet", "cab_visible_w");
local cab_visible_h = CabSetting("cabinet", "cab_visible_h");
local cab_w_min_pct = CabSetting("cabinet", "cab_w_min_pct") / 100.0;
local cab_w_max_pct = CabSetting("cabinet", "cab_w_max_pct") / 100.0;
local cab_h_max_pct = CabSetting("cabinet", "cab_h_max_pct") / 100.0;

// Components within the cab are added full size, but the outer_main_srf is resized to fit
local resized_cab_h = flh; // start with full height cabinet
local resized_cab_w = resized_cab_h * cab_ratio;
local visible_w_pct = cab_visible_w / cab_w.tofloat(); // 'visible' ignores transparency on right side of cabinet
local visible_cab_w = resized_cab_w * visible_w_pct;
local adjustment = "";

local min_w = cab_w_min_pct * flw;
if (visible_cab_w < min_w)
{
	// if visible width below min visible width, resize width (stretch)
	local cab_w_stretch_pct = CabSetting("cabinet", "cab_w_stretch_pct") / 100.0;
	local resize_pct = min_w / visible_cab_w.tofloat();
	if (resize_pct > cab_w_stretch_pct)
		resize_pct = cab_w_stretch_pct;
	resized_cab_w = (visible_cab_w * resize_pct) / visible_w_pct;
	adjustment += " stretch_w " + (resize_pct * 100.0).tointeger() + "%";
}

local max_w = cab_w_max_pct * flw;
if (visible_cab_w > max_w)
{
	// if visible width exceeded max visible width, resize width (squeeze)
	local cab_w_squeeze_pct = CabSetting("cabinet", "cab_w_squeeze_pct") / 100.0;
	local squeeze_pct = max_w / visible_cab_w.tofloat();

	if (squeeze_pct < cab_w_squeeze_pct)
	{
		// need to squeeze width by cab_w_squeeze_pct, then also reduce cab size to get to max_w
		squeeze_pct = cab_w_squeeze_pct;
		local reduce_needed = (visible_cab_w * squeeze_pct) - max_w;
		resized_cab_w = max_w / visible_w_pct;
		resized_cab_h -= (reduce_needed / cab_ratio);
		adjustment += " reduce to " + ((1 - (reduce_needed / visible_cab_w)) * 100.0).tointeger() + "%";
	}
	else
	{
		// just need to squeeze width by squeeze_pct
		resized_cab_w = (visible_cab_w * squeeze_pct) / visible_w_pct;
	}
	if (squeeze_pct < 100)
		adjustment += " squeeze_w " + (squeeze_pct * 100.0).tointeger() + "%";
}

local max_h = cab_h_max_pct * flh;
local visible_h_pct = cab_visible_h / cab_h.tofloat();
local visible_cab_h = resized_cab_h * visible_h_pct;

if (visible_cab_h > max_h)
{
	// if visible height exceeded max visible height, resize height
	resized_cab_h = max_h / visible_h_pct;
	resized_cab_w = resized_cab_h * cab_ratio;
	adjustment += " squeeze_h";
}

// Determine positioning of resized cab
local resized_cab_x = (flw - resized_cab_w) * (CabSetting("cabinet", "cab_x_extra_pct") / 100.0)
	+ resized_cab_w * (CabSetting("cabinet", "cab_x_offset_pct") / 100.0);
local resized_cab_y = (flh - resized_cab_h) * (CabSetting("cabinet", "cab_y_extra_pct") / 100.0)
	+ resized_cab_h * (CabSetting("cabinet", "cab_y_offset_pct") / 100.0);

resized_cab_x = resized_cab_x.tointeger();
resized_cab_y = resized_cab_y.tointeger();
resized_cab_w = resized_cab_w.tointeger();
resized_cab_h = resized_cab_h.tointeger();
local resized_w_ratio = resized_cab_w / cab_w.tofloat();
local resized_h_ratio = resized_cab_h / cab_h.tofloat();

print("Rendered cab as " + resized_cab_w + "x" + resized_cab_h + " @ " + 
	  resized_cab_x + "x" + resized_cab_y + adjustment + 
	  " (ratio to orig = " + (resized_w_ratio * 100).tointeger() + "%x" + (resized_h_ratio * 100).tointeger() + "%)\n");

// Main surface, all other surfaces are attached to this one
local main_srf; // contains snap, bezels, marquee
local outer_main_srf; // contains main_srf (and top if needed), then resized

local cab_topper;
local add_topper = resized_cab_y > 0 && CabSetting("cabinet", "supports_topper") == true;

if (add_topper)
{
	// add topper to hide upper edge of cabinet
	local cab_topper_h = 20;
	outer_main_srf = fe.add_surface(cab_w, cab_h + cab_topper_h);
	cab_topper = outer_main_srf.add_image("cabinetTop.png", 0, 0, cab_w, cab_topper_h);
	main_srf = outer_main_srf.add_surface(cab_w, cab_h);
	main_srf.set_pos(0, cab_topper_h);
}
else
{
	// when cab is full-height, outer_main_srf is the same as main_srf
	main_srf = fe.add_surface( cab_w, cab_h );
	outer_main_srf = main_srf;
}

// Resize to fit
outer_main_srf.set_pos(resized_cab_x, resized_cab_y, resized_cab_w, resized_cab_h);

local snap_w = CabSetting("snap", "snap_w");
local snap_h = CabSetting("snap", "snap_h");
local snap_x = CabSetting("snap", "snap_x");
local snap_y = CabSetting("snap", "snap_y");
local snap_pinch_x = CabSetting("snap", "snap_pinch_x");

// Check if autorotate enabled for cab type, but disable for fx3 snaps which are vertical landscape
local snap_autorotate = CabSetting("snap", "autorotate") && fe.list.name.tolower().find("fx3") == null;

// Black background when no snap is available
//local snapbg_srf = main_srf.add_surface( snap_w, snap_h );
//snapbg_srf.set_pos( snap_x, snap_y );
//local snapbg = snapbg_srf.add_image( FeConfigDirectory+"gtc-common/art/arcade/vertical_cover.png", 0, 0, snap_w, snap_h );
//snapbg_srf.pinch_x = snap_pinch_x;


// Bezels for vertical snaps
local bezel_left_srf, bezel_right_srf, bezel_left, bezel_right;
local bezel_type = my_config["enable_bezels"];
local bezel_side_w = 0
local using_bezels = my_config["enable_verticlesnap"] == "Yes" 
	&& CabSetting("cabinet", "supports_bezels") == true
	&& bezel_type != "No";

if (using_bezels)
{
	local bezel_name = "bezel_nosep";
	if (bezel_type == "Bezels with Separators")
		bezel_name = "bezel_sep";

	bezel_side_w = CabSetting("bezel", "bezel_side_w");
	local bezel_w = CabSetting("bezel", bezel_name + "_w");
	local bezel_hide_w = (bezel_w - snap_w) / 2;
	if (bezel_hide_w < 0)
		bezel_hide_w = 0;

	// Left side of bezel image
	bezel_left_srf = main_srf.add_surface(snap_w * 0.5, snap_h);
	bezel_left_srf.set_pos(snap_x, snap_y);
	bezel_left_srf.visible = false;
	bezel_left = bezel_left_srf.add_artwork("bezels", - bezel_hide_w, 0, bezel_w, snap_h);
	bezel_left.trigger = Transition.EndNavigation;
	bezel_left.mipmap = true;

	// Right side of bezel image
	bezel_right_srf = main_srf.add_surface(snap_w * 0.5, snap_h);
	bezel_right_srf.set_pos(snap_x + (snap_w / 2), snap_y);
	bezel_right_srf.visible = false;
	local bezel_right_x = (snap_w / 2) + bezel_hide_w - bezel_w;
	bezel_right = bezel_right_srf.add_artwork("bezels", bezel_right_x, 0, bezel_w, snap_h);
	bezel_right.trigger = Transition.EndNavigation;
	bezel_right.mipmap = true;
}

// Snap
local cab_srf;
if (CabSetting("snap", "snap_on_top") == true)
	cab_srf = main_srf.add_surface( cab_w, cab_h );

local snap_surface = main_srf.add_surface( snap_w, snap_h );
snap_surface.set_pos( snap_x, snap_y );
snap_surface.pinch_x = snap_pinch_x;
local snap = snap_surface.add_artwork( "snap", 0, 0, snap_w, snap_h );
snap.trigger = Transition.EndNavigation;

local preserve_snap_aspect = my_config["enable_verticlesnap"] == "Yes" && snap_pinch_x == 0;
if (preserve_snap_aspect)
	snap.preserve_aspect_ratio = true;

if ( my_config["mute_videos"] == "Yes" )
	snap.video_flags = Vid.NoAudio;

// Support for auto snap rotation to handle horizontal pinball snaps
if (snap_autorotate)
{
	fe.add_transition_callback("snap_transitions");
	snap_transitions <- function( ttype, var, ttime ) {
		switch (ttype)
		{
			case Transition.ToNewList:	
			case Transition.EndNavigation:
				if (snap.texture_width > snap.texture_height)  // landscape snapshot/video
				{
					snap_surface.rotation = 270;
					snap_surface.pinch_x = 0;
					snap_surface.pinch_y = 0 - snap_pinch_x;
					snap_surface.width = snap_h;
					snap_surface.height = snap_w - (snap_pinch_x * 2);
					snap_surface.set_pos(snap_x + snap_pinch_x, snap_y + snap_h);
				}
				else // Normal portrait orientation snapshot/video
				{
					snap_surface.rotation = 0;
					snap_surface.pinch_x = snap_pinch_x;
					snap_surface.pinch_y = 0;
					snap_surface.width = snap_w;
					snap_surface.height = snap_h;
					snap_surface.set_pos(snap_x, snap_y);
				}
			break;
		}
		return false;
	}
}

// snap shader effects
local using_snap_shader = my_config["enable_snap_shader"] != "No" 
	&& ShadersAvailable == 1 
	&& CabSetting("cabinet", "supports_crt_effects") == true;
	
if (using_snap_shader)
{
	if ( my_config["enable_snap_shader"] == "CRT Bloom")
	{
		local sh = fe.add_shader( Shader.Fragment, "shaders/bloom_shader.frag" );
		sh.set_texture_param("bgl_RenderedTexture"); 
		snap_surface.shader = sh;
	}
	
	if ( my_config["enable_snap_shader"] == "CRT Lottes")
	{
		local shader_lottes = null;
		
		shader_lottes=fe.add_shader(
			Shader.VertexAndFragment,
			"shaders/CRT-geom.vsh",
			"shaders/CRT-geom.fsh");
			
		// APERATURE_TYPE
		// 0 = VGA style shadow mask.
		// 1.0 = Very compressed TV style shadow mask.
		// 2.0 = Aperture-grille.
		shader_lottes.set_param("aperature_type", 1.0);
		shader_lottes.set_param("hardScan", 0.0);   // Hardness of Scanline -8.0 = soft -16.0 = medium
		shader_lottes.set_param("hardPix", -2.0);     // Hardness of pixels in scanline -2.0 = soft, -4.0 = hard
		shader_lottes.set_param("maskDark", 0.9);     // Sets how dark a "dark subpixel" is in the aperture pattern.
		shader_lottes.set_param("maskLight", 0.3);    // Sets how dark a "bright subpixel" is in the aperture pattern
		shader_lottes.set_param("saturation", 1.1);   // 1.0 is normal saturation. Increase as needed.
		shader_lottes.set_param("tint", 0.0);         // 0.0 is 0.0 degrees of Tint. Adjust as needed.
		shader_lottes.set_param("distortion", 0.15);		// 0.0 to 0.2 seems right
		shader_lottes.set_param("cornersize", 0.04);  // 0.0 to 0.1
		shader_lottes.set_param("cornersmooth", 80);  // Reduce jagginess of corners
		shader_lottes.set_texture_param("texture");
		
		snap.shader = shader_lottes;
		
		fe.add_transition_callback( "shader_transitions" );
		shader_transitions <- function( ttype, var, ttime ) {
			switch( ttype )
			{
				case Transition.ToNewList:	
				case Transition.EndNavigation:
					// snap.width = snap_surface.subimg_width;
					// snap.height = snap_surface.subimg_height;
					// Play with these settings to get a good final image
					snap.shader.set_param("color_texture_sz", snap_surface.width, snap_surface.height);
					snap.shader.set_param("color_texture_pow2_sz", snap_surface.width, snap_surface.height);
				break;
			}
			return false;
		}
	}
}

// CRT scanlines
local scanlines_srf, crt_scanlines;
local using_scanlines = my_config["enable_crt_scanline"] != "No" && CabSetting("cabinet", "supports_crt_effects") == true;

if (using_scanlines)
{
	scanlines_srf = main_srf.add_surface( snap_w, snap_h );
	scanlines_srf.set_pos( snap_x, snap_y );
	local scan_art = FeConfigDirectory+"gtc-common/art/arcade/scanlines_720.png";
	crt_scanlines = scanlines_srf.add_image( scan_art, 0, 0, snap_w, snap_h );
	crt_scanlines.preserve_aspect_ratio = true;

	if( my_config["enable_crt_scanline"] == "Light" )
		crt_scanlines.alpha = 50;
	else if( my_config["enable_crt_scanline"] == "Medium" )
		crt_scanlines.alpha = 100;
	else if( my_config["enable_crt_scanline"] == "Dark" )
		crt_scanlines.alpha = 200;

	scanlines_transitions <- function(ttype, var, ttime) 
	{
		switch (ttype) 
		{
			case Transition.ToNewList:	
			case Transition.EndNavigation:
				// Hide scanlines for games that use vector graphics
				if (fe.game_info(Info.DisplayType) == "vector")
					scanlines_srf.visible = false;
				else
					scanlines_srf.visible = true;
				break;
		}
		
		return false;
	}
	
	fe.add_transition_callback("scanlines_transitions");
}

if (using_bezels)
{
	bezel_transitions <- function(ttype, var, ttime) 
	{
		switch (ttype)
		{
			case Transition.ToNewList:	
			case Transition.EndNavigation:
				local bezel_width = 0;
				local orientation = "horizontal";
				
				if (snap.texture_width < snap.texture_height)  // vertical game snapshot
				{
					orientation = "vertical";
					bezel_width = bezel_side_w;
					bezel_left_srf.visible = true;
					bezel_right_srf.visible = true;
				}
				else
				{
					bezel_left_srf.visible = false;
					bezel_right_srf.visible = false;
				}

				if (using_scanlines)
				{
					// adjust scanlines so they don't cover the bezels
					scanlines_srf.x = snap_x - 8 + bezel_width;
					scanlines_srf.width = snap_w - (bezel_width * 1.9);
				}

				print("> " + fe.game_info(Info.Name) + ": " + orientation + " " + snap.texture_width + "x" + snap.texture_height + "\n");
				break;
		}
		
		return false;
	}
	
	fe.add_transition_callback("bezel_transitions");
}

// CRT scratches
if( my_config["enable_crt_scratches"] == "Yes" )
{
	local scratched_cover_srf = main_srf.add_surface( snap_w, snap_h );
	scratched_cover_srf.set_pos( snap_x, snap_y );
	local scratched_cover = scratched_cover_srf.add_image( FeConfigDirectory+"gtc-common/art/arcade/scratched_cover.png", 0, 0, snap_w, snap_h );
	scratched_cover.alpha = 100;
	scratched_cover_srf.pinch_x = snap_pinch_x;
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Marquee
local marquee_w = CabSetting("marquee", "marquee_w");
local marquee_h = CabSetting("marquee", "marquee_h");
local marquee_x = CabSetting("marquee", "marquee_x");
local marquee_y = CabSetting("marquee", "marquee_y");

local marquee_srf = main_srf.add_surface( marquee_w, marquee_h );
marquee_srf.set_pos( marquee_x, marquee_y );
local marquee = marquee_srf.add_artwork( "marquee", 0, 0, marquee_w, marquee_h );
marquee.trigger = Transition.EndNavigation;

if( my_config["enable_Lmarquee"] == "Yes" )
{
	local shader = fe.add_shader( Shader.Fragment "shaders/bloom_shader_marquee.frag" );
	shader.set_texture_param( "bgl_RenderedTexture" );
	marquee.shader = shader;
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Cabinet
if (CabSetting("snap", "snap_on_top") != true)
	cab_srf = main_srf.add_surface( cab_w, cab_h );
cab_srf.set_pos( 0, 0 );
local cab = cab_srf.add_artwork( CabSetting("cabinet", "artwork"), 0, 0, cab_w, cab_h );
cab.trigger = Transition.EndNavigation;

// animate the main surface
if( my_config["enable_ini_anim"] == "Yes" )
{
	local animate_cab = { when = Transition.StartLayout, property = "x", start = flx*-1.555, end = resized_cab_x, tween = "cubic", time = ini_anim_time }
	animation.add( PropertyAnimation( outer_main_srf, animate_cab ) );
}

if (add_topper && ShadersAvailable)
{
	local topper_shader = fe.add_shader(Shader.Fragment, "shaders/masked_color_from_sample.frag");
	
	topper_shader.set_texture_param("maskTexture", cab_topper);
	topper_shader.set_param("surfaceDimensions", cab_w, cab_h + cab_topper.height);
	topper_shader.set_param("maskDimensions", cab_topper.width, cab_topper.height);
	topper_shader.set_param("copyRect", 93, 0, 40, 20); // left t-molding rectangle of cabinet topper
	topper_shader.set_param("copyRect2", 971, 0, 40, 20); // right t-molding rectangle of cabinet topper

	topper_shader.set_texture_param("sampleTexture", cab);
	topper_shader.set_param("sampleDimensions", cab.width, cab.height);
	topper_shader.set_param("samplePoint", 124, 0);
	topper_shader.set_param("samplePoint2", 115, 0);
	topper_shader.set_param("samplePoint3", 220, 0);
	cab_topper.shader = topper_shader;
}

//////////////////////////////////////////////////////////////////////////////////////////////////
// wheel background
local wheel_art;
local wheel_art_alpha = 220; // default "dark" shading level

local slot_width = flw * 0.12; // width of shaded portion
if (my_config["wheel_logo_size"] == "Larger")
	slot_width *= 1.5;

local wheel_height = flh + slot_width;
if (aspect_ratio < 1) // portrait
	wheel_height *= 0.6;

local wheel_radius_x = flw * 0.60;
local wheel_radius_y = wheel_height * 0.75;

if (my_config["wheel_type"] != "Round")
{	// adjustments for vertical wheel
	wheel_height = flh * 1.2;
	wheel_radius_x = flw * 0.5; // smaller radius = further right
}

local wheel_offset_y = (flh - wheel_height) / 2;
local wheel_offset_x = flw - (wheel_radius_x * 0.5); // determines how much wheel width to show
if (my_config["wheel_logo_size"] == "Larger")
	wheel_offset_x -= flw * 0.04;
if (my_config["wheel_position"] == "Adjust Right")
	wheel_offset_x += flw * 0.04;

local wheel_center_x = wheel_offset_x + wheel_radius_x;

if (my_config["enable_wl_bg"] != "No")
{
	if (my_config["enable_wl_bg"] == "Light") 
		wheel_art_alpha = 80;
	else if (my_config["enable_wl_bg"] == "Medium") 
		wheel_art_alpha = 180;

	if (ShadersAvailable == 1)
	{
		// Use shaders to draw the desired size and shape shaded area.
		// The surface_offset is needed to translate the layout size/position to the GLSL shader
		// (particularly when we're testing custom layout aspect ratios).
		local shader;
		local wheel_shader_srf = fe.add_surface(flx, fly);

		local shade_color = Setting("color", my_config["wheel_bg_color"]);
		if (shade_color == null)
			shade_color = [0, 0, 0];

		if (my_config["wheel_type"] == "Round")
		{
			shader = fe.add_shader(Shader.Fragment, "shaders/shaded_arc.frag");
			shader.set_param("shadeRadius", wheel_radius_x, wheel_radius_y);
			shader.set_param("shadeCenter", wheel_center_x, flh / 2);
			shader.set_param("arcWidth", slot_width);
			shader.set_param("shadeEdge", 30); // level of anti-alias "fuzziness" applied to the edge (0-100)
		}
		else
		{
			shader = fe.add_shader(Shader.Fragment, "shaders/shaded_rectangle.frag");
			shader.set_param("shadeSize", slot_width, flh);
			shader.set_param("shadePosition", wheel_offset_x, 0);
		}

		local layout_offset_x = (flw - ScreenWidth) / 2;
		local layout_offset_y = (flh - ScreenHeight) / 2;
		shader.set_param("screenResolution", ScreenWidth, ScreenHeight);
		shader.set_param("fragmentOffset", layout_offset_x, layout_offset_y);
		shader.set_param("shadeColor", shade_color[0], shade_color[1], shade_color[2]); // RGB color of shaded region
		shader.set_param("shadeAlpha", wheel_art_alpha);

		wheel_shader_srf.shader = shader;
		wheel_art = wheel_shader_srf;
	}
	else // fallback images when shaders aren't available, try to show images at approximately the desired size
	{
		local background_x, background_w;
		local background_h = wheel_height;
		local background_y = wheel_offset_y;
		
		if (my_config["wheel_type"] == "Round")
		{
			// Round image: 1280x720, shading starts at offset 842, curve width 262
			//   width = (desired shaded width) * (background file width / shaded portion width)
			//   offset = wheel start - (shaded portion start * (rendered width / background file width)) - margin
			background_w = slot_width * 1.2 * (1280.0 / 262.0);
			background_x = wheel_offset_x - (842 * (background_w / 1280.0));
			wheel_art = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/wheel_art.png", background_x, background_y, background_w, background_h );
		}
		else
		{
			// Vertical image: 1280x720, shading starts at offset 908, shaded width 359
			background_w = slot_width * (1280.0 / 359.0);
			background_x = wheel_offset_x - (908 * (background_w / 1280.0));
			wheel_art = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/wheel_vert.png", background_x, wheel_offset_y, background_w, background_h );
		}
		wheel_art.alpha = wheel_art_alpha;
	}
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel
local _partially = 60;
local wheel_count, _alpha, wheel_x=[], wheel_y=[], wheel_w=[], wheel_a=[], wheel_h=[], wheel_r=[];

try { wheel_count = my_config["wheels"].tointeger(); } catch ( e ) { }

local total_slots = 12;
local center_slot = total_slots / 2;
local center_slot_y;
local slot_margin = slot_width * 0.12;

// Circle goes from (0 to 2*pi) radians, so half-circle is (0 to pi).
// We're hiding part of the semi-circle, so further reduce the range of angles we will process.
local hidden_angle = 0.30 * 3.14; // percentage of half circle times pi
if (wheel_height >= fly)
	hidden_angle = 0.45 * 3.14;
local visible_angle = 3.14 - hidden_angle;
local angle_per_slot = visible_angle / total_slots.tofloat();

for (local slot = 0; slot <= total_slots; slot++)
{
	local slot_offset = (total_slots / 2) - slot;
	local slot_angle = (hidden_angle / 2) + (slot * angle_per_slot);
	local slot_x, slot_y, slot_w, slot_h, slot_r, slot_a;
	
	if (my_config["wheel_type"] == "Round")
	{
		// Starting with the formula for points on a circle (where t is the angle from 0 to 2 * pi)
		// x = r * cos(t), y = r * sin(t), then use separate x/y radii for an ellipse
		slot_x = wheel_center_x - (wheel_radius_x * sin(slot_angle));
		slot_y = wheel_offset_y + (wheel_height / 2) - (wheel_radius_y * cos(slot_angle));
		slot_r = slot_offset * 8;
	}
	else
	{
		slot_x = wheel_offset_x;
		slot_y = wheel_offset_y + (slot * (wheel_height / total_slots));
		slot_r = 0;
	}
	
	slot_a = 255;
	slot_w = slot_width;	
	slot_h = wheel_height / total_slots;
	
	if (my_config["wheel_semi_t"] == "Yes")
	{
		slot_a -= abs(slot_offset) * 40; // the further away from the center, the more transparent
	}
	
	if (slot == center_slot) // adjust size/position of selected game
	{
		slot_x *= 0.95;
		if (my_config["wheel_logo_size"] == "Larger")
			slot_x *= 0.97;
		slot_y = ((flh - slot_h) / 2);
		slot_w *= 1.6;
		slot_h *= 1.8;
		slot_a = 255;
		center_slot_y = slot_y + (slot_h / 2);
	}

	wheel_x.push(slot_x + slot_margin);
	wheel_y.push(slot_y);
	wheel_w.push(slot_w - (2 * slot_margin));
	wheel_h.push(slot_h);
	wheel_r.push(slot_r);
	wheel_a.push(slot_a);
}

//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel pointer
local pointer; 

if( my_config["enable_pointer"] == "Yes" ) 
{
	// pointer_size is the image height, pointer_size/2 is the visible width.
	// Note that there are an even number of slots, so center slot is not true center.
	local pointer_size = flw * 0.15;
	local pointer_y = center_slot_y - (pointer_size / 2);

	local start_x = flx - (pointer_size / 2);
	local end_x = (flx * 0.98) - (pointer_size / 2);

	pointer = fe.add_image( "pointers/default.png", start_x, pointer_y, pointer_size, pointer_size );	
	local movex_cfg = {	when = Transition.ToNewSelection, property = "x", start = end_x, end = pointer.x, time = 200 }	
	animation.add( PropertyAnimation( pointer, movex_cfg ) );
}

//////////////////////////////////////////////////////////////////////////////////////////////////
// Wheel animation
class WheelEntry extends ConveyorSlot
{
	constructor()
	{
		base.constructor( ::fe.add_artwork( "wheel" ) );
	}

	function on_progress( progress, var )
	{
		local p = progress / 0.1;
		local slot = p.tointeger();
		p -= slot;
		
		slot++;

		if( slot < 0 ) slot=0;
		if( slot >=10 ) slot=10;

		m_obj.x = wheel_x[slot] + p * ( wheel_x[slot+1] - wheel_x[slot] );
		m_obj.y = wheel_y[slot] + p * ( wheel_y[slot+1] - wheel_y[slot] );
		m_obj.width = wheel_w[slot] + p * ( wheel_w[slot+1] - wheel_w[slot] );
		m_obj.height = wheel_h[slot] + p * ( wheel_h[slot+1] - wheel_h[slot] );
		m_obj.rotation = wheel_r[slot] + p * ( wheel_r[slot+1] - wheel_r[slot] );
		m_obj.alpha = wheel_a[slot] + p * ( wheel_a[slot+1] - wheel_a[slot] );
		if( my_config["wheel_logo_mipmap"] == "Yes" )
			m_obj.mipmap = true;
		if( my_config["wheel_logo_aspect"] == "Yes" )
			m_obj.preserve_aspect_ratio=true;
	}
};

local wheel_entries = [];
for( local i=0; i<wheel_count/2; i++ )
	wheel_entries.push( WheelEntry() );

local remaining = wheel_count - wheel_entries.len();

// we do it this way so that the last wheelentry created is the middle one showing the current
// selection (putting it at the top of the draw order)
for ( local i=0; i<remaining; i++ )
	wheel_entries.insert( wheel_count/2, WheelEntry() );

local conveyor = Conveyor();
conveyor.set_slots( wheel_entries );
try { conveyor.transition_ms = my_config["transition_ms"].tointeger(); } catch ( e ) { }

	
// Favourite games marker
function FavStar() 
{
	if( fe.game_info( Info.Favourite ) == "1" ) return FeConfigDirectory+"gtc-common/art/arcade/fav.png";
}
	
local favourite_marker;
if( my_config["enable_favstar"] == "Left of Wheel" )
{
	local x, y, wh;
	
	if( conveyor.m_objs.len() > 0 )
	{
		local art = wheel_entries[conveyor.m_objs.len()/2].m_obj;
		x = art.x-(flw*0.042);
		wh = flw*0.04;
		y = center_slot_y - (wh / 2);
	}

	favourite_marker = fe.add_image( "[!FavStar]",x, y, wh, wh );
	
	if( my_config["wheel_logo_mipmap"] == "Yes" )
		favourite_marker.mipmap = true;
}

//Wheel fading code starts here
if( my_config["wheel_fadeout"] != "No" )
{
	first_tick <- 0;
	stop_fading <- true;
	wheel_fade_ms <- 0;
	try { wheel_fade_ms = my_config["wheel_fade_ms"].tointeger(); } catch ( e ) { }

	if( wheel_fade_ms > 0 )
	{
		wheel_fade_transition <- function( ttype, var, ttime )
		{
			if( ttype == Transition.ToNewSelection || ttype == Transition.ToNewList )
			{
				print("enable="+my_config["enable_favstar"]+",wa="+wheel_art+"\n");
				first_tick = -1;
				my_delay = fe.layout.time;
				if( my_config["enable_pointer"] != "No" ) 
					pointer.alpha = 255;

				if( my_config["enable_wl_bg"] != "No" )
				{
					if (ShadersAvailable == 1)
						wheel_art.shader.set_param("shadeAlpha", wheel_art_alpha);
					else
						wheel_art.alpha = wheel_art_alpha;
				}

				if( my_config["enable_favstar"] != "No" )
				{
					if( fe.game_info( Info.Favourite, var ) == "1" )
						favourite_marker.alpha = 255;
				}
			}
			return false;	 
		}
		fe.add_transition_callback( "wheel_fade_transition" );
		
		wheel_alpha <- function( ttime )
		{
			local _elapsed = 0;
			
			if( first_tick == -1 )
				stop_fading = false;

			// handle wheel alpha after keyboard search
			if( first_tick > 0 )
				_elapsed = ttime - first_tick;
			
			if( _elapsed < wheel_fade_ms )
			{
				local count = conveyor.m_objs.len();

				for( local i=0; i<count; i++ )
				{
					if( i == count/2 )
						conveyor.m_objs[i].alpha = 255;
					else
					{
						if( my_config["wheel_semi_t"] == "Yes" )
							conveyor.m_objs[i].alpha = 80;
						else
							conveyor.m_objs[i].alpha = 255;
					}	
				}
			}

			// Wheel fading
			if( !stop_fading && ttime - my_delay >= my_play )
			{
				local elapsed = 0;

				if( first_tick > 0 )
					elapsed = ttime - first_tick;

				local count = conveyor.m_objs.len();
				
				for( local i=0; i<count; i++ )
				{
					if( elapsed > wheel_fade_ms)
					{
						if( my_config["wheel_fadeout"] == "Partially" )
							conveyor.m_objs[i].alpha = _partially;
						else
							conveyor.m_objs[i].alpha = 0;
					}
					else
					{
						if( i == count/2 )
						{
							_alpha = (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
								_alpha = _partially;
							conveyor.m_objs[i].alpha = _alpha;
						}
						else
						{
							local _start_alpha = 79;
							if( my_config["wheel_semi_t"] == "No" )
								_start_alpha = 254;
							_alpha = (_start_alpha * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
								_alpha = _partially;
							conveyor.m_objs[i].alpha = _alpha;
						}
						
						if( my_config["enable_pointer"] != "No" ) 
						{
							_alpha =  (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if(_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							pointer.alpha = _alpha;
						}
						
						if( my_config["enable_wl_bg"] != "No" )
						{
							_alpha = (wheel_art_alpha * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
								_alpha = _partially;

							if (ShadersAvailable == 1)
								wheel_art.shader.set_param("shadeAlpha", _alpha);
							else
								wheel_art.alpha = _alpha;
						}
						
						if( my_config["enable_favstar"] == "Left of Wheel" )
						{
							_alpha =  (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if( _alpha < _partially && my_config["wheel_fadeout"] == "Partially" )
								_alpha = _partially;
							favourite_marker.alpha = _alpha;
						}
					}
				}

				if( elapsed > wheel_fade_ms )
				{
					//So we don't keep doing the loop above when all values have 0 alpha
					stop_fading = true;
				}
			
				if( first_tick == -1 )
					first_tick = ttime;
			}
		}
		fe.add_ticks_callback( "wheel_alpha" );
	}
}

// pulse current wheel logo
if( my_config["wheel_pulse"] != "No" )
{
	local _loop = false;
	if( my_config["wheel_pulse"] == "Loop")
		_loop = true;

	local art = wheel_entries[wheel_count/2].m_obj;
	local art_pulse = fe.add_artwork( "wheel", art.x,art.y,art.width,art.height );
	art.zorder = 1
	if( my_config["wheel_logo_aspect"] == "Yes" )
		art_pulse.preserve_aspect_ratio=true;
	
	local _time = 3000;
	
	local art_scale = {when = Transition.StartLayout, property = "scale", start = 1.0, end = 1.2, time = _time, loop = _loop}
	local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 150, end = 0,	time = _time, loop = _loop}
	animation.add( PropertyAnimation( art_pulse, art_scale ) );
	animation.add( PropertyAnimation( art_pulse, alpha_cfg ) );

	pulse_transition <- function( ttype, var, ttime )
	{
		if( ttype == Transition.ToNewSelection )
		{
			// turn off StartLayout pulse animation when ToNewSelection begins
			if( alpha_cfg.loop == true ) 
			{
				alpha_cfg.start = 0;
				alpha_cfg.loop = false;
				art_scale.loop = false;
			}
			art_pulse.alpha = 0;
		}
		return false;
	}
	fe.add_transition_callback( "pulse_transition" );

	local art_scale2 = {when = Transition.ToNewSelection, property = "scale", start = 1.0, end = 1.2, time = _time, loop = _loop}
	local alpha_cfg2 = {when = Transition.ToNewSelection, property = "alpha", start = 150, end = 0,	time = _time, loop = _loop}
	animation.add( PropertyAnimation( art_pulse, art_scale2 ) );
	animation.add( PropertyAnimation( art_pulse, alpha_cfg2 ) );
		
	stop_pulse <- function( ttime )
	{
		// if there is fadeout, pulse once only
		if( conveyor.m_objs[wheel_count/2].m_obj.alpha == 0 || conveyor.m_objs[wheel_count/2].m_obj.alpha == _partially )
		{
			alpha_cfg.loop = false;
			alpha_cfg2.loop = false;
		}
		else // if no fadeout pulse loop
		{
			alpha_cfg.loop = true;
			alpha_cfg2.loop = true;
			
			if( my_config["wheel_pulse"] == "Once" )
			{
				alpha_cfg.loop = false;
				alpha_cfg2.loop = false;
			}
		}
	}
	fe.add_ticks_callback( "stop_pulse" );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Play sound when transitioning to next / previous game on wheel
//
// Use an array that is loaded outside and only updated inside the transition_callback function 
// in order to prevent a memory leak by calling fe.add_sound() within that function

local random_num;
local sound_name = "";
local Wheelclick = [];
local sid = 0;

for( local i=0; i<10; i++ )
	Wheelclick.push(fe.add_sound(sound_name));

function sound_transitions(ttype, var, ttime) 
{
	if( my_config["enable_random_sound"] != "No" )
	{		
		if( my_config["enable_random_sound"] == "Random" )
		{
			random_num = floor(((rand() % 1000 ) / 1000.0) * 322);
			sound_name = FeConfigDirectory+"gtc-common/sounds/GS"+random_num+".mp3";
		}

		if( my_config["enable_random_sound"] == "Click" )
			sound_name = FeConfigDirectory+"gtc-common/sounds/click.mp3";
			
		if( my_config["enable_random_sound"] == "Arcade Joystick" )
			sound_name = FeConfigDirectory+"gtc-common/sounds/joystick.mp3";
		
		switch( ttype ) 
		{
			case Transition.StartLayout:		
			case Transition.EndNavigation:	
				sid++; // next cell in the array
				if( sid > 9 ) //if reached end of the array go to the beginning
					sid = 0;
				Wheelclick[sid].file_name = sound_name;
				Wheelclick[sid].playing = true;
			break;
		}
	}
	return false;
}
fe.add_transition_callback("sound_transitions");


//////////////////////////////////////////////////////////////////////////////////////////////////
// Flyer art
if( my_config["enable_gcartart"] == "Yes" && my_config["wheel_fadeout"] != "No" )
{
	local x = 0.76;
	local y = 0.39;

	if( my_config["enable_gboxart"] == "No" ) 
	{
		x = 0.68;
		y = 0.42;
	}	

	local flyer = fe.add_artwork( "flyer", flx*2, fly*y, flw*0.206, flh*0.49 );
	flyer.trigger = Transition.EndNavigation;
	flyer.preserve_aspect_ratio = true;
	
	local start_transition1 = { when = Transition.StartLayout, property = "x", start = flx*2, end = flx*x, time = my_delay+600 }
	animation.add( PropertyAnimation( flyer, start_transition1 ) );

	art_transition_flyer <- function( ttype, var, ttime )
	{
		if( ttype == Transition.EndNavigation )
			flyer.alpha = 255;

		if( ttype == Transition.ToNewSelection )
			flyer.alpha = 0;

		return false;
	}
	fe.add_transition_callback( "art_transition_flyer" );

	local move_transition2 = { when = Transition.EndNavigation, property = "x", start = flx*2, end = flx*x, time = my_delay+600 }
	animation.add( PropertyAnimation( flyer, move_transition2 ) );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Boxart
if( my_config["enable_gboxart"] == "Yes" )
{
	local x = 0.6 * flw;
	local y_adjust_factor = 1.2;
	if( my_config["wheel_fadeout"] == "No")
	{
		x = 0;
	}

	local w = 0.15 * flw;
	if (aspect_ratio < 1) // portrait
	{
		w = 0.15 * flh;
		y_adjust_factor = 1.4;
	}
		
	local boxart_aspect = 1.5; // images normally 582x889, so height is approximately width * 1.5
	local h = w * boxart_aspect;

	local y_start = 2 * flh;
	local y_end = flh - (h * y_adjust_factor);

	if( my_config["enable_gcartart"] == "No" && my_config["wheel_fadeout"] != "No" )
	{
		x = 0.7 * flw;
	}
	else if (resized_cab_y > 0)
	{
		// use w rather than h for position because boxart preserves aspect ratio
		local top_boxart = resized_cab_y - h;
		if (top_boxart > 0)
		{
			// if cabinet is not full-height and there is available space above,
			// position art at top instead of bottom
			y_start = -flh;
			y_end = top_boxart;
		}
	}

	local boxart = fe.add_artwork( "boxart", x, y_end, w, h );
	boxart.trigger = Transition.EndNavigation;

	if( my_config["wheel_fadeout"] == "No" )
		boxart.preserve_aspect_ratio = true;
	else
		boxart.preserve_aspect_ratio = false;

	local start_transition1 = {	when = Transition.StartLayout, property = "y", start = y_start, end = y_end, time = my_delay+200 }
	animation.add( PropertyAnimation( boxart, start_transition1 ) );

	local move_transition2 = { when = Transition.EndNavigation, property = "y", start = y_start, end = y_end, time = my_delay+200 }
	animation.add( PropertyAnimation( boxart, move_transition2 ) );		

	art_transition <- function( ttype, var, ttime )
	{
		if( ttype == Transition.EndNavigation )
			boxart.alpha = 255;

		if( ttype == Transition.ToNewSelection )
			boxart.alpha = 0;

		return false;
	}
	fe.add_transition_callback( "art_transition" );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Shader - Screen Glow
// check if GLSL shaders are available on this system
if( my_config["enable_crt_screenglow"] != "No" && ShadersAvailable == 1 )
{
	// shadow parameters
	local shadow_radius = flw;
	local shadow_alpha = 255;
	local shadow_downsample = 0;
	local shadow_size = 1.0; // multiplies the screen size that is used as a basis for the blurred shadow

	if (my_config["enable_crt_screenglow"] == "Light")
	{
		shadow_downsample = 0.04;
		shadow_size = 1.0;
	}
	else if (my_config["enable_crt_screenglow"] == "Medium")
	{
		shadow_downsample = 0.03;
		shadow_size = 1.4;
	}
	else if (my_config["enable_crt_screenglow"] == "Strong")
	{
		shadow_downsample = 0.02;
		shadow_size = 1.8;
	}

	// determine actual snap coordinates (after cabinet resize/reposition)
	local actual_snap_x = resized_cab_x + (snap_x * resized_w_ratio);
	local actual_snap_y = resized_cab_y + (snap_y * resized_h_ratio);
	local actual_snap_w = snap_w * resized_w_ratio;
	local actual_snap_h = snap_h * resized_h_ratio;
	
	// creation of first surface with safeguards area
	local glow_w = actual_snap_w + (2 * shadow_radius);
	local glow_h = actual_snap_h + (2 * shadow_radius);
	local xsurf1 = fe.add_surface(shadow_downsample * glow_w, shadow_downsample * glow_h);

	// add a clone of the picture to topmost surface
	local pic1 = xsurf1.add_clone(snap);
	pic1.set_pos(shadow_radius*shadow_downsample, shadow_radius*shadow_downsample);

	// creation of second surface
	local xsurf2 = fe.add_surface(xsurf1.width, xsurf1.height);

	// nesting of surfaces
	xsurf1.visible = false;
	xsurf1 = xsurf2.add_clone(xsurf1);
	xsurf1.visible = true;

	// define and apply blur shaders
	local blursizex = 1.0 / xsurf2.width;
	local blursizey = 1.0 / xsurf2.height;
	local kernelsize = shadow_downsample * (shadow_radius * 2) + 1;
	local kernelsigma = shadow_downsample * shadow_radius * 0.3;

	local shaderH1 = fe.add_shader(Shader.Fragment, fe.script_dir + "gauss_kernsigma_o.glsl");
	shaderH1.set_texture_param("texture");
	shaderH1.set_param("kernelData", kernelsize, kernelsigma);
	shaderH1.set_param("offsetFactor", blursizex, 0.0);
	xsurf1.shader = shaderH1;

	local shaderV1 = fe.add_shader(Shader.Fragment, fe.script_dir + "gauss_kernsigma_o.glsl");
	shaderV1.set_texture_param("texture");
	shaderV1.set_param("kernelData", kernelsize, kernelsigma);
	shaderV1.set_param("offsetFactor", 0.0, blursizey);
	xsurf2.shader = shaderV1;

	// apply black color and alpha channel to shadow
	pic1.alpha = shadow_alpha;
	pic1.width = shadow_size * actual_snap_w * shadow_downsample;
	pic1.height = shadow_size * actual_snap_h * shadow_downsample;

	// reposition and upsample shadow surface stack
	local shadow_xoffset = (1 - shadow_size) * actual_snap_w / 2;
	local shadow_yoffset = (1 - shadow_size) * actual_snap_h / 2;
	xsurf2.set_pos(actual_snap_x - shadow_radius + shadow_xoffset, actual_snap_y - shadow_radius + shadow_yoffset, glow_w, glow_h);
}

//////////////////////////////////////////////////////////////////////////////////////////////////
// Game info background frame
local line_count = 1;
local line_h = fly * 0.06;
local line_padding = -fly * 0.02; // negative padding to make the lines closer together
local title_line_y = fly - line_h;
local details_line_y = title_line_y;

if (aspect_ratio < 1)
{
	// switch to two lines in portrait mode
	line_count += 1;
	title_line_y -= (line_h + line_padding);
}

if( my_config["enable_frame"] == "Yes" )
{
	local frame_h = line_count * line_h + ((line_count - 1) * line_padding);
	local frame = fe.add_image( FeConfigDirectory+"gtc-common/art/arcade/frame.png", 0, title_line_y, flw, frame_h );
	frame.alpha = 255;

	if( my_config["enable_ini_anim"] == "Yes" )
	{
		local start_transition1 = { when = Transition.StartLayout, property = "y", start = fly*2, end = title_line_y, time = ini_anim_time }
		animation.add( PropertyAnimation( frame, start_transition1 ) );
	}
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Favourite marker for "With Game Info" setting, separated from "Left to Wheel" 
// to avoid zorder issues
if( my_config["enable_favstar"] == "With Game Info" )
{
	local x = flx*0.07;
	local y = fly*0.95;
	local wh = flw*0.022;
	
	favourite_marker = fe.add_image( "[!FavStar]",x, y, wh, wh );
	favourite_marker.mipmap = true;
	
	if( my_config["enable_ini_anim"] == "No" )
	{
		// fade in if startup animation is set to No
		local alpha_cfg = {	when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2) }
		animation.add( PropertyAnimation( favourite_marker, alpha_cfg ) );
	}
	else
	{
		// animate with game info
		local move_transition_year = { when = Transition.StartLayout, property = "x", start = flx*-2, end = x, time = (ini_anim_time+350) }
		animation.add( PropertyAnimation( favourite_marker, move_transition_year ) );
	}
}	


//////////////////////////////////////////////////////////////////////////////////////////////////
// Game info
function Manufacturer_Name( ioffset )
{
	local name = fe.game_info( Info.Manufacturer, ioffset );
	if( name.len() > 0 ) 
	{
		name = split( name, "(" )[0]; // shorten the manufacturer name when one of the followig characters exist
		name = split( name, "[" )[0];
		name = split( name, "/" )[0];
		name = split( name, "," )[0];
		name = split( name, "?" )[0];
		
		name = strip( name ); // remove white-space-only from the beginning or end of the manufacturer name
	}
	return name;
}

if( my_config["enable_gameinfo"] != "No" )
{
	local year = "";
	local title = "";
	local filter = "";
	local x_year = flx*0.0;
	local x_title = flx*0.11;
	local x_filter = flx*0.6;
	local font_size = flh*0.028;
	local text_w = flw * 0.7; // generic width for block of text
	
	// Year
	year = fe.add_text( "[Year]", x_year, details_line_y, text_w, line_h );
	year.align = Align.Left;
	year.charsize = font_size;
	year.set_rgb(255, 120, 0);

	// Title
	if( my_config["enable_game_manu"] == "Title Only" )
		title = fe.add_text( "[Title]", x_title, title_line_y, flw, line_h );
	else
	{
		formatted_text <- function()
		{
			local m = Manufacturer_Name(0);
			local t = "[Title]";

			if( ( m.len() > 0 ) && ( t.len() > 0 ) )
				return m + ",  " + t;

			return t;
		}
		if (line_count > 1)
			x_title = 0;
		title = fe.add_text( "[!formatted_text]", x_title, title_line_y, flw, line_h );
	}
	title.align = Align.Left;
	title.charsize = font_size;
	title.set_rgb(255, 120, 0);
	
	if( my_config["enable_gameinfo"] == "Info and Enumerate" )
	{  
		// Current game out of total number of games
		filter = fe.add_text( "Game: [ListEntry]/[ListSize]", x_filter, details_line_y, flx * 0.4, line_h );
		filter.align = Align.Right;
		filter.charsize = font_size-4;
		filter.set_rgb(255, 120, 0);
	}

	if( ShadersAvailable == 1 )
	{
		local shader = fe.add_shader( Shader.Fragment "shaders/bloom_shader_text.frag" );
		shader.set_texture_param("bgl_RenderedTexture"); 
		if( year != "" )
			year.shader = shader;
		if( title != "" )
			title.shader = shader;
		if( filter != "" )
			filter.shader = shader;
	}
	
	// random color for info text
	if( my_config["enable_colors"] == "Yes" )
	{
		brightrand <- function() {
			return 255-(rand()/255);
		}

		local red, green, blue;
		
		// Color Transitions
		fe.add_transition_callback( "color_transitions" );
		color_transitions <- function( ttype, var, ttime ) {
			switch( ttype )
			{
				case Transition.StartLayout:
				case Transition.ToNewSelection:
					red = brightrand();
					green = brightrand();
					blue = brightrand();
					if( filter != "" )
						filter.set_rgb(red, green, blue);
					if( year != "" )
						year.set_rgb(red, green, blue);
					if( title != "" )
						title.set_rgb(red, green, blue);
				break;
			}
			return false;
		}
	}
	
	// fade in game info if the startup animation is disabled
	if( my_config["enable_ini_anim"] == "No" )
	{
		local alpha_cfg = {	when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = ini_anim_time*2 }

		animation.add( PropertyAnimation( year, alpha_cfg ) );
		animation.add( PropertyAnimation( title, alpha_cfg ) );
		
		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
			animation.add( PropertyAnimation( filter, alpha_cfg ) );
	}

	// animate game info
	if( my_config["enable_ini_anim"] == "Yes" )
	{
		local move_transition_year = { when = Transition.StartLayout, property = "x", start = flx*-2, end = x_year, time = ini_anim_time+350 }
		animation.add( PropertyAnimation( year, move_transition_year ) );

		// title
		local move_transition_title = {	when = Transition.StartLayout, property = "x", start = flx*-2, end = x_title, time = ini_anim_time+350 }
		animation.add( PropertyAnimation( title, move_transition_title ) );
		
		// filter
		if( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			local move_transition_title = {	when = Transition.StartLayout, property = "x", start = flx*2, end = x_filter, time = ini_anim_time+350 }
			animation.add( PropertyAnimation( filter, move_transition_title ) );
		}
	}
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Letters
local trigger_letter = false;
local letter_x = 0.5;	
local letters = fe.add_image( "", flw * letter_x - (flw*0.140 * 0.5), flh * 0.5 - (flh*0.280 * 0.5), flw*0.140, flh*0.280 );

fe.add_transition_callback( "letter_transition" );
function letter_transition( ttype, var, ttime )
{	
	if(ttype == Transition.ToNewList)
		rtime = glob_time;
}

fe.add_ticks_callback( "letter_tick" );
function letter_tick( ttime )
{
	glob_time = ttime;

	if( glob_time - rtime > glob_delay )
		letters.visible = false; // hide letter search if present
	
    if( trigger_letter == true )
	{
		local firstl = fe.game_info(Info.Title);
		/*if(fe.filters[fe.list.filter_index].sort_by == Info.Manufacturer)
			firstl = fe.game_info(Info.Manufacturer);*/

		if( my_config["letters_type"] != "No" )
		{
			if( my_config["letters_type"] == "Default" )
				letters.file_name = FeConfigDirectory + "gtc-common/letters/default/" + firstl.slice(0,1).tolower() + ".png";
			else  //by system display name
				letters.file_name = FeConfigDirectory + "gtc-common/letters/" + fe.displays[fe.list.display_index].name + "/" + firstl.slice(0,1).tolower() + ".png";

			letters.visible = true;
		}
		trigger_letter = false;
    }
}

fe.add_signal_handler( this, "on_signal" )
function on_signal( str ) 
{
	switch( str ) 
	{
		case "next_letter":
		case "prev_letter":
			rtime = glob_time;
			trigger_letter = true;
		break;
	}

    return false;
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// Search
local search_surface = fe.add_surface( fe.layout.width *1.12 , fe.layout.height * 1.6 );
KeyboardSearch(search_surface)
	.keys_pos([ 0.05, 0.45, 0.9, 0.4 ])
	.search_key( my_config["user_search_key"].tolower() )
	.mode( "show_results" )
	.text_font("BebasNeue Bold")
	.bg_color(0,0,0,210)
	.text_color(0,255,0)
	.keys_selected_color(0,255,0)
	.init()

if( my_config["user_search_boxsize"] == "Large" )
	search_surface.set_pos( 0, 0, flw, flh ); // Large center
else
	search_surface.set_pos( flx*0.15, fly*0.23, flw*0.680, flh*0.58 ); // Small center


//////////////////////////////////////////////////////////////////////////////////////////////////
// System games count
main_infos <- {};
if( !file_exist(FeConfigDirectory + "gtc.stats") ) 
{
	fe.overlay.splash_message ("Counting games, please wait...")
	print("Created the gtc.stats file!\n");
	refresh_stats();
}
main_infos <- LoadStats();

function system_stats( ttype, var, ttime )
{
	local curr_sys;
	if( ttype == Transition.StartLayout )
	{
		curr_sys = fe.list.name;
		
		if( fe.filters[fe.list.filter_index].name.tolower() == "all" )  //make sure default filter ("all") is on so all games are counted
		{
			if( main_infos.rawin(curr_sys) )  //check if system exists
			{				
				if( fe.list.size != main_infos[curr_sys].cnt )  //if count is wrong, update it with current system list size
				{
					main_infos[curr_sys].cnt = fe.list.size;
					SaveStats(main_infos);
					print("Updated number of games for " + curr_sys + "\n");
				}
			}
			else  //if system is new and does not exist in the gtc.stats file, create new entry and count
			{
				main_infos <- refresh_stats(curr_sys);
				print("Created new entry for " + curr_sys + " and counted games for it" + "\n");
			}
		}
	}
	return false;
}
fe.add_transition_callback( "system_stats" );
