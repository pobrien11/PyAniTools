Tests:
- nCloth gets updated when other depts present
- precedence - layout present, but anim and nHair are in downloads, so anim should replace, Nhair get left
Seq130
	Shot410
		nCloth, v3 - replace with nCloth, v2
		layout, v3 - replace with Ani, v3
Tests:
- Bg gets updated when other depts present
Seq210
	Shot030
		BG, Ani, v1 - replace with BG, Ani, v2
		Ani v1 - should replace with Ani, v2

Tests:
other depts replace 
Seq240
	Shot190
		previs, v1 - replace with ANi, v1
	Shot240
		previs, v1 - replace with Ani, v1
	Shot030
		BG should get created, not there but in downloads
