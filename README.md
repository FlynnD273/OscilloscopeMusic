# Oscilloscope Music

Generate vectorscope art using Blender grease pencil.

## Requirements

- Blender
- Python

To install all needed Python packages, run `pip install -r requirements.txt`

## How To Use

Open the Blender project, make whatever animation you want, then bake the grease pencil. It must be baked for the script to work. Next, run the `export.py` script from within Blender. Once this is complete, run the `convert.py` script outside of Blender. The reason why you need to run this in an outside environment is because I'm using the SciPy library to generate the wav file.


To test the file, you can use something like ffplay or ffmpeg to make a vectorscope visualization. For example, you can run this command with ffplay added to your PATH: 

`ffplay -f lavfi "amovie=curve_animation_stereo_audio.wav, asplit [a][out1]; [a] avectorscope=size=500x500:swap=1:mirror=y:zoom=1.5:mode=lissajous_xy:scale=log:draw=line:af=200:rf=200:bf=200:gf=200 [out0]"`

