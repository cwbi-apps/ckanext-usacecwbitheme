FROM ckan/ckan-dev:2.11.4

# Install any extensions needed by your CKAN instance
# - Make sure to add the plugins to CKAN__PLUGINS in the .env file
# - Also make sure all provide all extra configuration options, either by:
#   * Adding them to the .env file (check the ckanext-envvars syntax for env vars), or
#   * Adding extra configuration scripts to /docker-entrypoint.d folder) to update
#      the CKAN config file (ckan.ini) with the `ckan config-tool` command
#
# See README > Extending the base images for more details
#
USER root
# For instance:
#
### XLoader ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-xloader.git@master#egg=ckanext-xloader' && \ 
   pip3 install -r ${APP_DIR}/src/ckanext-xloader/requirements.txt && \
   pip3 install -U requests[security]

### Harvester ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@master#egg=ckanext-harvest' && \
   pip3 install -r ${APP_DIR}/src/ckanext-harvest/requirements.txt
# will also require gather_consumer and fetch_consumer processes running (please see https://github.com/ckan/ckanext-harvest)

### GeoView Spatial ###
RUN apt-get update -y && apt-get install -y python-dev-is-python3 libxml2-dev libxslt1-dev libgeos-c1v5

RUN pip3 install -e "git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial" && \
    pip3 install -r ${APP_DIR}/src/ckanext-spatial/requirements.txt && \
    pip3 install ckanext-geoview 

### Pages ###
#RUN  pip3 install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages

## DCAT ###
RUN pip3 install ckanext-dcat && \
    pip3 install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming"

## DCAT ###
RUN pip3 install ckanext-datajson ckanext-usmetadata ckanext-dcat-usmetadata
# Clone the extension(s) your are writing for your own project in the `src` folder
# to get them mounted in this image at runtime

## Really should put all the above in a requirements.txt file and just do a pip install -r requirements.txt, but this is just an example
COPY requirements.txt ${APP_DIR}
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --ignore-installed

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
