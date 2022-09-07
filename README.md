# Sensitivity_Map.py
Processes many images of hits to produce a sensitivity map

Enter a directory of many images. These images can be RGB/Gray, 8,10,12,16bit and any image file type(.jpg,.png,.tiff,etc..)

Enter the number of images you wish to process.


if you already have a centroiding/hit-identification algorithm, input the threshold you normally use. If you don't know what thresh to use, 
leave it blank and stand in threshold will be computed using the first 10 images in set ( thershold is calculated simply as mean gray level + 3 std )

The min hit size is simply for hit identification robustnesss, set to 1 if you don't care.

I recommend thresholded peak detection, but there is also an option for morphological identification  via dilations and relative height comparisons. 
The relative height input is a "threshold" for what fraction of total height of the hit must be descended before ascending again.
