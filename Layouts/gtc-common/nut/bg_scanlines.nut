if( my_config["enable_bg_scanline"] != "No" )
{
	local scanlines = FeConfigDirectory+"gtc-common/art/arcade/scanlines_1920.png"
	if(ScreenWidth < 1920)
		scanlines = FeConfigDirectory+"gtc-common/art/arcade/scanlines_720.png"

	bg_scanlines.file_name = scanlines
	bg_scanlines.preserve_aspect_ratio = false

	if( my_config["enable_bg_scanline"] == "Light" )
		bg_scanlines.alpha = 30
	else if( my_config["enable_bg_scanline"] == "Medium" )
		bg_scanlines.alpha = 80
	else if( my_config["enable_bg_scanline"] == "Strong" )
		bg_scanlines.alpha = 150
}
