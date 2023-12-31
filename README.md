# **Leto**
----------------------------------

## Mapping Between Compatible Reduction and Reconstruction Methods


| Reduction Method         | Applicable Reconstruction Method(s)    |
|--------------|-----------|
| [ffmpeg_resolution_downsampler](./reduction/ffmpeg_resolution_downsampler/) (360p,420p,640p,720p) | [opencv_resolution_upscaler](./reconstruction/opencv_resolution_upscaler/) <br> [superres](./reconstruction/superres/) (4 different configurations) <br> [fastsrgan](./reconstruction/fastsrgan/) <br> [realbasicvsr](./reconstruction/realbasicvsr/) (small sample size, takes a long time)     |
| [fps_bitrate](./reduction/fps_bitrate/) <br> key frame extraction    | Linear Frame interpolation <br> NN based frame interpolation   |
| NN Codec                   |  NN Codec |
| [cv2_jpg_reduction](./reduction/cv2_jpg_reduction/)                   |  N/A  |
|Background Subtraction  |  Background Addition  |



## Running Reduction and Reconstruction Methods Using ***config.ini***:

For existing Reduction and Reconstruction Methods, use the following guide to modify the [***config.ini***](config.ini) file prior to method execution.  If you have a new method you would like to get working with the ***config.ini***, then follow the instructions outlined in the [next section](#using-configini-with-new-reduction-and-reconstruction-methods) to do so.

### Reduction Method Execution
For existing Reduction methods, perform the following prior to method execution:

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
### Reconstruction Method Execution
Reconstruction method execution is similar to Reduction method execution, with one key difference; Reconstruction method execution is dependant upon a previously executed Reduction method.  Follow these steps to execute a Reconstruction method:

1. Within the [***config.ini***](config.ini) file, identify the appropriate Reconstruction section for the method you wish to execute.
    - sections are denoted by the following pattern ```[<METHOD_CLASS>.<METHOD_NAME>]```; so, if you want to use a ***reconstruction*** method called ***smooth_fps***, the ***config.ini*** file section should be titled something like ```[reconstruction.smooth_fps]```.

2. Modify the ***reduction_method_ref*** value to reflect the Reduction method you will be pulling from for the input videos.  This variable, ***reduction_method_ref***, is located at the top of each Reconstruction method section in the config.ini.  As an example, if you would like to change the referenced Reduction method from ***fps_bitrate*** to ***ffmpeg_resolution_downsampler***, then the ***reduction_method_ref*** for the Reconstruction section would need to change from:

```ini
reduction_method_ref = ${reduction.fps_bitrate:method_directory}
```
to the following reference:
```ini
reduction_method_ref = ${reduction.ffmpeg_resolution_downsampler:method_directory}
```
***Note***: the input video path and output video path for all Reconstruction methods are dependant on the values in the referenced Reduction section; so ensure that the variables listed in the referenced Reduction section are accurate for your use case.  This can be ensured by executing you desired [Reduction Method](#reduction-method-execution), and then immediately executing your desired [Reconstruction Method](#reconstruction-method-execution) without making any changes to the Reduction method section.

3. Modify the values for the keys you would like to change.  For example, if you would like to execute ***smooth_fps*** with a ***codec*** value of *mp4v* and a ***factor*** value of 2, then the ***config.ini*** file should be modified to resemble:

```ini
[reconstruction.smooth_fps]

#########################
; change reduction_method_ref to reflect desired reduction method
; i.e. FROM/ ${reduction.ffmpeg_resolution_downsampler:method_directory}  TO/  ${reduction.fps_bitrate:method_directory}
#########################
reduction_method_ref = ${reduction.fps_bitrate:method_directory}

; method specific parameters:
codec = mp4v ; desired video codec
factor = 2

; cloud_functionality parameters:
download_model = True ; boolean to indicate if a model needs to be downloaded
local_model_path = smooth.pkl ; local path to save pre-trained model
clean_model = True ; boolean to indicate to clean video or not

; s3 prefixs for input/output paths and models:
method_name = smooth_fps
input_prefix_s3 = reduced-videos/${reduction_method_ref}
output_prefix_s3 = reconstructed-videos/${method_name}-factor${factor}-reduction_${reduction_method_ref}
model_prefix_s3 = pretrained-models/smooth.pkl ; s3 prefix of the pre-trained model
```
4. Execute the method at the console just like any other .py file:

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

6. Run your .py file.  Boom, now you can dynamically allocate parameters in the ***config.ini*** file and then execute the .py file cleanly without CLI input.

## Requirement Installation

Each Reduction and Reconstruction method has its own set of requirements.  These requirements can be quickly and easily installed using the ***requirements.txt*** file in each method.  To do this, navigate to the desired method's subdirectory and run the following command:

```console
pip install -r <REQUIREMENTS.TXT>
```

The name of the requirements.txt file may vary slightly.




## Running Benchmarking:
**Note: Before running the benchmarking scripts make sure the AWS credentials and the token is not expired.**

The following scripts are aviliable.
```
1. orignal_file_size.py

2. reduced_file_size.py

3. reconstructed_file_size.py

4. yolo_confindence_scores.py

5. mediapipe_confidence_scores.py

```
Run py files to generate the appropriate metrics.
These scripts can run from anywhere.(local, aws etc)

The arguments passed to these scripts come form _config.ini file_
### for example:

```ini
[benchmarking.reduced_file_size]
; method specific arguments
table_name = leto_reduced_file_size
directory_key = original-videos/
```
All the scripts will upload the metrics to the tables in **Dynamodb**.

The following tables are present today so change them accordingly in the **config.ini** file.

1. leto_original_file_size
2. leto_reduced_file_size
3. leto_reconstructed_file_size
4. mediapipe_confidence_scores
5. yolo_confidence_scores


In order to merge tables to a dataframe,
```
from benchmarking.video_quality.table_merge import mergetablestodf

df = mergetablestodf()


```

----------------------------------
