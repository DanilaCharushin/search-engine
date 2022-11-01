FROM centos:7

ARG PYTHON_VERSION=3.8.15
ARG PYTHON_PATH=Python-$PYTHON_VERSION

RUN yum update -y \
  && yum install gcc openssl-devel bzip2-devel libffi-devel sqlite-devel epel-release make -y \
  && curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/$PYTHON_PATH.tgz \
  && tar -xzf $PYTHON_PATH.tgz \
  && rm $PYTHON_PATH.tgz \
  && cd $PYTHON_PATH \
  && ./configure --enable-loadable-sqlite-extensions --enable-optimizations \
  && make install \
  && cd .. \
  && rm -Rf $PYTHON_PATH \
  && rm -f $PYTHON_PATH.tgz \
  && yum clean all

COPY backend/requirements/ /backend/requirements/

RUN python3 -m venv /app \
    && source /app/bin/activate \
    && cd /backend \
    && pip install -r requirements/requirements.lock.txt \
    && pip install -r requirements/requirements.dev.txt

COPY backend/ /backend/

EXPOSE 8000 9191

CMD bash
