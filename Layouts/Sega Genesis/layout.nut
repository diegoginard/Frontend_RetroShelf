////////////////////////////////////////////////////////////////////////////////////////////////////////
/* Sega Genesis theme v10.3.2

███████╗███████╗ ██████╗  █████╗      ██████╗ ███████╗███╗   ██╗███████╗███████╗██╗███████╗
██╔════╝██╔════╝██╔════╝ ██╔══██╗    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝██║██╔════╝
███████╗█████╗  ██║  ███╗███████║    ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ███████╗██║███████╗
╚════██║██╔══╝  ██║   ██║██╔══██║    ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ╚════██║██║╚════██║
███████║███████╗╚██████╔╝██║  ██║    ╚██████╔╝███████╗██║ ╚████║███████╗███████║██║███████║
╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝╚══════╝

Design, Code and Art by Yaron2019

'coordinates table for different screen aspects' code adapted from nevato theme
Letters and 'System games count' code adapted from pcca theme */
////////////////////////////////////////////////////////////////////////////////////////////////////////   

local orderx = 0;
local divider = "----"

class UserConfig {
	</ label="Enable startup animations", help="Enable system animation when layout starts", options="Yes,No", order=orderx++ /> enable_ini_anim="Yes";
	</ label="Startup animation transition time", 
		help="animation time in ms", 
		options="500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000",
		order=orderx++
		/>ini_anim_trans_ms="1000";
	</ label="Select background image", help="Select backroung image", options="Sega,Black Mesh,Sonic Green Hill Zone", order=orderx++ /> select_bg_img="Sonic Green Hill Zone";
	</ label="Enable background scanlines", help="Show scanline effect on background image", options="None,Light,Medium,Dark", order=orderx++ /> enable_scanline="None";
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx1 = " "

	</ label="Type of wheel", help="Select round wheel or vertical wheel", options="Round,Vertical", order=orderx++ /> wheel_type="Round";
	</ label="Size of wheel logos", help="Use smaller or larger wheel logos", options="Smaller,Larger", order=orderx++ /> wheel_logo_size="Larger";
	</ label="Preserve wheel logo's aspect ratio", help="Preserve the original aspect ratio of the wheel logos, great for vertical wheel mode", options="Yes,No", order=orderx++ /> wheel_logo_aspect="No";
	</ label="Enable wheel logos mipmap", help="Mipmap reduces aliasing artifacts (jagged edges) for high resolution wheel logos", options="Yes,No", order=orderx++ /> wheel_logo_mipmap="No";
	</ label="Adjust wheel position", help="Adjust wheel position closer to or further from the right side of the screen", options="Adjust Left,Adjust Right", order=orderx++ /> wheel_poisition="Adjust Left";																										
	</ label="Enable semitransparent wheel", help="Semitransparent or fully opaque wheel logos", options="Yes,No", order=orderx++ /> wheel_semi_t="No";
	</ label="Number of wheel slots", 
		help="Number of slots in the wheel", 
		options="4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80",
		order=orderx++
		/>wheels="10";
	</ label="Wheel transition time", 
		help="Time in milliseconds for wheel spin", 
		options="1,25,50,75,100,125,150,175,200",
		order=orderx++
		/>transition_ms="25";
	</ label="Enable wheel fadeout", help="Enable wheel fadeout", options="No,Completely,Partially", order=orderx++ /> wheel_fadeout="No";
	</ label="Fade wheel time", help="Fade wheel time", options="500,1000,2000,3000", order=orderx++ /> wheel_fade_ms="500"; 
	</ 	label			= "Delay time",
		help			= "The time (in milliseconds) it takes to start hiding the wheel and pointer",
		options			= "500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000",
		order			= orderx++
	/> 	set_ms_delay	= "1250";	
	</ label="Enable wheel pulse", help="Animate a pulse of the current wheel logo - will pulse only once if wheel fadeout is enabled", options="No,Once,Loop", order=orderx++ /> wheel_pulse="Once";
	</ label="Enable wheel background", help="Show wheel background texture", options="Yes,No", order=orderx++ /> enable_wl_bg="No";
	</ label="Enable wheel sounds", help="Play sounds when navigating games wheel", options="No,Random,Click", order=orderx++ /> enable_random_sound="Random"; 
	</ label="Show wheel pointer", help="Show animated wheel pointer", options="Yes,No", order=orderx++ /> enable_pointer="Yes"; 
	</ label="Enable Letters", 
		help="Show graphical letters on the screen when pressing the wheel's 'Next Letter' or 'Previous Letter' hotkeys set in the Controls menu.\n 'System Display Name' option will seek the letters in a folder identical to the current system display name (attract/letters/mame for example).", 
		options="No,Default,By System Display Name", order=orderx++ /> letters_type="Default";
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx2 = " "

	</ label="Enable CRT scanlines", help="Show CRT scanlines", options="None,Light,Medium,Dark", order=orderx++ /> enable_crt_scanline="Light";
	</ label="Enable CRT bloom shader effect", help="Creates a bloom effect for the snap video, if device is able to run GLSL shaders", options="Yes,No", order=orderx++ /> enable_bloom="No";
	</ label="Mute game snap videos", help="Mute game snap videos", options="Yes,No", order=orderx++ /> mute_videos="No"; 
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx3 = " "

	</ label="Show game box art", help="Shows the current game box art if available", options="Yes,No", order=orderx++ /> enable_gboxart="Yes";
	</ label="Show game cart art", help="Shows the current game cart art if available", options="Yes,No", order=orderx++ /> enable_gcartart="Yes";
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx4 = " "

