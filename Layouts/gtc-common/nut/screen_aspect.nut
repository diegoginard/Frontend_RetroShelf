// Code adapted from nevato theme


local settings = {
   "default": {
   //16x9 is default
      aspectDepend = {
        res_x = 2133,
        res_y = 1200}
   },
   "16x10": {
      aspectDepend = {
        res_x = 1920,
        res_y = 1200}
   },
    "16x9": {
      aspectDepend = {
        res_x = 1920,
        res_y = 1080}
   },
   "4x3": {
      aspectDepend = {
        res_x = 1600,
        res_y = 1200}
   }
   "5x4": {
      aspectDepend = {
        res_x = 1500,
        res_y = 1200}
   }
}

local aspect = fe.layout.width / fe.layout.height.tofloat();
switch( aspect.tostring() )
{
    case "1.77865":  //for 1366x768 screen
    case "1.77778":  //for any other 16x9 resolution
        aspect_name = "16x9"
	break;
    case "1.6":
        aspect_name = "16x10"
	break;
    case "1.33333":
        aspect_name = "4x3"
	break;
    case "1.25":
        aspect_name = "5x4"
	break;
    case "0.75":
        aspect_name = "3x4"
	break;
	default:
        aspect_name = "16x9"
	break;
}

function Setting( id, name )
{
	if( aspect_name in settings && id in settings[aspect_name] && name in settings[aspect_name][id] )
		return settings[aspect_name][id][name]

	return settings["default"][id][name]
}

fe.layout.width = Setting("aspectDepend", "res_x")
fe.layout.height = Setting("aspectDepend", "res_y")
