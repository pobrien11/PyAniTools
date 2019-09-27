These are used with the mngr_tests.py in pyani.core.mngr package

* only file needed is analyzer.py, needs to be on z drive spo can check modification date, rest are just pretened files in cache

cgt_tools_cache_before.json is the cache before sync
	- adds new_app_bridge.py to pyani, lib, app_bridge
	- adds analyzer.py to maya, scripts, render_logs

cgt_tools_cache_after.json is the cache after a sync
	- asset_modified check (file deleted): removes new_app_bridge.py to pyani, lib, app_bridge
	- asset modified check (file modified): modifies analyzer.py in maya, scripts, render_logs
	- asset modified check (files added): adds new_tool.mll and new_tool.bundle to maya, plugins, 2016.5
	- assset modified check (files swapped): pyani, apps, PyExrViewer removes play_off, adds new_image
	- new asset check: adds a new tool to maya, scripts, lt_awesome.lt
	- remove asset check: removes PySession from pyani, apps

tools_timestamps_from_server.json is the server timestamps file - what is generated in server_download() dynamically, but this allows us to not have to download anything.

cgt_asset_info_cache_before.json is the cache before sync
	- adds AAA_Test_charFishSoldierB to char, rigs
	- 

cgt_asset_info_cache_after.json is the cache aftersync
	- asset_modified check (file deleted): remove file in char, rig, TestCharDog : TestCharDog_A_rig_high.ma
	- asset modified check (file modified): modifies setGarageInside in sets, rig updating setGarageInside_rig_high.mb
	- asset modified check (files added): set, cache, setBlackMarketCaveA: setBlackMarketCaveA_model_GPU_s100_cave.abc
	- assset modified check (files swapped): set, cache, setRestaurantInside removes:
		- setRestaurantInside_Fence_model_v001_high.ZTL
                - setRestaurantInside_model_v003_high.ZTL
                - setRestaurantInside_model_v004_high.ZTL
	  and swaps with:
		- setRestaurantInside_Fence_model_v001_high.abc
                - setRestaurantInside_model_v003_high.abc
                - setRestaurantInside_model_v004_high.abc
	- new asset check: adds new audio Seq160/Shot120.5 and AAA_setHeisHouseBlocking GPU cache
	- remove asset check: removes AAA_Test_charFishSoldierB from char, rigs


