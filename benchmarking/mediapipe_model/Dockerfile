FROM public.ecr.aws/lambda/python:3.10
#COPY --from=make-pthread-nameshim /pthread-nameshim/pthread_shim.so /opt/pthread_shim.so
COPY requirements_mp.txt ${LAMBDA_TASK_ROOT}
COPY object_detection.py "${LAMBDA_TASK_ROOT}"
COPY visulize.py "${LAMBDA_TASK_ROOT}"
COPY lambda_function_mp.py ${LAMBDA_TASK_ROOT}
# Install the specified packages
RUN pip install -r requirements_mp.txt
RUN yum install -y mesa-libGLw
ADD https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/latest/efficientdet_lite0.tflite /var/task/efficientdet_lite0.tflite
RUN chmod a+rx /var/task/*.tflite
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
RUN pwd
CMD [ "lambda_function_mp.handler" ]
