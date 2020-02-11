

--------------------------------------------------SEQ ASSET TESTS -----------------------------------------------------------


Sequence numbers

	- Seq310 tests part names
	- Seq210 tests no part names


testing precedence seq level
	
	upstream folder/
	
	part name check:

		- editorial 310 v001 part 2 should be replaced with animation 310 v002 part 2

	no part name check:

		- editorial 210 v001 should be replaced by animation 210 v002

	multiple depts:

		- same as above but upload both animation, layout, and editorial, and editorial, layout should go to general downloads so that general downloads contains:
			- editorial 210 v002
			- editorial 310 v002 part 2
			- editorial 310 v002 part 3 - checks that a dept with multiple files gets moved properly 
			- layout 310
			- layout 370

testing no precedence seq level

	upstream folder/

	part name check

		- editorial 310 v001 part2 should get editorial with v002 part 2
		- animation 310 002 part 2 gets added
	
	no part name check
		
		- editorial 210 v001 replaced by editorial 210 v002
		- animation 210 v002 gets added

------------------------------------------------ SHOT ASSET TESTS -------------------------------------------------------------


testing precedence shot level
	
	Seq370 folder/
	
		- layout 370 shot 470 v001 should be replaced with animation 370 shot 470 v002
		- previs 370 shot 470 v002 goes to general dl location
		- layout 370 shot 470 v002 goes to general dl location

	Seq400 folder/

		- previs shot 010 v001 replaced by layout v002

testing no precedence seq level

	Seq370 folder/

		- layout 370 shot 470 v001 should be replaced with layout 370 shot 470 v002
		- animation 370 shot 470 v002 added