	</ label="Show game information", help="Show game info", options="No,Info,Info and Enumerate", order=orderx++ /> enable_gameinfo="Info and Enumerate";
	</ label="Game name", help="Show game title only or manufacturer and game title. If there is no manufacturer name in the romlist, only the game title will be shown.", 
		options="Title Only,Manufacturer and Title", order=orderx++ /> enable_game_manu="Title Only";
	</ label="Enable random text colors", help="Enable game info random text colors", options="Yes,No", order=orderx++ /> enable_colors="No";
	</ label="Enable text frame", help="Show frame to make game info text standout ", options="Yes,No", order=orderx++ /> enable_frame="Yes"; 
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx5 = " "

	</ label="Mark favourite games", help="Mark favourite games with an icon to the left of the wheel logo or at the bottom with the game info", options="No,Left of Wheel,With Game Info", order=orderx++ /> enable_favstar="With Game Info";
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx6= " "

	</ label="Search key", help="Choose the key to initiate a search", options="Custom1,Custom2,Custom3,Custom4,Custom5,Custom6", order=orderx++ /> user_search_key="Custom1";
	</ label="Search box size", help="Choose size of the search box", options="Small,Large", order=orderx++ /> user_search_boxsize="Small";
	</ label= divider, help=" ", options = " ", order=orderx++ /> paramxx7 = " "
}  


local my_config = fe.get_config();
fe.layout.font="NiseGenesis";

// modules
fe.load_module( "animate" );
fe.load_module( "fade" );
fe.load_module("file");
fe.load_module("file-format");
fe.load_module("gtc");
fe.load_module("gtc-pas");
fe.load_module("gtc-kb");

local ini_anim_time;
try { ini_anim_time =  my_config["ini_anim_trans_ms"].tointeger(); } catch ( e ) { }

// initialize wheel delay time
my_delay <- 0;
try {my_delay = my_config["set_ms_delay"].tointeger();} catch(e) {}
my_play <- my_delay;

// Letters ini
local rtime = 0;
local glob_time = 0;
local glob_delay;
try { glob_delay =  my_config["set_ms_delay"].tointeger(); } catch ( e ) { }
if ( glob_delay > 750 )
	glob_delay = 750;

//coordinates table for different screen aspects -- Start
local settings = {
   "default": { 
   //16x9 is default
      aspectDepend = { 
        res_x = 2133,
        res_y = 1200,
        maskFactor = 1.9}
   },
   "16x10": {
      aspectDepend = { 
        res_x = 1920,
        res_y = 1200,
        maskFactor = 1.9}
   },
    "16x9": {
      aspectDepend = { 
        res_x = 1920,
        res_y = 1080,
        maskFactor = 1.9}
   },
   "4x3": {
      aspectDepend = { 
        res_x = 1600,
        res_y = 1200,
        maskFactor = 1.6}
   }
   "5x4": {
      aspectDepend = { 
        res_x = 1500,
        res_y = 1200,
        maskFactor = 1.6}
   }
}

local aspect = fe.layout.width / fe.layout.height.tofloat();
local aspect_name = "";
switch( aspect.tostring() )
{
    case "1.77865":  //for 1366x768 screen
    case "1.77778":  //for any other 16x9 resolution
        aspect_name = "16x9";
        break;
    case "1.6":
        aspect_name = "16x10";
        break;
    case "1.33333":
        aspect_name = "4x3";
        break;
    case "1.25":
        aspect_name = "5x4";
        break;
    case "0.75":
        aspect_name = "3x4";
        break;
}
print("Attract-Mode Version: " + FeVersion + "\n" + "Screen aspect ratio: "+aspect_name+"\n" + "Resolution: "+ScreenWidth+"x"+ScreenHeight+"\n" + "Shader GLSL available: "+ShadersAvailable+"\n" + "OS: "+OS+"\n");

function Setting( id, name )
{
    if ( aspect_name in settings && id in settings[aspect_name] && name in settings[aspect_name][id] )
  {
    ::print("\tusing settings[" + aspect_name + "][" + id + "][" + name + "] : " + settings[aspect_name][id][name] + "\n" );
    return settings[aspect_name][id][name];
  } else if ( aspect_name in settings == false )
  {
    ::print("\tsettings[" + aspect_name + "] does not exist\n");
  } else if ( name in settings[aspect_name][id] == false )
  {
    ::print("\tsettings[" + aspect_name + "][" + id + "][" + name + "] does not exist\n");
  }
  ::print("\t\tusing default value: " + settings["default"][id][name] + "\n" );
  return settings["default"][id][name];
}

fe.layout.width = Setting("aspectDepend", "res_x");
fe.layout.height = Setting("aspectDepend", "res_y");

local flx = fe.layout.width;
local fly = fe.layout.height;
local flw = fe.layout.width;
local flh = fe.layout.height;

local mask_factor = Setting("aspectDepend", "maskFactor");

//coordinates table for different screen aspects -- End


/////////////////////////////////////////////////////////////////////////////////
// load background art
local bg_img = my_config["select_bg_img"];
local bg = FadeArt( bg_img, 0, 0, flw, flh );
bg.zorder = -15;

//scanline effect overlay for background art
local bg_scanline;
if ( my_config["enable_scanline"] != "None" )
{
	local scanlines = FeConfigDirectory+"gtc-common/art/scanlines_1920.png"
	if (ScreenWidth < 1920)
		scanlines = FeConfigDirectory+"gtc-common/art/scanlines_720.png"
		
	bg_scanline = fe.add_image( scanlines, 0, 0, flw, flh );
	bg_scanline.preserve_aspect_ratio = false;

	if ( my_config["enable_scanline"] == "Light" )
		bg_scanline.alpha = 30;
	else if ( my_config["enable_scanline"] == "Medium" )
		bg_scanline.alpha = 80;
	else if ( my_config["enable_scanline"] == "Dark" )
		bg_scanline.alpha = 150;

	bg_scanline.zorder = -14;
}


