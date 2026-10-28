///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
	Favorites Module v1.1
	By Yaron

	This module enables any layout to manage a global favorite games romlist.

	*** YOU MUST DISABLE CONFIRM FAVOURITES IN THE ATTRACT MODE CONFIGURE MENU FOR THIS MODULE TO WORK ***
	To do so: Press Tab->General->Confirm Favourites and set to 'No'


	FUNCTIONS:

	get_favorites(): get the favorite games from the Favorites.txt romlist

	update_favorites(): add or remove a game from the Favorites.txt romlist

	check_favorite(): check if the current game is listed in the Favorites.txt romlist, return 'true' if listed and 'false' if not

	test_romlist(): ensures the favorites.txt romlist integrity. If damaged, will try to recreate it from favorites back file
*/
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


DEBUG <- false
DEBUG_CHECK_FAV <- false


local fav_split_list = []

function copy_files( source, target )
{
	local t = clock()

	local data = []
	local line, b

	// read from source file
	local fs = ReadTextFile( FeConfigDirectory+"romlists/" + source + ".txt" )

	while( !fs.eos() )
	{
		data.push( fs.read_line() )
	}

	// write to target file
    local ft = file( FeConfigDirectory+"romlists/" + target + ".txt", "w" )

	for( local x = 0; x < data.len(); x++ )
	{
        line = data[x] + "\n"
        b = blob( line.len() )

		foreach( i, item in line )
			b.writen( item, 'b' )

		ft.writeblob( b )
	}

	ft.close()

	if( DEBUG ) print( format( "Favorites module: copy_files() executed in %u ms\n", (::clock() - t) * 1000 ))
}


function update_favorites_split_list()
{
	local t = clock()

	if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST" ) )
	{
		fav_split_list.clear()
		foreach( i, item in fe.nv["GLOBAL_FAVORITES_LIST"] )
		{
			fav_split_list.push( split(item,";") )
		}
	}

	if( DEBUG ) print( format( "Favorites module: get_favourites_split_list() executed in %u ms, %d games listed\n", (::clock() - t) * 1000, fav_split_list.len() ))
}


// Test the integrity of the favorites romlist file
function test_romlist()
{
	local t = clock()

	local error_line = ";;;;;;;;;;;;;;;;;;;;"
	local i = 0
	local read_favs = []
	local test_good = true

	print("TESTING ROMLIST...\n")

	// read entries from favorites.txt romlist to array
	local f = ReadTextFile( FeConfigDirectory+"romlists/Favorites.txt" )

	while( !f.eos() )
	{
		read_favs.push( f.read_line() )

		if( error_line == read_favs[i] )
		{
			test_good = false

			// copy favorites from backup file
			copy_files( "Favorites_auto_backup", "Favorites" )

			print("!!!!! ROMLIST TEST FAILED, RECREATED IT FROM BACKUP !!!!!\n")
			if( DEBUG ) print( format( "Favorites module: test_romlist() executed in %u ms\n", (::clock() - t) * 1000 ))

			// splash screen message notifying user
			while( !fe.overlay.splash_message( "Favorites romlist was damaged and was recreated from auto backup!\n\n Press Back (Exit) button or key to continue" )) {}
			return
		}
		i++
	}

	if( test_good )
	{
		// backup current favorites version
		copy_files( "Favorites", "Favorites_auto_backup" )
		print("ROMLIST WAS BACKED UP!\n")
	}


	if( DEBUG ) print( format( "Favorites module: test_romlist() executed in %u ms\n", (::clock() - t) * 1000 ))
}


// Read from favorites romlist file
function get_favorites()
{
	local t = clock()
	local read_favs = []

	// read entries from favorites.txt romlist to array
	local f = ReadTextFile( FeConfigDirectory+"romlists/Favorites.txt" )

	while( !f.eos() )
	{
		read_favs.push( f.read_line() )
	}

	// if GLOBAL_FAVORITES_LIST exists in fe.nv, clear it
	if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST" ) )
		fe.nv["GLOBAL_FAVORITES_LIST"].clear()

	// add the favourites list to our own table in fe.nv
	fe.nv["GLOBAL_FAVORITES_LIST"] <- read_favs

	// Create a split list of favorites
	update_favorites_split_list()

	if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST_LOADED" ) )
		fe.nv["GLOBAL_FAVORITES_LIST_LOADED"] = 1
	else
		fe.nv["GLOBAL_FAVORITES_LIST_LOADED"] <- 1

	if( DEBUG ) print( format( "Favorites module: load_favourites() executed in %u ms, %d games listed\n", (::clock() - t) * 1000, fe.nv["GLOBAL_FAVORITES_LIST"].len() ))
}


// Update favorites romlist file
game_found <- false

