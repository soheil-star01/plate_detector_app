### main.py:  
contains 4 important functions:
1. load_model: loads the pre-trained model (npr-net)  for plate detection
2. preprocess_image: does some preprocess on image
3. get_plate: extracts plate by calling detect_lp function
4. do_process: gets the detected plate and returns plate license and its confidence by calling “tr” OCR
5. video_process: receives the video and samples it per second for plate detection. If plate is detected in sampled frame, its license is recognized. All recognition results are aggregated. Then, the licenses which are recognized in a defined period of time create a group (a car). Finally, confident level is calculated for all groups.

### requirements.txt: 
specifies what python packages and which versions are required to run the project.

### Dockerfile: 
contains a set of instructions that specify what environment to use and which commands to run

### local_utils.py in utils/: 
includes two main functions:
1. detect_lp: detects the plate by applying the preprocessed image to npr-net.
2. reconstruct: crops the output of prediction model for reconstructing  the plate image

### Model/: 
contains two files:
1. npr-net.json:  includes the model structure and some meta data, such as the framework with which the model is implemented
2. npr-net.h5: contains the pre-trained model of npr-net.



## How to use docker?
1. first run this command to create a docker image
```
docker build -t plate_detect .
```
2. run this command to create a container and forward the Jupyter Notebook's port from container to the local machine
```
docker run -d -p 8888:8888 --name plate_detect_cont plate_detect
```
3. (optional) to see logs of container, please use:
```
docker logs plate_detect_cont
```