/////////////////////////////////////////////////////////////////////////////////
// Video snap and static

// static effect if no snap video available
local snapbg = fe.add_image(FeConfigDirectory+"gtc-common/videos/static.mp4", flx*0.049, fly*0.189, flw*0.322, flh*0.44);
snapbg.zorder = -13;
if ( my_config["enable_ini_anim"] == "Yes" )
{
	// animate static effect entry when layout starts
	local move_transition1 = {when = Transition.StartLayout, property = "x", start = flx*-1.36,	end = flx*0.049, tween = "cubic", time = ini_anim_time}
	animation.add( PropertyAnimation( snapbg, move_transition1 ) );
}

// add current game snap video
local snap = fe.add_artwork("snap", flx*0.049, fly*0.189, flw*0.322, flh*0.44);
snap.trigger = Transition.EndNavigation;
snap.preserve_aspect_ratio = false;
snap.zorder = -12;

if ( my_config["mute_videos"] == "Yes" )
	snap.video_flags = Vid.NoAudio;

if ( my_config["enable_ini_anim"] == "Yes" )
{
	// animate snap entry when layout starts
	local move_transition1 = {when = Transition.StartLayout, property = "x", start = flx*-1.36,	end = flx*0.049, tween = "cubic", time = ini_anim_time}
	animation.add( PropertyAnimation( snap, move_transition1 ) );
}

// bloom shader 
if ( my_config["enable_bloom"] == "Yes" && ShadersAvailable == 1)
{
    local sh = fe.add_shader( Shader.Fragment, "bloom_shader.frag" );
	sh.set_texture_param("bgl_RenderedTexture"); 
	snap.shader = sh;
}


/////////////////////////////////////////////////////////////////////////////////
// crt scanline
local scanline;
if ( my_config["enable_crt_scanline"] != "None" )
{
	local scanlines = FeConfigDirectory+"gtc-common/art/scanlines_1920.png"
	if (ScreenWidth < 1920)
		scanlines = FeConfigDirectory+"gtc-common/art/scanlines_640.png"

	scanline = fe.add_image( scanlines, flx*0.049, fly*0.189, flw*0.322, flh*0.44 );
	scanline.preserve_aspect_ratio = false;
	
	if ( my_config["enable_crt_scanline"] == "Light" )
		scanline.alpha = 30;
	else if ( my_config["enable_crt_scanline"] == "Medium" )
		scanline.alpha = 60;
	else if ( my_config["enable_crt_scanline"] == "Dark" )
		scanline.alpha = 150;

	scanline.zorder = -11;

	if ( my_config["enable_ini_anim"] == "Yes" )
	{
		// animate crt scanline when layout starts
		local move_transition1 = {when = Transition.StartLayout, property = "x", start = flx*-1.36, end = flx*0.049, tween = "cubic",time = ini_anim_time}
		animation.add( PropertyAnimation( scanline, move_transition1 ) );
	}
}


/////////////////////////////////////////////////////////////////////////////////
// art images
local art_x = flx*1.5;
local logo_y = fly*-1;
if ( my_config["enable_ini_anim"] == "No" )
{
	art_x = 0;
	logo_y = 0;
}

local tv = fe.add_image( "tv.png", 0, 0, flw, flh );
tv.zorder = -10;
if ( my_config["enable_ini_anim"] == "Yes" )
{
	// animate art images when layout starts
	local move_transition1 = { when = Transition.StartLayout, property = "x", start = flx*-1.5, end = flx*0.0, tween = "cubic", time = ini_anim_time }
	animation.add( PropertyAnimation( tv, move_transition1 ) );
}

local sonic;
if ( my_config["enable_ini_anim"] == "Yes" )
{
	sonic = PanAndScanImage( "sonic.png", flx*3, 0, flw, flh);
	sonic.trigger = Transition.EndNavigation;
	sonic.preserve_aspect_ratio = false;
	sonic.set_fit_or_fill("fit");
	sonic.set_anchor(::Anchor.Bottom);
	sonic.set_zoom(0, 0);
	sonic.set_animate(::AnimateType.Bounce, 0.2, 0.15)
	sonic.set_start_scale(1.02);
	
	local move_transition2 = { when = Transition.StartLayout, property = "x", start = flx*3, end = flx*0.0, delay = 1000, tween = "circle", time = ini_anim_time }
	animation.add( PropertyAnimation( sonic, move_transition2 ) );
}
else
	sonic = fe.add_image( "sonic.png", art_x, 0, flw, flh );
sonic.zorder = -9;


local console = fe.add_image( "console.png", 0, 0, flw, flh );
console.zorder = -8;
if ( my_config["enable_ini_anim"] == "Yes" )
{
	local move_transition3 = { when = Transition.StartLayout, property = "y", start = fly*1, end = fly*0, tween = "cubic", time = ini_anim_time }
	animation.add( PropertyAnimation( console, move_transition3 ) );
}

