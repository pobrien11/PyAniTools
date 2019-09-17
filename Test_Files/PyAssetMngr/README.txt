
exe folder:
for any executables that are used to debug, but not part of actual application ecosystem.

Testing Rigs

Test 1:

1. Upload the char folder contents to /LongGong/assets/char/. 
2. Remove the v008 in work/ and approved/history folder. This will get added after users get the first rig addition which is v007
3. V005 and v006 of the rig never get downloaded or shown.
4. Once users get the rig v007, can upload v008.
5. The rig file in the approved/ folder (not approved/history) starts off as the v007 rig. Be sure to update it to v008 when testing v008.
6. Then remove rig and see it gets removed.

Test 2:
repeat but only upload work folders to test no approved.



Testing GPU cache

1. Upload the set folder contents to /LongGong/assets/set/.
2. After users get the new cache, can update it with new text and re-upload and check users get update.
3. Then remove cache and see that it gets removed.



Testing Audio

- Will need to send a custom sequence.json since sequence list users have eliminates test sequences

1. Upload Seq001/Shot010/ contents to /LongGong/sequences/Seq001/Shot010/
2. Test users get audio file, if being tracked won't show anyhting since brand new
3. Update audio file with new text. See if users get new file and if tracking, shows in report.
4. Then remove audio and see it gets removed.



Testing Tools

1. Upload tools/maya/scripts/misc_scripts/one_button_shot_finish.mel to /LongGong/tools/maya/scripts/misc_scripts/
2. Upload tools/maya/scripts/lt_awesome.mel to /LongGong/tools/maya/scripts/
3. See that tools show up. Note won't be in cgt_metadata, so no version or notes available.
4. Update tools and see if update.
5. Delete tools.

