# **Leto**
----------------------------------
## Running Reduction and Reconstruction Methods Using ***config.ini***:

For existing Reduction and Reconstruction Methods, use the following guide to modify the [***config.ini***](config.ini) file prior to method execution.  If you have a new method you would like to get working with the ***config.ini***, then follow the instructions outlined in the [next section](#using-configini-with-new-reduction-and-reconstruction-methods) to do so.

For existing methods, perform the following prior to method execution:

1. Open the [***config.ini***](config.ini) and identify the appropriate section for the method you would like to execute.
    - sections are denoted by the following pattern ```[<METHOD_CLASS>.<METHOD_NAME>]```; so, if you want to use a ***reduction*** method called ***fps_bitrate***, the ***config.ini*** file section should be titled something like ```[reduction.fps_bitrate]```.

2. Modify the values for the keys you would like to change.  For example, if you would like to execute ***fps_bitrate*** with an ***fps*** value of 15 and a ***bitrate*** value of 0 (for 10x reduction), then the ***config.ini*** file should be modified to resemble:

```ini
[reduction.fps_bitrate]
; method specific parameters:
fps = 15
bitrate = 0

; s3 prefixs for input/output:
method_name = fps_bitrate
input_prefix_s3 = original-videos/
output_prefix_s3 = reduced-videos/%(method_name)s-fps_%(fps)s-bitrate_%(bitrate)s/
```

3. Execute the method at the console just like any other .py file:

```console
python path/to/method/fps_bitrate.py
```

## Using ***config.ini*** with New Reduction and Reconstruction Methods:

To use the ***config.ini*** file to handle all arguments for the new method, implement the following steps:

***Note***: a comprehensive guide on the syntax of **configparser** and access of the ***config.ini*** arguments can be found in the [configparser documentation](https://docs.python.org/3/library/configparser.html).

1. Add access to modules from the root of the repo by copying the following code into the ***imports*** sections of your .py file:
```python
# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)
```
2. Import the ***ConfigHandler*** from the ***utilities*** module:
```python
from utilities import ConfigHandler
```
3. Create a new section in the [config.ini](config.ini) file for your method
  - Follow the existing formatting to create a new section:
    - For Reduction (R1) methods, place your section under:
      ```; REDUCTION (R1) METHODS: ```
    - For Reconstruction (R2) methods, place your section under:
      ```; RECONSTRUCTION (R2) METHODS:```
  - A section is defined by Square Brackets, and should follow the defined naming convention:

      ```
      [<METHOD_CLASS>.<METHOD_NAME>]
      ```
      An example for a ***reduction*** method named ***fps_bitrate***:
      ```
      [reduction.fps_bitrate]
      ```  
  - Under your new section, define the arguments/variables you will need in your method.  This takes the form of a key/value format.  An example section is given below.  Comments are denoted using ```;``` and inline comments are allowed using ```;``` as well.  Sub-sections can be denoted with comments for readability, but this has no effect on accessing the configurations.
  - Interpolation of values is supported with ***configparser***, here is the [documentation for the syntax of interpolation](https://docs.python.org/3/library/configparser.html#interpolation-of-values).

  ```ini
  [reduction.fps_bitrate]
; method specific parameters:
fps = 20 ; frames per second
bitrate = 100 ; internal bitrate of the reduced video

; s3 prefixs for input/output:
method_name = fps_bitrate
input_prefix_s3 = original-videos/
output_prefix_s3 = reduced-videos/%(method_name)s-fps_%(fps)s-bitrate_%(bitrate)s/
  ```

4. Instantiate the ***ConfigHandler*** class in the entry-point section of your Python file.  This is done by specifying the section you defined in the above step ```[<METHOD_CLASS>.<METHOD_NAME>]```.  Once the class is instantiated, create variables to make accessing different sections of the ***config.ini*** file easier.  In the below example, two sections are accessed: ***s3***, which maps to the ```[DEFAULT]``` section of the ***config.ini*** file; and ***method***, which maps to the ```[reduction.fps_bitrate]``` section supplied in the class instantiation.  

```python
config = ConfigHandler('reduction.fps_bitrate')
s3 = config.s3
method = config.method
```

5. Access the configurations/arguments supplied in the ***config.ini*** file within your Python file.  This is done using standard ***dict*** notation, supplying the key to get the value.  ***Note***: *configparser* by default returns a ***str*** object when keys are accessed directly.  However, there are specific [getter methods in configparser](https://docs.python.org/3/library/configparser.html) to return ***bools***, ***ints***, and ***floats***.  Alternatively, the ***str*** object can be pulled into the py file and then cast to the correct datatype.  An example of accessing values from the above instantiation is given below:

```python 
# accessing bitrate, pulling in as an int
bitrate = method.getint('bitrate')

# accessing output_prefix_s3 as a str
method['output_prefix_s3'] 

```

6. Run your .py file.  Boom, no you can dynamically allocate parameters in the ***config.ini*** file and then execute the .py file cleanly without CLI input.  

## Requirement Installation

Each Reduction and Reconstruction method has its own set of requirements.  These requirements can be quickly and easily installed using the ***requirements.txt*** file in each method.  To do this, navigate to the desired method's subdirectory and run the following command:

```console
pip install -r <REQUIREMENTS.TXT>
```

The name of the requirements.txt file may vary slightly.

## Project Structure

```
├──  leto				contains all modules that facilities all functionality to achieve leto's goal
│   ├── benchmarking
│       ├── mediapipe
│           ├── object_detection.py
│           ├── visualize.py
│           ├── Dockerfile_mp
│           ├── requirements_mp.txt
│           ├── Dockerfile_mp
│           ├──lambda_function_mp.py
│       ├── yolo
│           ├── yolo.py
│           ├── pipeline.py
│           ├── training_parameter_input.py
│           ├── prediction_parameter_input.py
│           ├── pipeline.py
│           ├── visualize.py
│           ├── Dockerfile_yolo
│           ├──lambda_function_yolo.py
│           ├── requirements_yolo.txt
│       ├── video_quality
│           ├── video_quality_functions.py
│
│   ├── reduction
│       ├── ffmpeg_resolution_downsampler
│           ├── requirements_ffmpeg_resolution_downsampler.txt
│           ├── ffmpeg_resolution_downsampler.py
│       ├── fps_bitrate
│           ├── fps_bitrate.py
│           ├── app-fps_bitrate.py
│           ├── requirements.txt
│           ├── README.md
│       ├── cv2_jpg_reduction
│           ├── cv2_jpg_reduction.py
│           ├── requirements_cv2_jpg_reduction.txt
│
│   ├── reconstruction
│       ├── realbasicvser
│           ├── builder.py
│           ├── realbasicvsr_x4.py
│           ├── realbasicvsr_x4.py
│           ├── reconstruction_realbasicvsr_setup.sh
│           ├── realbasicvsr_preprocessing.py
│           ├── reconstruction_realbasicvsr.py
│           ├── realbasicvsr_postprocessing.py
│       ├── opencv_resoltion_upscaler
│           ├── requirements_opencv_resoltion_upscaler.txt
│           ├── opencv_resoltion_upscaler.py
│       ├── superres
│           ├── requirements_superres.txt
│           ├── reconstruction_superres.py
│       ├── fastsrgan
│           ├── fastsrgan.py
│           ├── requirements_fastsrgan.txt
|
│   ├── utilities
|       ├──cloud_functionality.py
|       ├──config_handler.py
|
│
├──  tests				contains unit tests
│   ├── test_get_meta_data.py
│   ├── conftest.py
│   ├── test_data
│      ├── test_video.mp4

```
----------------------------------