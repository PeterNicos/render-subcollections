# Render-Subcollections
A Blender Add-On that lets you select subcollections in your scenetree, then for each subcollection: Activates it, renders the camera(s) inside, deactivates it

### What is it used for?
I use it for a scene with many individual camerashots in it. Each of these camerashots has a specific news anchor in it and as there are too many to always render all the cameras individually and each time activate one camera and its realated objects, then change the renderoutput name to be the right one, then deactivate the camera and all of its realted objects, then proceed to the next one and spend hours and hours of doing this just to have a new version of each shot in your scene, I created this Add-On.

### Here is a demo.
This is how I set up my Blenderproject to work with the Add-On. I have my Scene Collection that contains everything. Inside that my Base scene that is always displayed, then my "Camera Shots Main Collection" that holds all the Subcollections that contains the cameras + specific object needed for that shot.

![gif animation of the Add-On used in chess scene](assets/Chess_Scene_1.gif)

Naming is totaly up to you, just make sure to select your Main Collection in the panel, then your Subcollections should be listed for you to check which one should be rendered.

The beautiful models in the demo scene are from Polyhaven:
- [Chess Set](https://polyhaven.com/a/chess_set)
- [Gothic Coffee Table](https://polyhaven.com/a/gothic_coffee_table)
- [HDRI Mirrored Hall](https://polyhaven.com/a/mirrored_hall)

### Have fun!
Hope you can save time using the add-on!