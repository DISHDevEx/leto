FROM public.ecr.aws/lambda/python:3.10

# Set the working directory inside the container


#COPY --from=make-pthread-nameshim /pthread-nameshim/pthread_shim.so /opt/pthread_shim.so
COPY requirements_mp.txt ${LAMBDA_TASK_ROOT}

COPY object_detection.py ${LAMBDA_TASK_ROOT}

# Copy function code
COPY lambda_function_mp.py ${LAMBDA_TASK_ROOT}

# Copy wheel file
COPY setup.py ${LAMBDA_TASK_ROOT}

COPY dist/mediapipe_model-0.0.1-py3-none-any.whl ${LAMBDA_TASK_ROOT}
RUN pip3 install mediapipe_model-0.0.1-py3-none-any.whl --target "${LAMBDA_TASK_ROOT}"



# Install the specified packages
RUN pip install -r requirements_mp.txt ${LAMBDA_TASK_ROOT}
RUN yum install -y mesa-libGLw

ADD https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite /var/task/efficientdet_lite0.tflite

RUN chmod a+rx /var/task/*.tflite
RUN ls
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
RUN pwd
CMD [ "lambda_function_mp.handler" ]