function update_favorites()
{
	local t = clock()

	// prevents favourites display from freezing if trying to remove from an empty list
	if( fe.game_info(Info.Name) == "" && fe.game_info(Info.Title) == "" && fe.game_info(Info.Emulator) )
		return


	local favs = []
	local b, line, title_and_emulator

	game_found = false

	fav_split_list.clear()

	// rebuild list
	if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST" ) )
	{
		foreach( i, item in fe.nv["GLOBAL_FAVORITES_LIST"] )
		{
			title_and_emulator = split( item, ";" )

			if( fe.game_info( Info.Title ) == title_and_emulator[1] && fe.game_info(Info.Emulator) == title_and_emulator[2] )
			{
				game_found = true
				if( DEBUG ) print("Favorites module: update_favorites() Removed from favorites: " + item + "\n")
			}
			else
			{
				favs.push(item)
				fav_split_list.push( title_and_emulator )
			}
		}
	}

	// if game doesn't exist add it to array
	if( game_found == false )
	{
		local new_fav = fe.game_info(Info.Name) + ";" +
						fe.game_info(Info.Title) + ";" +
						fe.game_info(Info.Emulator) + ";" +
						fe.game_info(Info.CloneOf) + ";" +
						fe.game_info(Info.Year) + ";" +
						fe.game_info(Info.Manufacturer) + ";" +
						fe.game_info(Info.Category) + ";" +
						fe.game_info(Info.Players) + ";" +
						fe.game_info(Info.Rotation) + ";" +
						fe.game_info(Info.Control) + ";" +
						fe.game_info(Info.Status) + ";" +
						fe.game_info(Info.DisplayCount) + ";" +
						fe.game_info(Info.DisplayType) + ";" +
						fe.game_info(Info.AltRomname) + ";" +
						fe.game_info(Info.AltTitle) + ";" +
						fe.game_info(Info.Extra) + ";" +
						fe.game_info(Info.Buttons) + ";" +
						fe.game_info(Info.Series) + ";" +
						fe.game_info(Info.Language) + ";" +
						fe.game_info(Info.Region) + ";" +
						fe.game_info(Info.Rating)

		favs.push( new_fav )

		title_and_emulator = split( new_fav,";" )

		fav_split_list.push( title_and_emulator )

		if( DEBUG ) print("Favorites module: update_favorites() Added to favorites: " + new_fav + ", list size = " + favs.len() + "\n")
	}


	// if table exists in fe.nv, clear it
	if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST" ) )
		fe.nv["GLOBAL_FAVORITES_LIST"].clear()

	// update table in fe.nv
	fe.nv["GLOBAL_FAVORITES_LIST"] <- favs


	// write array to favorites.txt romlist
    local fs = file( FeConfigDirectory+"romlists/Favorites.txt", "w" )

	for( local x = 0; x < favs.len(); x++ )
	{
        line = favs[x] + "\n"
        b = blob( line.len() )

		foreach( i, item in line )
			b.writen( item, 'b' )

		fs.writeblob( b )
	}

	fs.close()

	if( DEBUG ) print( format( "Favorites module: update_favorites() executed in %u ms\n", (::clock() - t) * 1000 ))
}


// Find out if a game is listed in favorites romlist
function check_favorite()
{
	local t = clock()

	for( local i = 0; i < fav_split_list.len(); i++ )
	{
		if( fe.game_info(Info.Title) == fav_split_list[i][1] && fe.game_info(Info.Emulator) == fav_split_list[i][2] )
		{
			// game found
			if( DEBUG_CHECK_FAV ) print( format( "Favorites module: check_favorite() game found in %u ms\n", (::clock() - t) * 1000 ))
			return true
		}
	}

	// game not found
	if( DEBUG_CHECK_FAV ) print( format( "Favorites module: check_favorite() game not found in %u ms\n", (::clock() - t) * 1000 ))
	return false
}


// Intercept add/remove favorites signals
fe.add_signal_handler( "signal_intercept_favorites" )
function signal_intercept_favorites( str )
{
	switch( str )
	{
		case "add_favourite":
			// if removing a game from the Favourites display screen don't update romlist as it is done locally there
			if( fe.displays[fe.list.display_index].name == "Favorites" || fe.displays[fe.list.display_index].name == "Favourites" )
				return false
			else
				update_favorites()
		break

		case "exit":
		case "exit_to_desktop":
			if( fe.nv.rawin( "GLOBAL_FAVORITES_LIST_LOADED" ) )
				fe.nv["GLOBAL_FAVORITES_LIST_LOADED"] = 0
			else
				fe.nv["GLOBAL_FAVORITES_LIST_LOADED"] <- 0
		break
	}

    return false
}
