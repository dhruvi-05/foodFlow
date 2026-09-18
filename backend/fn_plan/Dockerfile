FROM public.ecr.aws/lambda/python:3.12

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t "${LAMBDA_TASK_ROOT}"

# Copy handler code and model booster artifact
COPY app.py forecast.py recommend.py ingredients.py model.txt "${LAMBDA_TASK_ROOT}"/
COPY common/ "${LAMBDA_TASK_ROOT}"/common/

# Set Lambda handler entrypoint
CMD ["app.plan_handler"]