local logo = fe.add_image( "logo.png", 0, logo_y, flw, flh );
logo.zorder = -7;
if ( my_config["enable_ini_anim"] == "Yes" )
{
	local move_transition4 = { when = Transition.StartLayout, property = "y", start = fly*-1, end = fly*0, tween = "circle", delay = ini_anim_time, time = ini_anim_time }
	animation.add( PropertyAnimation( logo, move_transition4 ) );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
//Cartart
if ( my_config["enable_gcartart"] == "Yes" )
{
	local y = 0.54;
	
	local cartart = fe.add_artwork("cartart", flx*0.443, fly*-2.1, flw*0.125, flh*0.25 );
	cartart.trigger = Transition.EndNavigation;
	cartart.preserve_aspect_ratio = true;

	local start_transition1 = {when = Transition.StartLayout, property = "y", start = fly*-2.1,	end = fly*y, tween = "cubic", delay = ini_anim_time*0.5, time = ini_anim_time+500}
	animation.add( PropertyAnimation( cartart, start_transition1 ) );
	
	function cartart_transition( ttype, var, ttime )
	{
		if ( ttype == Transition.EndNavigation )
			cartart.alpha = 255;

		if ( ttype == Transition.ToNewSelection )
			cartart.alpha = 0;
		
		return false;
	}
	fe.add_transition_callback( "cartart_transition" );
	
	local move_transition1 = {when = Transition.EndNavigation, property = "y",	start = fly*-2.1, end = fly*y, tween = "cubic",	time = ini_anim_time+500}
	animation.add( PropertyAnimation( cartart, move_transition1 ) );
}


//////////////////////////////////////////////////////////////////////////////////////////////////
// console cover
local console_cover = fe.add_image( "console_cover.png", 0, 0, flw, flh );
if ( my_config["enable_ini_anim"] == "Yes" )
{
	// animate console_cover image when layout starts
	local move_transition1 = {when = Transition.StartLayout, property = "y", start = fly*1,	end = fly*0, tween = "cubic", time = ini_anim_time}
	animation.add( PropertyAnimation( console_cover, move_transition1 ) );
}


/////////////////////////////////////////////////////////////////////////////////
// wheel background
local wheel_art;
local wheel_art_alpha=255;
if ( my_config["enable_wl_bg"] == "Yes" )
{
	// Large is default
	local round_x = 0;
	local round_w = flw;
	local vertical_x = flx*0.1;
	local vertical_w = flw*0.8;
	
	if ( my_config["wheel_poisition"] == "Adjust Right" )
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
		{
			round_x = flx*0.05;
			vertical_x = flx*0.17;
		}
		else //smaller
		{
			round_x = flx*0.27;	
			round_w = flw*0.75;
			vertical_x = flx*0.23;
			vertical_w = flw*0.71;
		}
	}
	if ( my_config["wheel_poisition"] == "Adjust Left" )
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
		{
			round_x = flx*0;
			vertical_x = flx*0.13;
		}
		else //smaller
		{
			round_x = flx*0.2;	
			round_w = flw*0.77;
			vertical_x = flx*0.2;	
			vertical_w = flw*0.7;
		}
	}

	if ( my_config["wheel_type"] == "Round" )
		wheel_art = fe.add_image( FeConfigDirectory+"gtc-common/art/wheel_art.png", round_x, 0, round_w, flh );
	else
		wheel_art = fe.add_image( FeConfigDirectory+"gtc-common/art/wheel_vert.png", vertical_x, 0, vertical_w, flh );
}


/////////////////////////////////////////////////////////////////////////////////
// Pointers
local pointer; 

if ( my_config["enable_pointer"] == "Yes") 
{
	local start_x = 0.91;
	local end_x = 0.87;
	
	if ( my_config["wheel_poisition"] == "Adjust Right" )
	{
		start_x = 0.915;
		end_x = 0.89;
	}
		
	pointer = fe.add_image("pointers/default.png", flx*start_x, fly*0.34, flw*0.2, flh*0.35);
	pointer.preserve_aspect_ratio = true;

	local movex_cfg = {	when = Transition.ToNewSelection, property = "x", start = flx*end_x, end = pointer.x, time = 200 }	
	animation.add( PropertyAnimation( pointer, movex_cfg ) );
}


/////////////////////////////////////////////////////////////////////////////////
// Wheels
fe.load_module( "conveyor" );

local wheel_count;
try { wheel_count = my_config["wheels"].tointeger(); } catch ( e ) { }

local _partially = 30;
local _alpha;
local wheel_x;
local wheel_y;
local wheel_w;
local wheel_a;
local wheel_h;
local wheel_r;
local num_arts;

