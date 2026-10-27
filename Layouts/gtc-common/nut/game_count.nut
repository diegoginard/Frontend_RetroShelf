// Code adapted from the PCCA theme by pcca-matrix


main_infos <- {}
if( !file_exist(FeConfigDirectory + "gtc.stats") )
{
	fe.overlay.splash_message ("Counting games, please wait...")
	print("Created the gtc.stats file!\n")
	refresh_stats()
}
main_infos <- LoadStats()

fe.add_transition_callback( "system_stats" )
function system_stats( ttype, var, ttime )
{
	local curr_sys
	if( ttype == Transition.StartLayout )
	{
		curr_sys = fe.list.name

		if( fe.filters[fe.list.filter_index].name.tolower() == "all" )   // make sure default filter ("all") is on so all games are counted
		{
			if( main_infos.rawin(curr_sys) )  //check if system exists
			{
				if( fe.list.size != main_infos[curr_sys].cnt )   // if count is wrong, update it with current system list size
				{
					main_infos[curr_sys].cnt = fe.list.size
					SaveStats(main_infos)
					print("Updated number of games for " + curr_sys + "\n")
				}
			}
			else   // if system is new and does not exist in the gtc.stats file, create new entry and count
			{
				main_infos <- refresh_stats(curr_sys)
				print("Created new entry for " + curr_sys + " and counted games for it" + "\n")
			}
		}
	}
	
	return false
}
