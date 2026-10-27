local search_surface = fe.add_surface(fe.layout.width *1.12 , fe.layout.height * 1.6)
search_surface.zorder = 20
local search_box = KeyboardSearch(search_surface)
	.keys_pos([ 0.05, 0.45, 0.9, 0.4 ])
	.search_key( my_config["user_search_key"].tolower() )
	.mode( "show_results" )
	.text_font("BebasNeue Bold")
	.bg_color(0,0,0,210)
	.text_color(0,255,0)
	.keys_selected_color(0,255,0)
	.init()

if(my_config["user_search_boxsize"] == "Large")
	search_surface.set_pos(0, 0, flw, flh); // Large center
else
	search_surface.set_pos(flx*0.15, fly*0.23, flw*0.680, flh*0.58); // Small center