// Round wheel
if ( my_config["wheel_type"] == "Round" )
{
	if ( my_config["wheel_poisition"] == "Adjust Left" )
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
			wheel_x = [ flx*0.80, flx*0.795, flx*0.756, flx*0.725, flx*0.70, flx*0.68, flx*0.63, flx*0.68, flx*0.70, flx*0.725, flx*0.756, flx*0.76, ]; 
		else //smaller
			wheel_x = [ flx*0.85, flx*0.850, flx*0.801, flx*0.775, flx*0.75, flx*0.73, flx*0.68, flx*0.73, flx*0.75, flx*0.775, flx*0.8006, flx*0.81, ]; 
	}
	else //adjust right
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
			wheel_x = [ flx*0.85, flx*0.845, flx*0.806, flx*0.775, flx*0.75, flx*0.730, flx*0.68, flx*0.73, flx*0.75, flx*0.775, flx*0.806, flx*0.81, ]; 
		else //smaller
			wheel_x = [ flx*0.90, flx*0.895, flx*0.856, flx*0.825, flx*0.80, flx*0.780, flx*0.73, flx*0.78, flx*0.80, flx*0.825, flx*0.856, flx*0.86, ]; 
	}
	wheel_y = [ -fly*0.22, -fly*0.105, fly*0.0, fly*0.105, fly*0.215, fly*0.325, fly*0.436, fly*0.61, fly*0.72 fly*0.83, fly*0.935, fly*0.99, ];
	if ( my_config["wheel_logo_size"] == "Larger" )
		wheel_w = [ flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.28, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, ];
	else //smaller
		wheel_w = [ flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.19, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, ];
	if ( my_config["wheel_semi_t"] == "Yes" )
		wheel_a = [  80,  80,  80,  80,  80,  80, 255,  80,  80,  80,  80,  80, ];
	else
		wheel_a = [  255,  255,  255,  255,  255,  255, 255,  255,  255,  255,  255,  255, ];
	wheel_h = [  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11, flh*0.168,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11, ];
	wheel_r = [  30,  25,  20,  15,  10,   5,   0, -10, -15, -20, -25, -30, ];
}
else // Vertical wheel
{
	if ( my_config["wheel_poisition"] == "Adjust Left" )
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
			wheel_x = [ flx*0.72, flx*0.72, flx*0.72, flx*0.72, flx*0.72, flx*0.72, flx*0.685, flx*0.72, flx*0.72, flx*0.72, flx*0.72, flx*0.72, ]; 
		else //smaller
			wheel_x = [ flx*0.74, flx*0.74, flx*0.74, flx*0.74, flx*0.74, flx*0.74, flx*0.70, flx*0.74, flx*0.74, flx*0.74, flx*0.74, flx*0.74, ]; 
	}	
	else //adjust right
	{
		if ( my_config["wheel_logo_size"] == "Larger" )
			wheel_x = [ flx*0.76, flx*0.76, flx*0.76, flx*0.76, flx*0.76, flx*0.76, flx*0.725, flx*0.76, flx*0.76, flx*0.76, flx*0.76, flx*0.76, ]; 
		else //smaller
			wheel_x = [ flx*0.78, flx*0.78, flx*0.78, flx*0.78, flx*0.78, flx*0.78, flx*0.74, flx*0.78, flx*0.78, flx*0.78, flx*0.78, flx*0.78, ]; 
	}
	wheel_y = [ -fly*0.22, -fly*0.105, fly*0.0, fly*0.105, fly*0.215, fly*0.325, fly*0.436, fly*0.61, fly*0.72 fly*0.83, fly*0.935, fly*0.99, ];
	if ( my_config["wheel_logo_size"] == "Larger" )
		wheel_w = [ flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.25, flw*0.18, flw*0.18, flw*0.18, flw*0.18, flw*0.18, ];
	else //smaller
		wheel_w = [ flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.19, flw*0.12, flw*0.12, flw*0.12, flw*0.12, flw*0.12, ];
	
	if ( my_config["wheel_semi_t"] == "Yes" )
		wheel_a = [  80,  80,  80,  80,  150,  150, 255,  150,  150,  80,  80,  80, ];
	else
		wheel_a = [  255,  255,  255,  255,  255,  255, 255,  255,  255,  255,  255,  255, ];
	wheel_h = [  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11, flh*0.15,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11,  flh*0.11, ];
	wheel_r = [  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ];
}
num_arts = wheel_count;

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

		if ( slot < 0 ) slot=0;
		if ( slot >=10 ) slot=10;

		m_obj.x = wheel_x[slot] + p * ( wheel_x[slot+1] - wheel_x[slot] );
		m_obj.y = wheel_y[slot] + p * ( wheel_y[slot+1] - wheel_y[slot] );
		m_obj.width = wheel_w[slot] + p * ( wheel_w[slot+1] - wheel_w[slot] );
		m_obj.height = wheel_h[slot] + p * ( wheel_h[slot+1] - wheel_h[slot] );
		m_obj.rotation = wheel_r[slot] + p * ( wheel_r[slot+1] - wheel_r[slot] );
		m_obj.alpha = wheel_a[slot] + p * ( wheel_a[slot+1] - wheel_a[slot] );
		if ( my_config["wheel_logo_mipmap"] == "Yes" )
			m_obj.mipmap = true;
		if ( my_config["wheel_logo_aspect"] == "Yes" )
			m_obj.preserve_aspect_ratio=true;
	}
};

local wheel_entries = [];
for ( local i=0; i<num_arts/2; i++ )
	wheel_entries.push( WheelEntry() );

local remaining = num_arts - wheel_entries.len();

// we do it this way so that the last wheelentry created is the middle one showing the current
// selection (putting it at the top of the draw order)
for ( local i=0; i<remaining; i++ )
	wheel_entries.insert( num_arts/2, WheelEntry() );

local conveyor = Conveyor();
conveyor.set_slots( wheel_entries );
try { conveyor.transition_ms = my_config["transition_ms"].tointeger(); } catch ( e ) { }


// Favourite games marker
function FavStar() 
{
	if (fe.game_info( Info.Favourite ) == "1") return FeConfigDirectory+"gtc-common/art/fav.png";
}

local favourite_marker;
if ( my_config["enable_favstar"] == "Left of Wheel" )
{
	local x;
	local y;
	local wh;
	
	if (conveyor.m_objs.len() > 0)
	{
		local art = wheel_entries[conveyor.m_objs.len()/2].m_obj;
		x = art.x-(flw*0.042);
		y = art.y+(flh*0.038);
		wh = flw*0.04;
	}
		
	favourite_marker = fe.add_image("[!FavStar]",x, y, wh, wh );
	
	if ( my_config["wheel_logo_mipmap"] == "Yes" )
		favourite_marker.mipmap = true;
}

