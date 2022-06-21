# Dockerfile
# 0.11.1 is latest stable release at the time of this writing
FROM jupyterhub/k8s-hub:1.1.3-n616.he76e1e57

COPY ./flask /usr/src/flask
RUN python3 -m pip install -r /usr/src/flask/requirements.txt
