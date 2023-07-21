FROM public.ecr.aws/lambda/python:3.10
#COPY --from=make-pthread-nameshim /pthread-nameshim/pthread_shim.so /opt/pthread_shim.so

COPY requirements_yolo.txt ${LAMBDA_TASK_ROOT}

# Copy function code
COPY lambda_function_yolo.py ${LAMBDA_TASK_ROOT}
 
# Install the specified packages
RUN pip install -r requirements_yolo.txt
RUN yum install -y mesa-libGLw

# Setup Wheel
COPY dist/yolo-0.0.1-py3-none-any.whl .
RUN pip3 install yolo-0.0.1-py3-none-any.whl --target "${LAMBDA_TASK_ROOT}"

ADD https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt /var/task/yolov8s.pt

RUN chmod a+rx /var/task/*.pt
RUN ls
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function_yolo.handler" ]