//Wheel fading code starts here
if ( my_config["wheel_fadeout"] != "No" )
{
	first_tick <- 0;
	stop_fading <- true;
	wheel_fade_ms <- 0;
	try {	wheel_fade_ms = my_config["wheel_fade_ms"].tointeger(); } catch ( e ) { }
	
	if ( wheel_fade_ms > 0 )
	{
		function wheel_fade_transition( ttype, var, ttime )
		{
			if ( ttype == Transition.ToNewSelection || ttype == Transition.ToNewList )
			{
					first_tick = -1;
					my_delay = fe.layout.time;
					if ( my_config["enable_pointer"] != "No") 
						pointer.alpha = 255;
					if (my_config["enable_wl_bg"] != "No")
						wheel_art.alpha = wheel_art_alpha;
					if ( my_config["enable_favstar"] != "No" )
					{
						if (fe.game_info( Info.Favourite, var ) == "1")
							favourite_marker.alpha = 255;
					}
			}
			return false;	 
		}
		fe.add_transition_callback( "wheel_fade_transition" );
		
		function wheel_alpha( ttime )
		{
			local _elapsed = 0;
			
			if (first_tick == -1)
				stop_fading = false;

			// handle wheel alpha after keyboard search
			if (first_tick > 0)
				_elapsed = ttime - first_tick;
			
			if (_elapsed < wheel_fade_ms)
			{
				local count = conveyor.m_objs.len();

				for (local i=0; i < count; i++)
				{
					if (i == count/2)
						conveyor.m_objs[i].alpha = 255;
					else
					{
						if ( my_config["wheel_semi_t"] == "Yes" )
							conveyor.m_objs[i].alpha = 80;
						else
							conveyor.m_objs[i].alpha = 255;
					}	
				}
			}

			// Wheel fading
			if ( !stop_fading && ttime - my_delay >= my_play )
			{
				local elapsed = 0;

				if (first_tick > 0)
					elapsed = ttime - first_tick;

				local count = conveyor.m_objs.len();
				
				for (local i=0; i < count; i++)
				{
					if ( elapsed > wheel_fade_ms)
					{
						if ( my_config["wheel_fadeout"] == "Partially" )
							conveyor.m_objs[i].alpha = _partially;
						else
							conveyor.m_objs[i].alpha = 0;
					}
					else
					{
						if (i == count/2)
						{
							_alpha = (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if (_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							conveyor.m_objs[i].alpha = _alpha;
						}
						else
						{
							local _start_alpha = 79;
							if ( my_config["wheel_semi_t"] == "No" )
								_start_alpha = 254;
							_alpha = (_start_alpha * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if (_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							conveyor.m_objs[i].alpha = _alpha;
						}
						
						if ( my_config["enable_pointer"] != "No") 
						{
							_alpha =  (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if (_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							pointer.alpha = _alpha;
						}
						
						if (my_config["enable_wl_bg"] != "No")
						{
							_alpha = (wheel_art_alpha * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if (_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							wheel_art.alpha = _alpha;
						}
						
						if ( my_config["enable_favstar"] == "Left of Wheel" )
						{
							_alpha =  (255 * (wheel_fade_ms - elapsed)) / wheel_fade_ms;
							if (_alpha < _partially && my_config["wheel_fadeout"] == "Partially")
								_alpha = _partially;
							favourite_marker.alpha = _alpha;
						}
					}
				}

				if ( elapsed > wheel_fade_ms)
				{
					//So we don't keep doing the loop above when all values have 0 alpha
					stop_fading = true;
				}
			
				if (first_tick == -1)
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
		art_pulse.preserve_aspect_ratio = true;
	
	local _time = 3000;
	
	local art_scale = { when = Transition.StartLayout, property = "scale", start = 1.0, end = 1.2, time = _time, loop = _loop }
	local alpha_cfg = { when = Transition.StartLayout, property = "alpha", start = 150, end = 0, time = _time, loop = _loop }
	animation.add( PropertyAnimation( art_pulse, art_scale ) );
	animation.add( PropertyAnimation( art_pulse, alpha_cfg ) );

	function pulse_transition( ttype, var, ttime )
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

	local art_scale2 = { when = Transition.ToNewSelection, property = "scale", start = 1.0, end = 1.2, time = _time, loop = _loop }
	local alpha_cfg2 = { when = Transition.ToNewSelection, property = "alpha", start = 150, end = 0, time = _time, loop = _loop }
	animation.add( PropertyAnimation( art_pulse, art_scale2 ) );
	animation.add( PropertyAnimation( art_pulse, alpha_cfg2 ) );
		
	function stop_pulse( ttime )
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


/////////////////////////////////////////////////////////////////////////////////
// Play sound when transitioning to next / previous game on wheel
//
// Use an array that is loaded outside and only updated inside the transition_callback function 
// in order to prevent a memory leak by calling fe.add_sound() within that function

local random_num;
local sound_name="";
local Wheelclick = [];
local i;
for ( i=0; i<20; i++)
	Wheelclick.push(fe.add_sound(sound_name));

local sid = 0;

function sound_transitions(ttype, var, ttime) 
{
	if (my_config["enable_random_sound"] != "No")
	{		
		if (my_config["enable_random_sound"] == "Random")
		{
			random_num = floor(((rand() % 1000 ) / 1000.0) * (322 - (1 - 1)) + 1);
			sound_name = FeConfigDirectory+"gtc-common/sounds/GS"+random_num+".mp3";
		}

		if (my_config["enable_random_sound"] == "Click")
			sound_name = FeConfigDirectory+"gtc-common/sounds/click.mp3";
		
		switch(ttype) 
		{
		case Transition.StartLayout:		
		case Transition.EndNavigation:	
			sid++; // next cell in the array
			if (sid > 19) //if reached end of the array go to the beginning
				sid = 0;
			Wheelclick[sid].file_name = sound_name;
			Wheelclick[sid].playing = true;
		break;
		}
		return false;
	}
}
fe.add_transition_callback("sound_transitions");


/////////////////////////////////////////////////////////////////////////////////
//Boxart 
if ( my_config["enable_gboxart"] == "Yes")
{
	// if wheel_fadeout != No
	local from_side = 2; //enter from right
	local y = 0.41;
	local x = 0.7;
	local w = 0.2;
	local h = 0.5;
	
	if( my_config["wheel_fadeout"] == "No" )
	{
		from_side = -2; //animate from left
		x = 0.01;
		y = 0.55;
        if( aspect_name == "16x10")
			y = 0.57;
		w = 0.13;
		h = 0.4;
	}
		
	local boxart = fe.add_artwork("boxart", flx*from_side, fly*y, flw*w, flh*h );
	boxart.trigger = Transition.EndNavigation;
	boxart.preserve_aspect_ratio = true;
	
	if( my_config["wheel_fadeout"] == "No" )
		boxart.zorder = -10;

	local start_transition1 = {when = Transition.StartLayout, property = "x", start = flx*from_side, end = flx*x, time = my_delay+200}
	animation.add( PropertyAnimation( boxart, start_transition1 ) );

	function boxart_transition( ttype, var, ttime )
	{
		if ( ttype == Transition.EndNavigation )
			boxart.alpha = 255;

		if ( ttype == Transition.ToNewSelection )
			boxart.alpha = 0;

		return false;
	}
	fe.add_transition_callback( "boxart_transition" );

	local move_transition1 = {when = Transition.EndNavigation, property = "x", start = flx*from_side, end = flx*x, time = my_delay+200}
	animation.add( PropertyAnimation( boxart, move_transition1 ) );
}


/////////////////////////////////////////////////////////////////////////////////
// Game info background frame
if ( my_config["enable_frame"] == "Yes" )
{
	local frame = fe.add_image( FeConfigDirectory+"gtc-common/art/frame.png", 0, fly*0.94, flw, flh*0.06 );
	frame.alpha = 255;

	if ( my_config["enable_ini_anim"] == "Yes" )
	{
		local start_transition1 = { when = Transition.StartLayout, property = "y", start = fly*2, end = fly*0.94, time = ini_anim_time }
		animation.add( PropertyAnimation( frame, start_transition1 ) );
	}
}


/////////////////////////////////////////////////////////////////////////////////
// Favourite marker for "With Game Info" setting, separated from "Left to Wheel" 
// to avoid zorder issues
if ( my_config["enable_favstar"] == "With Game Info" )
{
	local x = flx*0.071;
	local y = fly*0.95;
	local wh = flw*0.022;
	
	favourite_marker = fe.add_image("[!FavStar]",x, y, wh, wh );
	favourite_marker.mipmap = true;
	
	if ( my_config["enable_ini_anim"] == "No" )
	{
		// fade in if startup animation is set to No
		local alpha_cfg = {	when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2) }
		animation.add( PropertyAnimation( favourite_marker, alpha_cfg ) );
	}
	if ( my_config["enable_ini_anim"] == "Yes" )
	{
		// animate with game info
		local move_transition_year = { when = Transition.StartLayout, property = "x", start = flx*-2, end = x, time = (ini_anim_time+350) }
		animation.add( PropertyAnimation( favourite_marker, move_transition_year ) );
	}
}	


/////////////////////////////////////////////////////////////////////////////////
// Game info
function Manufacturer_Name( ioffset )
{
	local name = fe.game_info( Info.Manufacturer, ioffset );
	if (name.len() > 0) 
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

if ( my_config["enable_gameinfo"] != "No" )
{
	local year = "";
	local year_b = ""; //black shadow
	local title = "";
	local title_b = ""; //black shadow
	local filter = "";
	local filter_b = ""; //black shadow
	local x_year_b = flx*0.009;
	local x_year = flx*0.01;
	local x_title_b = flx*0.109;
	local x_title = flx*0.11;
	local x_filter_b = flx*0.589;
	local x_filter = flx*0.59;
	//local font_size = 16;
	local font_size = flh*0.016;


	// Year
	year_b = fe.add_text("[Year]", x_year_b, fly*0.92, flw*0.4, flh*0.1);
	year = fe.add_text("[Year]", x_year, fly*0.92, flw*0.4, flh*0.1);
		
	year_b.align = Align.Left;
	year_b.charsize = font_size;
	year_b.set_rgb(0, 0, 0);

	year.align = Align.Left;
	year.charsize = font_size;
	year.set_rgb(255, 255, 255);

	// Title
	if ( my_config["enable_game_manu"] == "Title Only" )
	{
		title_b = fe.add_text("[Title]", x_title_b, fly*0.92, flw*0.6, flh*0.1);
		title = fe.add_text("[Title]", x_title, fly*0.92, flw*0.6, flh*0.1);
	}
	else
	{
		function formatted_text()
		{
			local m = Manufacturer_Name(0);
			local t = "[Title]";

			if (( m.len() > 0 ) && ( t.len() > 0 ))
				return m + ",  " + t;

			return t;
		}
		title_b = fe.add_text("[!formatted_text]", x_title_b, fly*0.92, flw*0.6, flh*0.1);	
		title = fe.add_text("[!formatted_text]", x_title, fly*0.92, flw*0.6, flh*0.1);
	}
	title_b.align = Align.Left;
	title_b.charsize = font_size;
	title_b.set_rgb(0, 0, 0);

	title.align = Align.Left;
	title.charsize = font_size;
	title.set_rgb(255, 255, 255);

	// enumerate game list
	if ( my_config["enable_gameinfo"] == "Info and Enumerate" )
	{
		// Current game out of total number of games
		filter_b = fe.add_text( "Game: [ListEntry]/[ListSize]", x_filter_b, fly*0.92, flw*0.4, flh*0.1 );
		filter = fe.add_text( "Game: [ListEntry]/[ListSize]", x_filter, fly*0.92, flw*0.4, flh*0.1 );
		
		filter_b.align = Align.Right;
		filter_b.charsize = font_size-2;
		filter_b.set_rgb(0, 0, 0);
		
		filter.align = Align.Right;
		filter.charsize = font_size-2;
		filter.set_rgb(255, 255, 255);
	}

	// Random color for info text
	if ( my_config["enable_colors"] == "Yes" )
	{
		function brightrand() {
			return 255-(rand()/255);
		}

		local red, green, blue;

		// Color Transitions
		fe.add_transition_callback( "color_transitions" );
		function color_transitions( ttype, var, ttime ) {
			switch ( ttype )
			{
				case Transition.StartLayout:
				case Transition.ToNewSelection:
				red = brightrand();
				green = brightrand();
				blue = brightrand();
				if(year!="")
					year.set_rgb(red,green,blue);
				if(title!="")
					title.set_rgb(red,green,blue);
				if(filter!="")
					filter.set_rgb(red,green,blue);
				break;
			}
			return false;
		}
	}

	// fade in game info if the startup animation is disabled
	if ( my_config["enable_ini_anim"] == "No" )
	{
		// fade in year
		local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255,	time = (ini_anim_time*2)}
		animation.add( PropertyAnimation( year, alpha_cfg ) );
		
		local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2)}
		animation.add( PropertyAnimation( year_b, alpha_cfg ) );
		
		// fade in title
		local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255,	time = (ini_anim_time*2)}
		animation.add( PropertyAnimation( title, alpha_cfg ) );
		
		local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2)}
		animation.add( PropertyAnimation( title_b, alpha_cfg ) );

		// fade in filter
		if ( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			// animate title
			local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2)}
			animation.add( PropertyAnimation( filter, alpha_cfg ) );
			
			local alpha_cfg = {when = Transition.StartLayout, property = "alpha", start = 0, end = 255, time = (ini_anim_time*2)}
			animation.add( PropertyAnimation( filter_b, alpha_cfg ) );
		}
	}

	// animate game info
	if ( my_config["enable_ini_anim"] == "Yes" )
	{
		// animate year
		local move_transition_year = {when = Transition.StartLayout, property = "x", start = flx*-2, end = x_year, time = (ini_anim_time+350)}
		animation.add( PropertyAnimation( year, move_transition_year ) );

		local move_transition_year_b = {when = Transition.StartLayout,	property = "x",	start = flx*-2,	end = x_year_b, time = (ini_anim_time+350)}
		animation.add( PropertyAnimation( year_b, move_transition_year_b ) );

		// animate title
		local move_transition_title = {when = Transition.StartLayout, property = "x", start = flx*-2, end = x_title, time = (ini_anim_time+350)}
		animation.add( PropertyAnimation( title, move_transition_title ) );
		
		local move_transition_title_b = {when = Transition.StartLayout,	property = "x",	start = flx*-2, end = x_title_b, time = (ini_anim_time+350)}
		animation.add( PropertyAnimation( title_b, move_transition_title_b ) );

		if ( my_config["enable_gameinfo"] == "Info and Enumerate" )
		{
			// animate filter
			local move_transition_title = {when = Transition.StartLayout, property = "x", start = flx*2, end = x_filter, time = (ini_anim_time+350)}
			animation.add( PropertyAnimation( filter, move_transition_title ) );
			
			local move_transition_title_b = {when = Transition.StartLayout,	property = "x",	start = flx*2, end = x_filter_b, time = (ini_anim_time+350)}
			animation.add( PropertyAnimation( filter_b, move_transition_title_b ) );
		}
	}
}


/////////////////////////////////////////////////////////////////////////////////
// Letters
local trigger_letter = false;
local letter_x = 0.5;
if ( my_config["wheel_poisition"] == "Adjust Right" )
	letter_x = 0.55;
	
local letters = fe.add_image("", flw * letter_x - (flw*0.140 * 0.5), flh * 0.5 - (flh*0.280 * 0.5), flw*0.140, flh*0.280);

fe.add_transition_callback( "letter_transition" );
function letter_transition( ttype, var, ttime )
{	
	if (ttype == Transition.ToNewList)
		rtime = glob_time;
}

fe.add_ticks_callback( "letter_tick" );
function letter_tick( ttime )
{
	glob_time = ttime;

	if(glob_time - rtime > glob_delay)
		letters.visible = false; // hide letter search if present
	
    if(trigger_letter == true)
	{
		local firstl = fe.game_info(Info.Title);

		if (my_config["letters_type"] != "No")
		{
			if (my_config["letters_type"] == "Default")
				letters.file_name = FeConfigDirectory + "gtc-common/letters/default/" + firstl.slice(0,1).tolower() + ".png";
			else  //by system display name
				letters.file_name = FeConfigDirectory + "gtc-common/letters/" + fe.displays[fe.list.display_index].name + "/" + firstl.slice(0,1).tolower() + ".png";

			letters.visible = true;
		}
		trigger_letter = false;
    }
}

fe.add_signal_handler(this, "on_signal")
function on_signal(str) 
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


/////////////////////////////////////////////////////////////////////////////////
// Search
local search_surface = fe.add_surface(fe.layout.width *1.12 , fe.layout.height * 1.6)
KeyboardSearch(search_surface)
	.keys_pos([ 0.05, 0.45, 0.9, 0.4 ])
	.search_key( my_config["user_search_key"].tolower() )
	.mode( "show_results" )
	.text_font("BebasNeue Bold")
	.bg_color(0,0,0,210)
	.text_color(0,255,0)
	.keys_selected_color(0,255,0)
	.init()

if (my_config["user_search_boxsize"] == "Large")
	search_surface.set_pos(0, 0, flw, flh); // Large center
else
	search_surface.set_pos(flx*0.15, fly*0.23, flw*0.680, flh*0.58); // Small center


/////////////////////////////////////////////////////////////////////////////////
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
	if ( ttype == Transition.StartLayout)
	{
		curr_sys = fe.list.name;

		if( fe.filters[fe.list.filter_index].name.tolower() == "all" )  //make sure default filter ("all") is on so all games are counted
		{
			if( main_infos.rawin(curr_sys) )  //check if system exists
			{				
				if(fe.list.size != main_infos[curr_sys].cnt)  //if count is wrong, update it with current system list size
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
