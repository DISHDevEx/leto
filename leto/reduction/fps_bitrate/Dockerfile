FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Copy function code
COPY fps_bitrate.py ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
 
# Install the specified packages
RUN pip install -r requirements.txt
RUN yum install -y mesa-libGLw


RUN chmod a+rx /var/task/*.tflite

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]
