# Stable Diffusion WebUI Poses Browser

Extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) for displaying ControlNet's Poses. 

Display the pose preview image, with a button to send the OpenPose, Canny and/or Depth to ControlNet

## Install

Browse to the `Extensions` tab -> go to `Install from URL` -> paste in `https://github.com/Leomaradan/sd-poses-browser` -> click `Install`

## Usage

- Go the the Poses Browser
- Select the wanted pose
- Click to `Send to txt2img` or `Send to img2img`
- Update the ControlNet models according to the images. This step is necessary for this moment, but will hopefully be automated in a next update

### Configuration

By default, the poses are stored in  `/extensions/sd-poses-browser/poses`. 

The extension will look for all images in this directory. Images will be sorted using token filename.

For example, you have an image named `pose-heroic-full-013-ar2x3.png`:
- If you have a `pose-heroic-full-013-ar2x3.pose.png` file, it will be used as OpenPose map
- If you have a `pose-heroic-full-013-ar2x3.depth.png` file, it will be used as Depth map
- If you have a `pose-heroic-full-013-ar2x3.canny.png` file, it will be used as Canny map
- If you have a `pose-heroic-full-013-ar2x3.txt` file, the content will be used as description for the preview image

Theses token can be changed in the Settings, as well as the poses folder